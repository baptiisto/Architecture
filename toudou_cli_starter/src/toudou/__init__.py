import os
import logging
import sys

# Chargement des variables d'environnement à partir du fichier dev.env
from dotenv import load_dotenv

load_dotenv("dev.env")

# Configuration de l'application en utilisant les variables d'environnement
config = {
    "DATABASE_URL": os.getenv("TOUDOU_DATABASE_URL"),
    "DEBUG": os.getenv("TOUDOU_DEBUG", "False").lower() == "true",
    "SECRET_KEY": os.getenv("TOUDOU_FLASK_SECRET_KEY", "default_secret_key")
}

# Configuration du journal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("toudou.log"),
        logging.StreamHandler(stream=sys.stdout)
    ]
)
FORMAT = '%Y-%m-%d'

