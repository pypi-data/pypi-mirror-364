"""Logger Class"""
import os
import colorlog
# custom imports
from data_analytics_core.metaclasses.singleton import SingletonMetaClass


class DataAnalyticsLogger(metaclass=SingletonMetaClass):
    """
    Logger designed to work in any environment (Local, Localstack & AWS) and logging level.
    Includes singleton Python metaclass system and 4  different levels of messaging, with different colors
    (using colorlog package) to output the messages.
    Levels determined by logging as integers (as in their library):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    """
    def __init__(self, project=None, tech_component=None, level: int = colorlog.INFO):
        self.project = project
        self.tech_component = tech_component
        self.code = None
        self.logger = self._logger_config()
        self.logger.setLevel(level)

    def error(self, message: str, code: str = None):
        output = self.output(logger_type="Error", message=message, code=code)
        self.logger.error(output)

    def warning(self, message: str, code: str = None):
        output = self.output(logger_type="Warning", message=message, code=code)
        self.logger.warning(output)

    def debug(self, message: str, code: str = None):
        output = self.output(logger_type="Debug", message=message, code=code)
        self.logger.debug(output)

    def info(self, message: str, code: str = None):
        output = self.output(logger_type="Info", message=message, code=code)
        self.logger.info(output)

    def output(self, logger_type: str, message: str, code: str):
        """Message with code and value."""
        output = f"{logger_type} in {self.project}:{self.tech_component};"
        if code:
            output = output + f"{self.new_line()}{logger_type} code: {code};"
        return output + f"{self.new_line()}Message: {message}"

    @staticmethod
    def _logger_config():
        # define handler constraints and format
        handler = colorlog.StreamHandler()
        if "AWS_EXECUTION_ENV" not in os.environ:
            handler.setFormatter(
                fmt=colorlog.ColoredFormatter(
                    "%(log_color)s[%(levelname)s %(asctime)s] %(yellow)s- %(green)s%(message)s",
                    datefmt=None,
                    reset=True,
                    log_colors={
                        "DEBUG": "green",
                        "INFO": "blue",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "white",
                    },
                    secondary_log_colors={},
                    style="%",
                )
            )
        logger = colorlog.getLogger(__name__)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def new_line():
        """
        This function returns the needed new line type for each environment
        """
        return "\n" if "LOCALSTACK_ENDPOINT_URL" in os.environ else "\r"

    def file_key_and_provider_message_addition(self, file_key: str, provider_name: str) -> str:
        """
        Simple formatter function, for partitioned environments or file storage systems (like S3).
        Fits with the structure (provider_name/partition+filename_key|filename_key).
        """
        message = f"{self.new_line()}"\
                  f"{file_key}{self.new_line()}"\
                  f"From provider:{self.new_line()}"\
                  f"{provider_name}{self.new_line()}"
        return message


da_logger = DataAnalyticsLogger()
