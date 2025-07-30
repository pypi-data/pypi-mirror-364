import sys
import traceback
from typing import Optional, Union

from .constant import *


def error(message: str) -> None:
    error_str = (
        text_colors["error"]
        + text_colors["bold"]
        + "ERROR  "
        + text_colors["end_color"]
    )

    if sys.exc_info()[0] is None:
        traceback.print_stack()
    else:
        traceback.print_exc()
    sys.exit("{} - {}. Exiting!!!".format(error_str, message))


def color_text(in_text: str) -> str:
    return text_colors["light_red"] + in_text + text_colors["end_color"]


def log(message: str, end="\n") -> None:
    log_str = (
        text_colors["logs"] + text_colors["bold"] + "LOGS   " + text_colors["end_color"]
    )
    print("{} - {}".format(log_str, message), end=end)


def warning(message: Union[str, Warning]) -> None:
    if isinstance(message, Warning):
        message = f"{type(message).__name__}({','.join(map(repr, message.args))}"

    warn_str = (
        text_colors["warning"]
        + text_colors["bold"]
        + "WARNING"
        + text_colors["end_color"]
    )
    print("{} - {}".format(warn_str, message))


def ignore_exception_with_warning(message: str) -> None:
    """
    After catching a tolerable exception E1 (e.g. when Model.forward() fails during
    profiling with try-catch, it'll be helpful to log the exception for future
    investigation. But printing the error stack trace, as is, could be confusing
    when an uncaught (non-tolerable) exception "E2" raises down the road. Then, the log
    will contain two stack traces for E1, E2. When looking for errors in logs, users
    should look for E2, but they may find E1.

    This function appends "(WARNING)" at the end of all lines of the E1 traceback, so
    that the user can distinguish E1 from uncaught exception E2.

    Args:
        message: Extra explanation and context for debugging. (Note: the exception obj
    will be automatically fetched from python. No need to pass it as an argument or as
    message)
    """
    warning(f"{message}:\n{traceback.format_exc()}".replace("\n", "\n(WARNING)"))


def info(message: str, print_line: Optional[bool] = False) -> None:
    info_str = (
        text_colors["info"] + text_colors["bold"] + "INFO   " + text_colors["end_color"]
    )
    print("{} - {}".format(info_str, message))
    if print_line:
        double_line(dashes=150)


def debug(message: str) -> None:
    log_str = (
        text_colors["debug"]
        + text_colors["bold"]
        + "DEBUG   "
        + text_colors["end_color"]
    )
    print("{} - {}".format(log_str, message))


def double_line(dashes: Optional[int] = 75) -> None:
    print(text_colors["error"] + "=" * dashes + text_colors["end_color"])


def singe_line(dashes: Optional[int] = 67) -> None:
    print("-" * dashes)


def log_header_double_line(header: str) -> None:
    double_line()
    print(
        text_colors["info"]
        + text_colors["bold"]
        + "=" * 50
        + str(header)
        + text_colors["end_color"]
    )
    double_line()


def log_header_single_line(header: str) -> None:
    singe_line()
    print(
        text_colors["info"]
        + text_colors["bold"]
        + "=" * 50
        + str(header)
        + text_colors["end_color"]
    )
    singe_line()


def log_header(header: str) -> None:
    print(
        text_colors["warning"]
        + text_colors["bold"]
        + "=" * 25
        + str(header)
        + text_colors["end_color"]
    )



