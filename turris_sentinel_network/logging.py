"""
This module provides standardized logging for whole sentinel network.

There are 2 preconfigured handlers:
  - syslog - INFO and higher severity
  - file under rotation - DEBUG and higher severity

Expected usage in your script:

```
import logging
import turris_sentinel_network
logger = logging.getLogger("component_name")
logger.info("I'm running!")
```

Your logger will inherit INFO level from root logger. This is kind a fail-safe
mechanism.  If you need to use DEBUG level, you must enable it explicitly:

```
import logging
import turris_sentinel_network
logger = logging.getLogger("component_name")
logger.setLevel(logging.DEBUG)
logger.debug("Still running...")
```

Please, do not change logging format for syslog handler. It will be parsed by
TM. File handler is prefixed by current time, for better debugging.

"""
import sys
import logging
import logging.handlers

formatter = logging.Formatter("sentinel: %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                              "%Y-%m-%d %H:%M:%S")
time_formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                                   "%Y-%m-%d %H:%M:%S")

syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
syslog_handler.setFormatter(formatter)
syslog_handler.setLevel(logging.INFO)

file_handler = logging.handlers.RotatingFileHandler("sentinel.log", maxBytes=10*1024*1024, backupCount=10)
file_handler.setFormatter(time_formatter)
file_handler.setLevel(logging.DEBUG)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(syslog_handler)
root_logger.addHandler(file_handler)


def log_uncaught(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    root_logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = log_uncaught
