#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import logging.config
import os
import sys
import json

from loguru import logger

class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id='app')
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level,record.getMessage())

class CrwlLogger:
    """Класс журнала.
    Для настройки используются 4 переменных окружения:

    **LOG_LEVEL** - уровень журналирования
    (CRITICAL, ERROR, WARNING, INFO, DEBUG);

    **LOG_FILE_NAME** - имя файла журнала;

    **LOG_RETENTION**

    **LOG_ROTATION**

    Журнал создаётся функцией ``make_logger``.
    """

    @classmethod
    def make_logger(
        cls,
        level: str = "CRITICAL",
        file_name: str = "crawly.log",
        retention: str = "1 months",
        rotation: str = "20 days"
    ):
        """Функция создаёт новый журнал.

        Returns:
            Настроенный экземпляр журнала.
        """
        if level == "DEBUG":
            fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level> : {name}.{function}.{line} :: <level>{message}</level>"
        else:
            fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level> :: <level>{message}</level>"

        return cls.customize_logging(
            file_name,
            level=level,
            retention=retention,
            rotation=rotation,
            format=fmt
        )

    @classmethod
    def customize_logging(cls, filepath: str, level: str, rotation: str, retention: str, format: str):

        logger.remove()
        logger.add(
            sys.stdout,
            enqueue=True,
            colorize=True,
            backtrace=True,
            level=level.upper(),
            format=format
        )
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format
        )
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ['uvicorn',
                     'uvicorn.error',
                     'fastapi'
                     ]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)


    @classmethod
    def load_logging_config(cls, config_path):
        config = None
        with open(config_path, encoding='utf-8') as config_file:
            config = json.load(config_file)
        return config
