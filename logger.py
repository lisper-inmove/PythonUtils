# -*- coding: utf-8 -*-

"""日志处理模块."""

import logging
import traceback
from logging.handlers import SysLogHandler

from .sys_env import SysEnv
from .color_printer import ColorPrinter


class Logger(logging.Logger):

    def __init__(self):
        """日志处理类初始化函数."""
        name = SysEnv.get(SysEnv.APPNAME)
        if name is None:
            name = "Default"
        self.name = name
        super().__init__(self.name)
        _formatter = f'{self.name}: %(asctime)s - %(levelname)s - %(message)s'
        self._formatter = logging.Formatter(_formatter)
        self.__set_level()
        self.__init_syslog_handler()
        self.__init_console_handler()

    def __set_message_uuid(self):
        try:
            from flask import request
            self._message_uuid = request.headers.get("Message-Uuid")
        except Exception:
            self._message_uuid = None

    def __wrap_message_with_uuid(self, message):
        self.__set_message_uuid()
        if self._message_uuid is None:
            return message
        result = f"{self._message_uuid} - {message}"
        return result

    def __name_to_level(self, name):
        return logging._nameToLevel[name]

    def debug(self, message):
        """记录debug日志."""
        message = self.__wrap_message_with_uuid(message)
        super().debug(message)

    def info(self, message):
        message = self.__wrap_message_with_uuid(message)
        super().info(message)

    def exception(self, message):
        """记录exception日志.

        python3.9
          super().exception底层调用的是 error 函数，默认会传exc_info参数过去，
          会出现如下错误
        TypeError: error() got an unexpected keyword argument 'exc_info'
        """
        # message = self.__wrap_message_with_uuid(message)
        # super().exception(message)

    def traceback(self, e, msg=None):
        if msg is not None:
            self.info(msg)
        color_value = ColorPrinter.red_value(f"=======>>> Traceback Info {str(e)} <<<========")
        self.info(color_value)
        self.info(traceback.print_tb(e.__traceback__))

    def error(self, message):
        """记录错误日志."""
        message = self.__wrap_message_with_uuid(message)
        super().error(message)

    def warning(self, message):
        """记录警告日志."""
        message = self.__wrap_message_with_uuid(message)
        super().warning(message)

    def fatal(self, message):
        """记录致命日志."""
        message = self.__wrap_message_with_uuid(message)
        super().fatal(message)

    def __init_syslog_handler(self):
        """设置syslog日志."""
        enable = SysEnv.get(SysEnv.LOGGER_ENABLE_SYSLOG)
        if enable is None:
            enable = False
        if not enable:
            return
        host = SysEnv.get(SysEnv.LOGGER_SYSLOG_HOST)
        port = int(SysEnv.get(SysEnv.LOGGER_SYSLOG_PORT))
        facility = SysEnv.get(SysEnv.LOGGER_SYSLOG_FACILITY)
        self.__create_syslog_handler(host, port, facility)

    def __create_syslog_handler(self, host, port, facility):
        handler = SysLogHandler(
            address=(host, port),
            facility=SysLogHandler.facility_names[facility],
            # socktype=socket.SOCK_STREAM # TCP
        )
        handler.setFormatter(self._formatter)
        handler.setLevel(self._level)
        self.addHandler(handler)

    def __init_console_handler(self):
        """设置终端日志."""
        enable = SysEnv.get(SysEnv.LOGGER_ENABLE_CONSOLE)
        if enable is None:
            enable = True
        if not enable:
            return
        handler = logging.StreamHandler()
        handler.setFormatter(self._formatter)
        self.addHandler(handler)

    def __set_level(self):
        level = SysEnv.get(SysEnv.LOGGER_LEVEL)
        _level = logging.INFO
        if level == 'INFO':
            _level = logging.INFO
        elif level == 'DEBUG':
            _level = logging.DEBUG
        if level == 'ERROR':
            _level = logging.ERROR
        if level == 'FATAL':
            _level = logging.FATAL
        self.setLevel(_level)
        self._level = _level


if __name__ == '__main__':
    SysEnv.set(SysEnv.LOGGER_ENABLE_CONSOLE, True)
    SysEnv.set(SysEnv.LOGGER_ENABLE_SYSLOG, True)
    SysEnv.set(SysEnv.LOGGER_SYSLOG_HOST, "logger.server")
    SysEnv.set(SysEnv.LOGGER_SYSLOG_PORT, 514)
    SysEnv.set(SysEnv.LOGGER_SYSLOG_FACILITY, "local7")

    import random
    logger = Logger()
    logger.info(f"test-{random.randint(1, 1000)}")
