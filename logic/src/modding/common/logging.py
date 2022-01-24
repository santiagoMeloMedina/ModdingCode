import datetime


class Logger:

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    EXCEPTION = "EXCEPTION"

    @property
    def __now(self) -> str:
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def info(self, message: str) -> None:
        print("%s | %s | %s" % (self.__now, self.INFO, message))

    def warning(self, message: str) -> None:
        print("%s | %s | %s" % (self.__now, self.WARNING, message))

    def error(self, message: str) -> None:
        print("%s | %s | %s" % (self.__now, self.ERROR, message))

    def exception(self, message: str) -> None:
        print("%s | %s | %s" % (self.__now, self.EXCEPTION, message))
