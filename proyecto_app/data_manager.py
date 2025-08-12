import pandas as pd
import os
from config import DATA_DIR, GASTOS_FILE, CATS_FILE, DEFAULT_CATEGORIES

os.makedirs(DATA_DIR, exist_ok=True)

# ---------- Movimientos (Gasto/Ingreso) ----------
def load_expenses():
    try:
        df = pd.read_csv(GASTOS_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Usuario", "Fecha", "Monto", "Nombre", "Categoría", "Tipo"])
    # Migración automática: si no existe 'Tipo', asumir 'Gasto'
    if "Tipo" not in df.columns:
        df["Tipo"] = "Gasto"
        save_expenses(df)
    return df

def save_expenses(df: pd.DataFrame):
    # asegurar columnas
    for col in ["Usuario", "Fecha", "Monto", "Nombre", "Categoría", "Tipo"]:
        if col not in df.columns:
            df[col] = "" if col != "Monto" else 0.0
    df.to_csv(GASTOS_FILE, index=False)

def add_movement(usuario: str, fecha: str, monto: float, nombre: str, categoria: str, tipo: str):
    if tipo not in ("Gasto", "Ingreso"):
        tipo = "Gasto"
    df = load_expenses()
    nuevo = {
        "Usuario": usuario,
        "Fecha": fecha,
        "Monto": float(monto),
        "Nombre": nombre,
        "Categoría": categoria,
        "Tipo": tipo
    }
    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    save_expenses(df)

# Compatibilidad hacia atrás: add_expense = movimiento de tipo Gasto
def add_expense(usuario: str, fecha: str, monto: float, nombre: str, categoria: str):
    add_movement(usuario, fecha, monto, nombre, categoria, "Gasto")

def delete_expense_by_index(idx: int):
    df = load_expenses()
    if idx in df.index:
        df = df.drop(index=idx)
        save_expenses(df)
        return True
    return False

# ---------- Categorías (igual que ya tenías) ----------
def load_categories():
    try:
        return pd.read_csv(CATS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Usuario", "Categoría"])

def save_categories(df: pd.DataFrame):
    df.to_csv(CATS_FILE, index=False)

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
    categoria = categoria.strip()
    if not categoria:
        return "La categoría no puede estar vacía."
    cats_df = load_categories()
    existe = not cats_df[(cats_df["Usuario"] == usuario) & (cats_df["Categoría"].str.lower() == categoria.lower())].empty
    if existe:
        return "Esa categoría ya existe."
    cats_df = pd.concat([cats_df, pd.DataFrame([{"Usuario": usuario, "Categoría": categoria}])], ignore_index=True)
    save_categories(cats_df)
    return None

def delete_category(usuario: str, categoria: str):
    cats_df = load_categories()
    idx = cats_df[(cats_df["Usuario"] == usuario) & (cats_df["Categoría"] == categoria)].index
    if not idx.empty:
        cats_df = cats_df.drop(index=idx)
        save_categories(cats_df)
