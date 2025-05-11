#!/bin/bash
set -e

# Проверяем, есть ли отличия между моделями и текущей БД
if alembic revision --autogenerate -m "auto" --head; then
    # Если есть изменения - применяем миграцию
    alembic upgrade head
fi

# Запускаем основной процесс
exec "$@"