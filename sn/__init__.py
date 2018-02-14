from sn.exceptions import *
from sn.messages import *
from sn.argparser import *
from sn.network import *

import logging
import logging.handlers

logging.basicConfig(
    level=logging.INFO,
    format="sentinel: %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("sentinel.log", encoding="UTF-8"),
        logging.handlers.SysLogHandler(address="/dev/log"),
    ],
)
