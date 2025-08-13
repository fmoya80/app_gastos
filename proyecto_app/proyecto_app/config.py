# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # carpeta mi_app/
DATA_DIR = os.path.join(BASE_DIR, "data")

GASTOS_FILE = os.path.join(DATA_DIR, "gastos.csv")
CATS_FILE   = os.path.join(DATA_DIR, "categorias.csv")

DEFAULT_CATEGORIES = ["Comida", "Transporte", "Ocio", "Otros"]
CURRENCY_SYMBOL = "$"
THOUSAND_SEPARATOR = "."
