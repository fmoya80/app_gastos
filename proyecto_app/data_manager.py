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
CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credenciales_google_cloud.json")

# Usa SIEMPRE la URL (más robusto que por nombre)
SPREADSHEET_URL = os.getenv(
    "SHEETS_URL",
    "https://docs.google.com/spreadsheets/d/1-YXU838TIBtGewGsWEb_zg96FeMVbTH21BJBYaATY7s/edit?pli=1&gid=0#gid=0"  # <-- Reemplaza
)

# Columnas esperadas
MOV_COLS = ["id_transaccion", "Usuario", "Fecha", "Monto", "Nombre", "Categoría", "Tipo"]
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


@st.cache_resource(show_spinner=False)
def _gc_cached():
    return gspread.authorize(_make_creds())

@st.cache_resource(show_spinner=False)
def _open_sheet_cached():
    try:
        return _gc_cached().open_by_url(SPREADSHEET_URL)
    except Exception as e:
        raise RuntimeError(
            "No se pudo abrir el Spreadsheet por URL.\n"
            f"Detalle: {e}"
        )

def _ws(sheet_name: str):
    sh = _open_sheet_cached()
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
@st.cache_data(ttl=30, show_spinner=False)  # 30s
def load_expenses() -> pd.DataFrame:
    ws = _ws("gastos")
    df = _sheet_to_df(ws, MOV_COLS)
    df["id_transaccion"] = df["id_transaccion"].astype(str)
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0.0)
    if "Tipo" not in df.columns:
        df["Tipo"] = "Gasto"
        save_expenses(df)  # regraba (ver C abajo limpia cache)
    return df


def save_expenses(df: pd.DataFrame):
    ws = _ws("gastos")
    _df_to_sheet(ws, df[MOV_COLS])
    try:
        st.cache_data.clear()
    except Exception:
        pass


def add_movement(usuario: str, fecha: str, monto: float, nombre: str, categoria: str, tipo: str):
    if tipo not in ("Gasto", "Ingreso"):
        tipo = "Gasto"

    ws = _ws("gastos")
    fila = [
        str(uuid.uuid4()),
        usuario,
        fecha,
        float(monto),
        nombre,
        categoria,
        tipo,
    ]
    ws.append_row(fila, value_input_option="USER_ENTERED")

    try:
        st.cache_data.clear()
    except Exception:
        pass


# Compat: si tu UI aún llama add_expense(...)
def add_expense(usuario: str, fecha: str, monto: float, nombre: str, categoria: str):
    add_movement(usuario, fecha, monto, nombre, categoria, "Gasto")


def delete_expense_by_id(mov_id: str) -> bool:
    df = load_expenses()
    before = len(df)
    df = df[df["id_transaccion"].astype(str) != str(mov_id)]
    if len(df) < before:
        save_expenses(df)
        return True
    return False


# ========= Categorías =========
@st.cache_data(ttl=300, show_spinner=False)  # 5 min
def load_categories() -> pd.DataFrame:
    ws = _ws("categorias")
    df = _sheet_to_df(ws, CAT_COLS)
    df["Usuario"] = df["Usuario"].astype(str)
    df["Categoría"] = df["Categoría"].astype(str)
    return df


def save_categories(df: pd.DataFrame):
    ws = _ws("categorias")
    _df_to_sheet(ws, df[CAT_COLS])


@st.cache_data(ttl=300, show_spinner=False)
def _raw_categories():
    ws = _ws("categorias")
    # Leemos solo dos columnas y acotamos filas si quieres
    values = ws.get_all_values()
    return values  # [[Usuario, Categoría], ...]

def get_user_categories(usuario: str):
    values = _raw_categories()
    if not values:
        # Inicializa por defecto
        ws = _ws("categorias")
        ws.append_rows([[usuario, c] for c in DEFAULT_CATEGORIES], value_input_option="USER_ENTERED")
        try:
            st.cache_data.clear()
        except Exception:
            pass
        return DEFAULT_CATEGORIES.copy()

    header = values[0] if values else []
    rows = values[1:] if len(values) > 1 else []

    idx_user = header.index("Usuario") if "Usuario" in header else 0
    idx_cat  = header.index("Categoría") if "Categoría" in header else 1

    user_cats = [r[idx_cat] for r in rows if len(r) > idx_cat and r[idx_user] == usuario and r[idx_cat]]
    if not user_cats:
        ws = _ws("categorias")
        ws.append_rows([[usuario, c] for c in DEFAULT_CATEGORIES], value_input_option="USER_ENTERED")
        try:
            st.cache_data.clear()
        except Exception:
            pass
        return DEFAULT_CATEGORIES.copy()

    # únicas y ordenadas
    return sorted(list(dict.fromkeys([str(c) for c in user_cats])))


def add_category(usuario: str, categoria: str):
    cat = (categoria or "").strip()
    if not cat:
        return False, "Ingresa un nombre de categoría."

    df = load_categories()  # cacheada
    # evitar duplicados (case-insensitive)
    if ((df["Usuario"] == usuario) & (df["Categoría"].str.lower() == cat.lower())).any():
        return False, f"La categoría '{cat}' ya existe."

    ws = _ws("categorias")
    ws.append_row([usuario, cat], value_input_option="USER_ENTERED")

    _clear_category_caches()  # muy importante para que el selectbox vea el cambio
    return True, ""


def delete_category(usuario: str, categoria: str):
    df = load_categories()
    before = len(df)
    df = df[~((df["Usuario"] == usuario) & (df["Categoría"] == categoria))]
    if len(df) < before:
        save_categories(df)     # tu save_categories ya debería limpiar cache global o hazlo aquí
        _clear_category_caches()  # <<<<<< IMPORTANTE
        return True
    return False

# --- helpers de cache ---
def _clear_cache_of(fn):
    try:
        fn.clear()
    except Exception:
        pass

def _clear_category_caches():
    # Limpia TODO lo que alimente categorías
    _clear_cache_of(load_categories)
    # Si tienes una función cacheada tipo _raw_categories(), límpiala también:
    try:
        _raw_categories.clear()
    except Exception:
        pass
    # Si llegaste a cachear get_user_categories, límpiala:
    try:
        get_user_categories.clear()
    except Exception:
        pass