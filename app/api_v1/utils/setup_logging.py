import logging
import logging.config
from logging import Logger
import os
import yaml
from pathlib import Path


def setup_logging(
    default_path="logging_config.yaml", default_level=logging.INFO, env_key="LOG_CFG"
) -> Logger:
    """Настройка логирования из YAML файла"""
    path = os.getenv(env_key, default_path)
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f)

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    return logging.getLogger("my_app")
