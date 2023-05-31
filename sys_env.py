# -*- coding: utf-8 -*-

import os


class SysEnv:

    APPNAME = 'APPNAME'
    APPROOT = 'APPROOT'
    # console
    LOGGER_ENABLE_CONSOLE = "LOGGER_ENABLE_CONSOLE"
    # SYSLOG
    LOGGER_ENABLE_SYSLOG = "LOGGER_ENABLE_SYSLOG"
    LOGGER_SYSLOG_HOST = "LOGGER_SYSLOG_HOST"
    LOGGER_SYSLOG_PORT = "LOGGER_SYSLOG_PORT"
    LOGGER_SYSLOG_FACILITY = "LOGGER_SYSLOG_FACILITY"
    LOGGER_LEVEL = "LOGGER_LEVEL"
    # 项目运行环境
    RUNTIME_ENVIRONMENT = "RUNTIME_ENVIRONMENT"
    # 项目的域名
    DOMAIN = "DOMAIN"

    @staticmethod
    def get(key: str, default=None) -> str:
        key = key.upper()
        if key not in os.environ:
            return default
        value = os.environ[key]
        if value.upper() == "TRUE":
            return True
        if value.upper() == "FALSE":
            return False
        return value

    @staticmethod
    def set(key: str, value: str) -> None:
        key = key.upper()
        os.environ[key] = value
