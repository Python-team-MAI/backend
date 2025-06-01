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
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # JSON handler (stdout → Promtail/Loki)
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setLevel(logging.INFO)
    json_formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(logger)s %(msg)s %(file)s %(function)s",
        json_ensure_ascii=False,
    )
    json_handler.setFormatter(json_formatter)

    # Console handler (читаемый формат)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s (%(filename)s:%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)

    logger.addHandler(json_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger

