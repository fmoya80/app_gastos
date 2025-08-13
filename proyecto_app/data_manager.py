import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import uuid

# ===== CONFIGURACIÓN =====
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credenciales_google_cloud.json"  # tu archivo descargado de Google Cloud
SPREADSHEET_NAME = "base_app_gastos"

# Conectar cliente
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)

# Abrir documento
sheet_gastos = client.open(SPREADSHEET_NAME).worksheet("gastos")
sheet_cats = client.open(SPREADSHEET_NAME).worksheet("categorias")


# ===== Funciones de ayuda =====
def sheet_to_df(worksheet):
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def df_to_sheet(worksheet, df):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


# ===== Gastos =====
def load_expenses():
    df = sheet_to_df(sheet_gastos)
    if df.empty:
        df = pd.DataFrame(columns=["id_transaccion", "Usuario", "Fecha", "Monto", "Nombre", "Categoría", "Tipo"])
    return df

def save_expenses(df):
    df_to_sheet(sheet_gastos, df)

def add_expense(usuario, fecha, monto, nombre, categoria, tipo="Gasto"):
    df = load_expenses()
    nuevo = {
        "id_transaccion": str(uuid.uuid4()),
        "Usuario": usuario,
        "Fecha": fecha,
        "Monto": float(monto),
        "Nombre": nombre,
        "Categoría": categoria,
        "Tipo": tipo
    }
    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    save_expenses(df)

def delete_expense_by_id(expense_id):
    df = load_expenses()
    df = df[df["id_transaccion"] != expense_id]
    save_expenses(df)


# ===== Categorías =====
def load_categories():
    df = sheet_to_df(sheet_cats)
    if df.empty:
        df = pd.DataFrame(columns=["Usuario", "Categoría"])
    return df

def save_categories(df):
    df_to_sheet(sheet_cats, df)

def get_user_categories(usuario):
    cats_df = load_categories()
    user_cats = cats_df[cats_df["Usuario"] == usuario]["Categoría"].dropna().unique().tolist()
    if not user_cats:
        default = ["Comida", "Transporte", "Ocio", "Otros"]
        nuevos = pd.DataFrame([{"Usuario": usuario, "Categoría": c} for c in default])
        cats_df = pd.concat([cats_df, nuevos], ignore_index=True)
        save_categories(cats_df)
        return default
    return user_cats

def add_category(usuario, categoria):
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

def delete_category(usuario, categoria):
    cats_df = load_categories()
    cats_df = cats_df[~((cats_df["Usuario"] == usuario) & (cats_df["Categoría"] == categoria))]
    save_categories(cats_df)
