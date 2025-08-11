import streamlit as st
import pandas as pd
from datetime import datetime

# ---------- Config ----------
st.set_page_config(page_title="Registro de Gastos", page_icon="💰", layout="centered")
st.title("💰 Registro de Gastos con Pestañas")

GASTOS_FILE = "gastos.csv"
CATS_FILE = "categorias.csv"
CATS_DEFAULT = ["Comida", "Transporte", "Ocio", "Otros"]

# ---------- Utils: gastos ----------
def cargar_df_gastos():
    try:
        return pd.read_csv(GASTOS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Usuario", "Fecha", "Monto", "Nombre", "Categoría"])

def guardar_df_gastos(df):
    df.to_csv(GASTOS_FILE, index=False)

# ---------- Utils: categorías ----------
def cargar_df_categorias():
    try:
        return pd.read_csv(CATS_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Usuario", "Categoría"])

def guardar_df_categorias(df):
    df.to_csv(CATS_FILE, index=False)

def get_categorias_usuario(usuario: str):
    cats_df = cargar_df_categorias()
    user_cats = cats_df[cats_df["Usuario"] == usuario]["Categoría"].dropna().unique().tolist()
    if not user_cats:  # inicializar por defecto
        nuevos = pd.DataFrame([{"Usuario": usuario, "Categoría": c} for c in CATS_DEFAULT])
        cats_df = pd.concat([cats_df, nuevos], ignore_index=True)
        guardar_df_categorias(cats_df)
        user_cats = CATS_DEFAULT.copy()
    return user_cats

def add_categoria(usuario: str, categoria: str):
    categoria = categoria.strip()
    if not categoria:
        return "La categoría no puede estar vacía."
    cats_df = cargar_df_categorias()
    existe = not cats_df[(cats_df["Usuario"] == usuario) & (cats_df["Categoría"].str.lower() == categoria.lower())].empty
    if existe:
        return "Esa categoría ya existe."
    cats_df = pd.concat([cats_df, pd.DataFrame([{"Usuario": usuario, "Categoría": categoria}])], ignore_index=True)
    guardar_df_categorias(cats_df)
    return None

def delete_categoria(usuario: str, categoria: str):
    cats_df = cargar_df_categorias()
    idx = cats_df[(cats_df["Usuario"] == usuario) & (cats_df["Categoría"] == categoria)].index
    if not idx.empty:
        cats_df = cats_df.drop(index=idx)
        guardar_df_categorias(cats_df)

# ---------- UI helpers ----------
def render_fila_gasto(idx, row):
    cols = st.columns([2.2, 1.4, 2.6, 2.0, 1.0])
    cols[0].write(row["Fecha"])
    cols[1].write(f"${row['Monto']:,.0f}".replace(",", "."))
    cols[2].write(row["Nombre"])
    cols[3].write(row["Categoría"])
    if cols[4].button("🗑️", key=f"del_{idx}", help="Eliminar este gasto"):
        df_full = cargar_df_gastos()
        if idx in df_full.index:
            df_full = df_full.drop(index=idx)
            guardar_df_gastos(df_full)
            st.success("✅ Gasto eliminado.")
            st.rerun()

# ---------- App ----------
usuario = st.text_input("👤 Nombre de usuario", placeholder="Ej: Felipe")

if not usuario.strip():
    st.warning("Por favor ingresa un nombre de usuario para comenzar.")
    st.stop()

tab_registrar, tab_gastos, tab_categorias = st.tabs(["➕ Registrar", "📋 Gastos", "🏷️ Categorías"])

# ====== Pestaña: Registrar ======
with tab_registrar:
    st.subheader("Registrar gasto")
    col1, col2 = st.columns(2)
    with col1:
        monto = st.number_input("Monto", min_value=0.0, step=100.0, format="%.0f")
        categoria = st.selectbox("Categoría", get_categorias_usuario(usuario), key="cat_select_reg")
    with col2:
        nombre = st.text_input("Nombre del gasto")
        fecha_manual = st.checkbox("Usar fecha y hora manual")
        if fecha_manual:
            fecha = st.text_input("Fecha (YYYY-MM-DD HH:MM)", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        else:
            fecha = None

    if st.button("Registrar gasto", type="primary"):
        if monto > 0 and nombre.strip():
            df = cargar_df_gastos()
            nuevo = {
                "Usuario": usuario,
                "Fecha": fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Monto": float(monto),
                "Nombre": nombre,
                "Categoría": categoria
            }
            df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
            guardar_df_gastos(df)
            st.success("✅ Gasto registrado.")
            st.rerun()
        else:
            st.warning("Por favor ingresa un monto y nombre válido.")

# ====== Pestaña: Gastos ======
with tab_gastos:
    st.subheader("Gastos del usuario")
    df_all = cargar_df_gastos()
    df_user = df_all[df_all["Usuario"] == usuario].copy()

    if df_user.empty:
        st.info("No hay gastos registrados para este usuario.")
    else:
        # Filtros opcionales
        with st.expander("Filtros"):
            f1, f2 = st.columns(2)
            fecha_desde = f1.text_input("Desde (YYYY-MM-DD)", value="")
            fecha_hasta = f2.text_input("Hasta (YYYY-MM-DD)", value="")
            if fecha_desde.strip():
                df_user = df_user[df_user["Fecha"] >= fecha_desde]
            if fecha_hasta.strip():
                df_user = df_user[df_user["Fecha"] <= f"{fecha_hasta} 99:99"]

            cats_disp = sorted(df_user["Categoría"].dropna().unique().tolist())
            cats_sel = st.multiselect("Categorías", cats_disp)
            if cats_sel:
                df_user = df_user[df_user["Categoría"].isin(cats_sel)]

        total_gastado = df_user["Monto"].sum() if not df_user.empty else 0.0
        st.subheader(f"💵 Total gastado: ${total_gastado:,.0f}".replace(",", "."))

        # Encabezado tabla
        header = st.columns([2.2, 1.4, 2.6, 2.0, 1.0])
        header[0].markdown("**Fecha**")
        header[1].markdown("**Monto**")
        header[2].markdown("**Nombre**")
        header[3].markdown("**Categoría**")
        header[4].markdown("**Acción**")

        for idx, row in df_user.iterrows():
            render_fila_gasto(idx, row)

        # 👇 Solo descarga del usuario (con filtros aplicados)
        st.download_button(
            label="⬇️ Descargar CSV (este usuario)",
            data=df_user.to_csv(index=False),
            file_name=f"gastos_{usuario}.csv",
            mime="text/csv"
        )

# ====== Pestaña: Categorías ======
with tab_categorias:
    st.subheader("Gestionar categorías")
    user_cats = get_categorias_usuario(usuario)

    c1, c2 = st.columns([3, 1.2])
    with c1:
        nueva_cat = st.text_input("Crear nueva categoría", placeholder="Ej: Salud, Educación, Suscripciones...")
    with c2:
        if st.button("Agregar"):
            error = add_categoria(usuario, nueva_cat)
            if error:
                st.warning(error)
            else:
                st.success(f"✅ Categoría '{nueva_cat}' creada.")
                st.rerun()

    st.caption("Tus categorías:")
    if user_cats:
        header = st.columns([4, 1])
        header[0].markdown("**Categoría**")
        header[1].markdown("**Acción**")
        for cat in sorted(user_cats, key=str.lower):
            cols = st.columns([4, 1])
            cols[0].write(cat)
            deshabilitar = len(user_cats) <= 1
            if cols[1].button("🗑️", key=f"del_cat_{cat}", disabled=deshabilitar, help="Eliminar categoría"):
                delete_categoria(usuario, cat)
                st.success(f"✅ Categoría '{cat}' eliminada.")
                st.rerun()
    else:
        st.info("Aún no tienes categorías. Crea la primera arriba.")
