import functools
import logging
import os

import click
from rich.logging import RichHandler
from rich.traceback import install

LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)
FORMAT = "%(message)s"


logging.basicConfig(
    level=LOG_LEVEL, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

# suppress info level messages and set level to warning
WARNING_LEVEL_MODULES = os.getenv(
    "LOG_LEVEL_WARNING_MODULES", "boto,boto3,botocore,mlflow"
).split(",")

for lib in WARNING_LEVEL_MODULES:
    lib_log = logging.getLogger(lib)
    lib_log.setLevel(logging.WARNING)


install(suppress=[click])


def log_function_call(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        log.debug(f"Calling function {fn.__name__}")
        result = fn(*args, **kwargs)
        log.debug(f"\t... finished {fn.__name__}")
        return result

    return wrapper
