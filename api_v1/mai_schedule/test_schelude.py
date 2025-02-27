import pytest
import fastapi
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from httpx import HTTPStatusError, TimeoutException, Request, Response, RequestError
import redis
from fastapi import HTTPException

# Импортируем ваш FastAPI app и зависимости
from backend.api_v1.shedule.utils import (
    app,
    get_redis_client,
    get_group_hash,
    fetch_schedule_from_mai,
)

# -------- Фикстуры (fixtures) --------


@pytest.fixture
def test_app():
    return TestClient(app)


@pytest.fixture
def mock_redis_client():
    class MockRedis:
        def __init__(self):
            self.cache = {}

        def get(self, key):
            if key in self.cache:
                return self.cache[key]
            return None

        def set(self, key, value, ex=None):
            self.cache[key] = value

        def close(self):
            pass

        def ping(self):
            return True

    return MockRedis()


@pytest.fixture
def override_dependencies(mock_redis_client):
    app.dependency_overrides[get_redis_client] = lambda: mock_redis_client
    yield
    app.dependency_overrides = {}  # Сброс


# -------- Тесты --------


def test_get_group_hash():
    group_name = "М8О-101БВ-24"
    expected_hash = "4030e433ea6903fb6df03cfd47ef3885.json"
    assert get_group_hash(group_name) == expected_hash


@pytest.mark.asyncio
async def test_fetch_schedule_from_mai_success():
    """
    Проверяет УСПЕШНОЕ получение расписания.
    """
    group_hash = "some_hash.json"
    mock_response_data = {"schedule": "data"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # ПРАВИЛЬНАЯ настройка:
        mock_response = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value=mock_response_data),  # Вот как надо!
            history=[],
        )
        mock_get.return_value = mock_response

        result = await fetch_schedule_from_mai(group_hash)
        assert result == mock_response_data

        mock_get.assert_called_once_with(
            f"https://public.mai.ru/schedule/data/{group_hash}",
            headers=mock_get.call_args.kwargs["headers"],
            timeout=20,
        )


@pytest.mark.asyncio
async def test_fetch_schedule_from_mai_http_error():
    """
    Проверяет обработку HTTP-ошибок (404 Not Found).
    """
    group_hash = "some_hash.json"
    mock_response_text = "Schedule not found"  # Текст ошибки
    mock_response = AsyncMock(status_code=404, text=mock_response_text, history=[])

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = HTTPStatusError(
            "Not Found", request=Request("GET", "url"), response=mock_response
        )
        with pytest.raises(fastapi.exceptions.HTTPException) as exc_info:
            await fetch_schedule_from_mai(group_hash)

        assert exc_info.value.status_code == 404
        assert mock_response_text in exc_info.value.detail  # Проверяем detail!


@pytest.mark.asyncio
async def test_fetch_schedule_from_mai_timeout_error():
    """
    Проверяет обработку таймаута.
    """
    group_hash = "some_hash.json"
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = TimeoutException("Request timed out")
        with pytest.raises(fastapi.exceptions.HTTPException) as exc_info:
            await fetch_schedule_from_mai(group_hash)
        assert exc_info.value.status_code == 500
        assert "Request timed out" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_fetch_schedule_from_mai_json_decode_error():
    """
    Проверяет обработку ошибки декодирования JSON.
    """
    group_hash = "some_hash.json"
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200, text="invalid json", history=[]
        )
        # side_effect ДЛЯ САМОГО json()!
        mock_get.return_value.json.side_effect = json.JSONDecodeError("Error", "doc", 0)

        with pytest.raises(fastapi.exceptions.HTTPException) as exc_info:
            await fetch_schedule_from_mai(group_hash)
        assert exc_info.value.status_code == 500
        assert "Некорректный JSON ответ" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_fetch_schedule_from_mai_request_error():
    """
    Проверяет обработку общей ошибки запроса (RequestError).
    """
    group_hash = "some_hash.json"
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = RequestError("Some network error")
        with pytest.raises(fastapi.exceptions.HTTPException) as exc_info:
            await fetch_schedule_from_mai(group_hash)
        assert exc_info.value.status_code == 500
        assert "Ошибка запроса" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_fetch_schedule_from_mai_unexpected_error():
    """
    Проверяет обработку непредвиденной ошибки в fetch_schedule_from_mai.
    """
    group_hash = "some_hash.json"
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Some unexpected error")
        with pytest.raises(fastapi.exceptions.HTTPException) as exc_info:
            await fetch_schedule_from_mai(group_hash)

        assert exc_info.value.status_code == 500
        assert "Непредвиденная ошибка" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_schedule_cache_hit(
    test_app, mock_redis_client, override_dependencies
):
    group_name = "М8О-101БВ-24"
    group_hash = get_group_hash(group_name)
    cache_key = f"schedule:{group_hash}"
    mock_schedule = {"schedule": "data from cache"}
    mock_redis_client.set(cache_key, json.dumps(mock_schedule))

    with patch(
        "schelude.fetch_schedule_from_mai"
    ) as mock_fetch:  # Мокаем fetch_schedule_from_mai
        response = test_app.get(f"/schedule/{group_name}")
        assert response.status_code == 200
        assert response.json() == mock_schedule
        mock_fetch.assert_not_called()  # fetch_schedule_from_mai НЕ должен вызываться


