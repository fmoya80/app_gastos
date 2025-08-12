import streamlit as st
from data_manager import get_user_categories, add_category, delete_category
import time

def render_tab(usuario: str):
    st.subheader("Gestionar categorías")

    # Crear
    c1, c2 = st.columns([3, 1.2])
    with c1:
        nueva_cat = st.text_input("Crear nueva categoría", placeholder="Ej: Salud, Educación, Suscripciones...")
    with c2:
        if st.button("Agregar"):
            error = add_category(usuario, nueva_cat)
            if error:
                st.warning(error)
            else:
                st.success(f"✅ Categoría '{nueva_cat}' creada.")
                time.sleep
                st.rerun()

    # Listado + borrar
    user_cats = get_user_categories(usuario)
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
                delete_category(usuario, cat)
                st.success(f"✅ Categoría '{cat}' eliminada.")
                time.sleep(1)
                st.rerun()
    else:
        st.info("Aún no tienes categorías. Crea la primera arriba.")
