from modding.common import logging

_LOGGER = logging.Logger()


class LoggingException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        _LOGGER.exception(message)


class LoggingErrorException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        _LOGGER.error(message)
