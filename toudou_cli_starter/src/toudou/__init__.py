import os
import logging
import sys

config = dict(
DATABASE_URL=os.getenv("TOUDOU_DATABASE_URL", ""),
DEBUG=os.getenv("TOUDOU_DEBUG", "False") == "True",
)
logging.basicConfig(
level=logging.INFO,
format="%(asctime)s [%(levelname)s] %(message)s",
handlers=[
logging.FileHandler("toudou.log"),
logging.StreamHandler(stream=sys.stdout)
]
)
