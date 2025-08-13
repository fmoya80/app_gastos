import streamlit as st

# Importa las tabs
from tabs.tab_gastos import render_tab as tab_gastos
from tabs.tab_registrar import render_tab as tab_registrar
from tabs.tab_categorias import render_tab as tab_categorias

st.set_page_config(page_title="App de Gastos", layout="wide")

usuario = st.text_input("Usuario", value="demo_user")

menu = st.sidebar.radio(
    "Menú",
    ["Registrar movimiento", "Ver gastos", "Categorías"]
)

if usuario.strip():
    if menu == "Registrar movimiento":
        tab_registrar(usuario)
    elif menu == "Ver gastos":
        tab_gastos(usuario)
    elif menu == "Categorías":
        tab_categorias(usuario)
else:
    st.warning("Ingresa un nombre de usuario para continuar.")
