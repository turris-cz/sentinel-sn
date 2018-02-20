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
