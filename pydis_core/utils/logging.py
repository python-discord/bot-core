"""Common logging related functions."""

import logging
import typing

if typing.TYPE_CHECKING:
    LoggerClass = logging.Logger
else:
    LoggerClass = logging.getLoggerClass()

TRACE_LEVEL = 5


class CustomLogger(LoggerClass):
    """Custom implementation of the :obj:`logging.Logger` class with an added :obj:`trace` method."""

    def trace(self, msg: str, *args, **kwargs) -> None:
        """
        Log the given message with the severity ``"TRACE"``.

        To pass exception information, use the keyword argument exc_info with a true value:

        .. code-block:: py

            logger.trace("Houston, we have an %s", "interesting problem", exc_info=1)

        Args:
            msg: The message to be logged.
            args, kwargs: Passed to the base log function as is.
        """
        if self.isEnabledFor(TRACE_LEVEL):
            self.log(TRACE_LEVEL, msg, *args, **kwargs)


def get_logger(name: typing.Optional[str] = None) -> CustomLogger:
    """
    Utility to make mypy recognise that logger is of type :obj:`CustomLogger`.

    Args:
        name: The name given to the logger.

    Returns:
        An instance of the :obj:`CustomLogger` class.
    """
    return typing.cast(CustomLogger, logging.getLogger(name))


# Setup trace level logging so that we can use it within pydis_core.
logging.TRACE = TRACE_LEVEL
logging.setLoggerClass(CustomLogger)
logging.addLevelName(TRACE_LEVEL, "TRACE")
