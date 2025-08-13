import streamlit as st
from datetime import datetime, date
from data_manager import add_movement, get_user_categories
import time

def render_tab(usuario: str):
    st.subheader("Registrar movimiento")
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.radio("tipo", ["Ingreso", "Gasto"], horizontal=True)
        monto = st.number_input("monto", min_value=0.0, step=100.0, format="%.0f")
        categoria = st.selectbox("categoria", get_user_categories(usuario), key="cat_select_reg")
    with col2:
        nombre = st.text_input("nombre")
        fecha_manual = st.checkbox("Usar fecha y hora manual")
        if fecha_manual:
            fecha = st.text_input("Fecha (YYYY-MM-DD HH:MM)", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        else:
            fecha = None

    if st.button("Registrar", type="primary"):
        if monto > 0 and nombre.strip():
            fecha_val = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M")
            add_movement(usuario, fecha_val, monto, nombre, categoria, tipo)
            st.success("✅ Movimiento registrado.")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Por favor ingresa un monto y nombre válido.")
