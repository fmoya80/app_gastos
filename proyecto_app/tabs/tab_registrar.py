import streamlit as st
from datetime import datetime
from data_manager import add_movement, get_user_categories

def render_tab(usuario: str):
    st.subheader("Registrar movimiento")

    # ⬅️ Botón de refresco (FUERA del form)
    if st.button("🔄 Actualizar categorías"):
        st.session_state["cat_nonce"] = st.session_state.get("cat_nonce", 0) + 1
        st.rerun()

    with st.form("frm_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.radio("tipo", ["Ingreso", "Gasto"], horizontal=True)
            monto = st.number_input("monto", min_value=0.0, step=100.0, format="%.0f")
            nonce = st.session_state.get("cat_nonce", 0)
            categoria = st.selectbox(
                "categoria",
                get_user_categories(usuario),
                key=f"cat_select_reg_{nonce}"  # <- cambia cuando cat_nonce cambia
            )

        with col2:
            nombre = st.text_input("nombre")
            fecha_manual = st.checkbox("Usar fecha y hora manual")
            fecha = (
                st.text_input("Fecha (YYYY-MM-DD HH:MM)", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
                if fecha_manual else None
            )

        submitted = st.form_submit_button("Registrar")
        if submitted:
            if monto > 0 and nombre.strip():
                fecha_val = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M")
                add_movement(usuario, fecha_val, monto, nombre, categoria, tipo)
                st.success("✅ Movimiento registrado.")
            else:
                st.warning("Por favor ingresa un monto y nombre válido.")