@pytest.mark.asyncio
async def test_get_schedule_cache_miss(
    test_app, mock_redis_client, override_dependencies
):
    group_name = "М8О-101БВ-24"
    group_hash = get_group_hash(group_name)
    cache_key = f"schedule:{group_hash}"
    mock_schedule = {"schedule": "data from MAI"}

    with patch(
        "schelude.fetch_schedule_from_mai", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = mock_schedule  # AsyncMock УЖЕ возвращает корутину

        response = test_app.get(f"/schedule/{group_name}")
        assert response.status_code == 200
        assert response.json() == mock_schedule
        assert mock_redis_client.get(cache_key) == json.dumps(
            mock_schedule
        )  # Проверка сохранения
        mock_fetch.assert_called_once_with(group_hash)


@pytest.mark.asyncio
async def test_get_schedule_empty_response(
    test_app, mock_redis_client, override_dependencies
):
    group_name = "М8О-101БВ-24"
    with patch(
        "schelude.fetch_schedule_from_mai", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = {}

        response = test_app.get(f"/schedule/{group_name}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Schedule not found"}
        mock_fetch.assert_called_once_with(get_group_hash(group_name))


@pytest.mark.asyncio
async def test_get_schedule_fetch_error(
    test_app, mock_redis_client, override_dependencies
):
    group_name = "М8О-101БВ-24"

    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = "Some server error detail"

    with patch(
        "schelude.fetch_schedule_from_mai", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.side_effect = HTTPStatusError(
            "Server Error", request=Request("GET", "url"), response=mock_response
        )
        with pytest.raises(HTTPException) as exc_info:
            await test_app.get(f"/schedule/{group_name}")
        assert exc_info.value.status_code == 500
        assert "Server Error" in str(exc_info.value.detail)
        mock_fetch.assert_called_once_with(get_group_hash(group_name))


@pytest.mark.asyncio
async def test_get_schedule_redis_set_error(
    test_app, mock_redis_client, override_dependencies
):
    """
    Тест на ошибку при СОХРАНЕНИИ в Redis.
    """
    group_name = "М8О-101БВ-24"
    mock_schedule = {"schedule": "data from MAI"}

    with (
        patch("schelude.fetch_schedule_from_mai", new_callable=AsyncMock) as mock_fetch,
        patch.object(
            mock_redis_client,
            "set",
            side_effect=redis.exceptions.ConnectionError("Redis error"),
        ),
    ):
        mock_fetch.return_value = mock_schedule
        response = test_app.get(f"/schedule/{group_name}")

        assert (
            response.status_code == 200
        )  # Должен вернуться успешный ответ, несмотря на ошибку Redis
        assert response.json() == mock_schedule
        mock_fetch.assert_called_once_with(get_group_hash(group_name))


@pytest.mark.asyncio
async def test_get_schedule_redis_get_error(
    test_app, mock_redis_client, override_dependencies
):
    """
    Тест на ошибку при ЧТЕНИИ из Redis.
    """
    group_name = "М8О-101БВ-24"
    mock_schedule = {"schedule": "data from MAI"}

    with (
        patch("schelude.fetch_schedule_from_mai", new_callable=AsyncMock) as mock_fetch,
        patch.object(
            mock_redis_client,
            "get",
            side_effect=redis.exceptions.ConnectionError("Redis error"),
        ),
    ):
        mock_fetch.return_value = (
            mock_schedule  # fetch_schedule_from_mai возвращает данные
        )
        response = test_app.get(f"/schedule/{group_name}")

        assert (
            response.status_code == 200
        )  # Все равно должен быть 200, т.к. fetch_schedule_from_mai отработал
        assert response.json() == mock_schedule
        mock_fetch.assert_called_once_with(
            get_group_hash(group_name)
        )  # fetch_schedule_from_mai должен быть вызван
