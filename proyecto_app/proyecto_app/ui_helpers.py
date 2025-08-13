# ui_helpers.py
import streamlit as st
from data_manager import delete_expense_by_id
from config import CURRENCY_SYMBOL, THOUSAND_SEPARATOR

def money_fmt(value: float) -> str:
    return f"{CURRENCY_SYMBOL}{format(int(round(value)), ',').replace(',', THOUSAND_SEPARATOR)}"

def render_expense_row(row):
    # row es una Serie con 'id_transaccion'
    cols = st.columns([2.0, 1.4, 2.6, 2.0, 1.0])
    cols[0].write(row["Fecha"])
    cols[1].write(money_fmt(row["Monto"]))
    cols[2].write(row["Nombre"])
    cols[3].write(row["Categoría"])
    if cols[4].button("🗑️", key=f"del_{row['id_transaccion']}", help="Eliminar este movimiento"):
        if delete_expense_by_id(row["id_transaccion"]):
            st.success("✅ Movimiento eliminado.")
            st.rerun()
        else:
            st.error("No se pudo eliminar.")
