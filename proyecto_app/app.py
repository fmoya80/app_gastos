import streamlit as st
from tabs.tab_registrar import render_tab as tab_registrar
from tabs.tab_gastos import render_tab as tab_gastos
from tabs.tab_categorias import render_tab as tab_categorias

st.set_page_config(page_title="Registro de Gastos", page_icon="💰", layout="centered")
st.title("💰 ¡Bienvenido!")

usuario = st.text_input("👤 Nombre de usuario", placeholder="Ej: Felipe")
if not usuario.strip():
    st.warning("Por favor ingresa un nombre de usuario para comenzar.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["➕ Registrar", "📋 Movimientos", "🏷️ Categorías"])

with tab1:
    tab_registrar(usuario)

with tab2:
    tab_gastos(usuario)

with tab3:
    tab_categorias(usuario)

