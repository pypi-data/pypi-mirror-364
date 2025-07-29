"""
Provides a static, Android Logcat-style logging interface.

This module offers a simple, zero-configuration facade over Python's standard
logging module, designed to be instantly familiar to Android developers.
"""
import sys
import logging
from contextlib import contextmanager

from logcatter.formatter import LogFormatter
from logcatter.logcat import Logcat
from logcatter.level import LEVEL_VERBOSE, LEVEL_DEBUG, LEVEL_INFO, LEVEL_WARNING, LEVEL_ERROR, LEVEL_FATAL


class Log:
    """
    A static utility class that provides an Android Logcat-like logging interface.

    This class is not meant to be instantiated. It offers a set of static methods
    (e.g., `d`, `i`, `w`, `e`) that wrap the standard Python `logging` module
    to provide a simple, zero-configuration logging experience. It automatically
    configures a logger that outputs messages in a format similar to Android's
    Logcat, including automatic tagging with the calling filename.
    """

    VERBOSE = LEVEL_VERBOSE
    DEBUG = LEVEL_DEBUG
    INFO = LEVEL_INFO
    WARNING = LEVEL_WARNING
    ERROR = LEVEL_ERROR
    FATAL = LEVEL_FATAL

    class _PrintLogger:
        """
        An internal file-like object that redirects writes to the Log utility.
        It buffers text until a newline is received, then logs the complete line.
        """

        def __init__(
                self,
                level: int,
                *args,
                **kwargs,
        ):
            self.level = level
            self.args = args
            self.kwargs = kwargs
            self._buffer = ""
            self.stacklevel = 3

        def write(self, text: str):
            """
            Receives text from a print call, buffers it, and logs complete lines.
            """
            if not text:
                return

            self._buffer += text
            if '\n' in self._buffer:
                lines = self._buffer.split('\n')
                self._buffer = lines.pop()
                for line in lines:
                    if line:
                        Log._log(
                            self.level,
                            line,
                            *self.args,
                            stacklevel=self.stacklevel,
                            **self.kwargs,
                        )

        def flush(self):
            """
            Logs any remaining text in the buffer. Called when the context exits.
            """
            if self._buffer:
                Log._log(
                    self.level,
                    self._buffer,
                    *self.args,
                    stacklevel=self.stacklevel,
                    **self.kwargs,
                )
                self._buffer = ""

    @staticmethod
    def getLogger() -> logging.Logger:
        """
        Retrieves the singleton logger instance for the application.

        On the first call, it initializes the logger with a `StreamHandler` and
        the custom `LogFormatter`. Subsequent calls return the same logger instance
        without adding more handlers, preventing duplicate log messages.

        Returns:
            logging.Logger: The configured logger instance.
        """
        logger = logging.getLogger(Logcat.NAME)
        # Init if not initiated
        if not logger.hasHandlers():
            logging.addLevelName(Log.VERBOSE, "VERBOSE")
            logging.addLevelName(Log.FATAL, "FATAL")
            logger.setLevel(Log.VERBOSE)
            handler = logging.StreamHandler()
            handler.setFormatter(LogFormatter())
            logger.addHandler(handler)
        return logger

    @staticmethod
    def setLevel(level: int | str):
        """
        Sets the logging level for the application's logger.

        Messages with a severity lower than `level` will be ignored.

        Args:
            level (int | str): The minimum level of severity to log.
                Can be an integer constant (e.g., `logging.INFO`) or its string
                representation (e.g., "INFO").
        """
        Log.getLogger().setLevel(level)

    @staticmethod
    def save(filename: str, mode="w"):
        """
        Saves the log to a file.
        :param filename: Path of the file to save to.
        :param mode: Mode to open the file with. Default is 'w'.
        """
        handler = logging.FileHandler(filename, mode=mode)
        handler.setFormatter(LogFormatter(ignore_color=True))
        Log.getLogger().addHandler(handler)

    @staticmethod
    def is_verbose():
        """
        Checks the logging level is `Log.VERBOSE` or below.
        :return:
            bool: `True` when the level is `Log.VERBOSE` or below, `False` otherwise.
        """
        return Log.getLogger().level <= Log.VERBOSE

    @staticmethod
    def is_quiet():
        """
        Checks the logging level is `Log.WARNING` or above.
        :return:
            bool: `True` when the level is `Log.WARNING` or above, `False` otherwise.
        """
        return Log.getLogger().level >= Log.WARNING

    @staticmethod
    def is_silent():
        """
        Checks the logging level is greater than `Log.FATAL`.
        :return:
            bool: `True` when the level is greater than `Log.FATAL`, `False` otherwise.
        """
        return Log.getLogger().level > Log.FATAL

    @staticmethod
    def _log(
            level: int,
            msg: str,
            *args,
            stacklevel: int = 3,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the given level.

        Args:
            :param level: Level of the message.
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        messages = msg.split('\n')
        for index, message in enumerate(messages):
            Log.getLogger().log(
                level,
                message,
                *args,
                stacklevel=stacklevel,
                exc_info=e if index == len(messages)-1 else None,
                stack_info=s if index == len(messages)-1 else False,
                **kwargs,
            )

    @staticmethod
    @contextmanager
    def print_log(
            level: int = VERBOSE,
            show_stack: bool = False,
            print_error: bool = False,
            error_level: int = ERROR,
            show_error_stack: bool = True,
    ):
        """
        Log `print` message with the given level in context

        Args:
            :param level: Level of the message.
            :param error_level: Level of the error message.
            :param print_error: Whether print the error or not.
            :param show_stack: Whether show the stacktrace or not for the message.
            :param show_error_stack: Whether show the stacktrace or not for the error.
        """
        # Print
        original_stdout = sys.stdout
        buffer_out = Log._PrintLogger(level, s=show_stack)
        sys.stdout = buffer_out
        # Error
        if print_error:
            original_stderr = sys.stderr
            buffer_err = Log._PrintLogger(error_level, s=show_error_stack)
            sys.stderr = buffer_err

        try:
            yield
        finally:
            buffer_out.flush()
            sys.stdout = original_stdout
            if print_error:
                buffer_err.flush()
                sys.stderr = original_stderr

    @staticmethod
    def v(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the VERBOSE level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.VERBOSE,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def d(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the DEBUG level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.DEBUG,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def i(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the INFO level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.INFO,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def w(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the WARNING level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.WARNING,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def e(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the ERROR level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.ERROR,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def f(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the CRITICAL level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.FATAL,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )
