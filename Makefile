# Поднять контейнеры (в фоне)
up:
	docker compose up -d

# Остановить контейнеры
down:
	docker compose down

# Пересобрать образы и запустить
rebuild:
	docker compose down
	docker compose build
	docker compose up -d

winlogapp:
	@if "$(t)"=="1" ( \
		docker compose logs -f app \
	) else ( \
		docker compose logs app \
	)

logapp:
	@if [ "$(t)" = "1" ]; then \
		docker compose logs -f app; \
	else \
		docker compose logs app; \
	fi

logworker:
	docker compose logs celery_worker

dropdb:
	docker compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS mai_students;"

createdb:
	docker compose exec postgres psql -U postgres -c "CREATE DATABASE mai_students;"

setadmin:
	docker compose exec postgres psql -U postgres -d mai_students -c "UPDATE users SET is_superuser = true WHERE id = 1;"

recreatedb: dropdb createdb


fullmigrate: makemigration migrate

# Выполнить миграции
migrate:
	docker compose run --rm app alembic upgrade head

# Создать миграцию
makemigration:
	docker compose run --rm app alembic revision --autogenerate -m "$(name)"


# Очистить volume'ы и образы
prune:
	docker system prune -af --volumes
