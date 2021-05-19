
# -*- coding: UTF-8 -*-
# vim:fenc=utf-8


"""
log module, need a ./log directory
"""

import logging.config

config = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s-%(thread)d-%(filename)s[line:%(lineno)d]%(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'encoding': 'utf-8',
            'filemode': 'a'
        }
        # other formater
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': './log/' + __name__ + '.log',
            'level': 'DEBUG',
            'formatter': 'simple',
            'when': 'h',
            'interval': 1
        }
        # other handler
    },
    'loggers': {
        'StreamLogger': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'FileLogger': {
            # have console and file
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
        # other logger
    }
}

logging.config.dictConfig(config)
StreamLogger = logging.getLogger("StreamLogger")
FileLogger = logging.getLogger("FileLogger")
