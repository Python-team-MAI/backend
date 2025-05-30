import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Кастомный JSON форматтер для логов"""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Добавляем timestamp в ISO формате
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat() + "Z"

        # Добавляем уровень лога
        log_record["level"] = record.levelname

        # Добавляем имя логгера
        log_record["logger"] = record.name

        # Добавляем информацию о файле и строке
        log_record["file"] = f"{record.filename}:{record.lineno}"

        # Добавляем имя функции
        log_record["function"] = record.funcName

        # Переименовываем message в msg для краткости
        if "message" in log_record:
            log_record["msg"] = log_record.pop("message")


def setup_logging(name: str) -> logging.Logger:
    """
    Настройка логирования для отправки в Loki

    Args:
        name: Имя логгера

    Returns:
        Настроенный логгер
    """

    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Убираем существующие обработчики
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Создаем обработчик для stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Устанавливаем JSON форматтер
    formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(logger)s %(msg)s %(file)s %(function)s",
        json_ensure_ascii=False,
    )
    handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(handler)

    # Отключаем распространение логов вверх по иерархии
    logger.propagate = False

    return logger
