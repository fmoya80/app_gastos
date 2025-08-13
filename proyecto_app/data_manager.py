# data_manager.py
import os
import uuid
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe


# ========= Config =========
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Ruta local por defecto (para tu .bat / entorno local)
CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credenciales.json")

# Usa SIEMPRE la URL (más robusto que por nombre)
SPREADSHEET_URL = os.getenv(
    "SHEETS_URL",
    "https://docs.google.com/spreadsheets/d/TU_ID_DE_SPREADSHEET/edit"  # <-- Reemplaza
)

# Columnas esperadas
MOV_COLS = ["Id", "Usuario", "Fecha", "Monto", "Nombre", "Categoría", "Tipo"]
CAT_COLS = ["Usuario", "Categoría"]
DEFAULT_CATEGORIES = ["Comida", "Transporte", "Ocio", "Otros"]


# ========= Credenciales / Cliente =========
def _make_creds():
    """
    Cloud: usa st.secrets["gcp_service_account"] (Streamlit Cloud).
    Local: usa archivo 'credenciales.json' (o GOOGLE_CREDS_FILE).
    """
    # Intentar Cloud
    try:
        sa_info = st.secrets["gcp_service_account"]  # lanza si no existe
        return Credentials.from_service_account_info(sa_info, scopes=SCOPE)
    except Exception:
        # Local
        if not os.path.exists(CREDS_FILE):
            raise FileNotFoundError(
                "No hay credenciales. Define st.secrets['gcp_service_account'] en Cloud "
                f"o coloca un archivo JSON local en: {os.path.abspath(CREDS_FILE)}"
            )
        return Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)


def _gc():
    """Cliente gspread autorizado."""
    return gspread.authorize(_make_creds())


def _ws(sheet_name: str):
    """
    Devuelve la worksheet por nombre. Si no existe, la crea.
    Evita fallar en import: se ejecuta solo cuando hace falta.
    """
    gc = _gc()
    try:
        sh = gc.open_by_url(SPREADSHEET_URL)
    except Exception as e:
        raise RuntimeError(
            "No se pudo abrir el Spreadsheet por URL.\n"
            "- Verifica SPREADSHEET_URL (o variable SHEETS_URL)\n"
            "- Comparte la hoja con la Service Account como Editor\n"
            "- Habilita APIs de Sheets y Drive en GCP\n"
            f"Detalle: {e}"
        )
    try:
        return sh.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return sh.add_worksheet(title=sheet_name, rows=1000, cols=20)


def _sheet_to_df(ws, expected_cols):
    df = get_as_dataframe(ws, evaluate_formulas=True, header=0).dropna(how="all")
    if df.empty:
        df = pd.DataFrame(columns=expected_cols)
    # asegurar columnas mínimas y orden
    for c in expected_cols:
        if c not in df.columns:
            df[c] = [] if c != "Monto" else []
    return df[expected_cols]


def _df_to_sheet(ws, df: pd.DataFrame):
    if df is None:
        return
    ws.clear()
    set_with_dataframe(ws, df)


# ========= Movimientos =========
def load_expenses() -> pd.DataFrame:
    ws = _ws("gastos")
    df = _sheet_to_df(ws, MOV_COLS)
    # tipos/casts
    df["Id"] = df["Id"].astype(str)
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0.0)
    # migración si vinieran datos viejos sin 'Tipo'
    if "Tipo" not in df.columns:
        df["Tipo"] = "Gasto"
        save_expenses(df)
    return df


def save_expenses(df: pd.DataFrame):
    ws = _ws("gastos")
    _df_to_sheet(ws, df[MOV_COLS])


def add_movement(usuario: str, fecha: str, monto: float, nombre: str, categoria: str, tipo: str):
    if tipo not in ("Gasto", "Ingreso"):
        tipo = "Gasto"
    df = load_expenses()
    nuevo = {
        "Id": str(uuid.uuid4()),
        "Usuario": usuario,
        "Fecha": fecha,
        "Monto": float(monto),
        "Nombre": nombre,
        "Categoría": categoria,
        "Tipo": tipo,
    }
    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    save_expenses(df)


# Compat: si tu UI aún llama add_expense(...)
def add_expense(usuario: str, fecha: str, monto: float, nombre: str, categoria: str):
    add_movement(usuario, fecha, monto, nombre, categoria, "Gasto")


def delete_movement_by_id(mov_id: str) -> bool:
    df = load_expenses()
    before = len(df)
    df = df[df["Id"].astype(str) != str(mov_id)]
    if len(df) < before:
        save_expenses(df)
        return True
    return False


# ========= Categorías =========
def load_categories() -> pd.DataFrame:
    ws = _ws("categorias")
    return _sheet_to_df(ws, CAT_COLS)


def save_categories(df: pd.DataFrame):
    ws = _ws("categorias")
    _df_to_sheet(ws, df[CAT_COLS])


def get_user_categories(usuario: str):
    cats_df = load_categories()
    user_cats = cats_df[cats_df["Usuario"] == usuario]["Categoría"].dropna().unique().tolist()
    if not user_cats:
        nuevos = pd.DataFrame([{"Usuario": usuario, "Categoría": c} for c in DEFAULT_CATEGORIES])
        cats_df = pd.concat([cats_df, nuevos], ignore_index=True)
        save_categories(cats_df)
        user_cats = DEFAULT_CATEGORIES.copy()
    return user_cats


def add_category(usuario: str, categoria: str):
    categoria = str(categoria or "").strip()
    if not categoria:
        return "La categoría no puede estar vacía."
    cats_df = load_categories()
    existe = not cats_df[
        (cats_df["Usuario"] == usuario) & (cats_df["Categoría"].str.lower() == categoria.lower())
    ].empty
    if existe:
        return "Esa categoría ya existe."
    cats_df = pd.concat([cats_df, pd.DataFrame([{"Usuario": usuario, "Categoría": categoria}])], ignore_index=True)
    save_categories(cats_df)
    return None


def delete_category(usuario: str, categoria: str):
    cats_df = load_categories()
    cats_df = cats_df[~((cats_df["Usuario"] == usuario) & (cats_df["Categoría"] == categoria))]
    save_categories(cats_df)
