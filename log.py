#!/usr/bin/env python3
# -*-encoding: utf-8-*-

import logging
import logging.handlers

import sys
import os


def get_logger(filepath: str = '', max_num: int = 0, level: int = logging.INFO, name = 'DefaultLogger',
               to_console = True, to_file = True):
    """
    :param filepath: set filepath to '' to disable file output
    :param max_num: If backupCount is > 0, when rollover is done, no more than backupCount files are kept - the oldest
                    ones are deleted.
    :param level: logging level
    :rtype logger: logging.Logger
    :return: the logger
    """

    # LOG_FORMAT = "%(asctime)s - %(levelname)s <%(filename)s> [%(funcName)s]: %(message)s"
    # DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    # logger = logging.getLogger('DefaultLogger')
    # logger.setLevel(logging.DEBUG)
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    # logger.addHandler(console_handler)
    # file_handler = RotatingFileHandler('default.log', maxBytes = 1024 * 1024, backupCount = 10)
    # file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    # logger.addHandler(file_handler)
    
    LOG_FORMAT = "%(asctime)s - %(levelname)s <%(filename)s> [%(funcName)s]: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    logger = logging.getLogger(name)

    logger.setLevel(level)

    if to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    if to_file:
        file_handler = logging.handlers.RotatingFileHandler(os.path.join(filepath, name + '.log'),
                                                            maxBytes = 1024 * 1024, backupCount = max_num)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    return logger


if __name__ == '__main__':
    get_logger()
