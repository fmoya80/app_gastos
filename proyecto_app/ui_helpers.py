import streamlit as st
from config import CURRENCY_SYMBOL, THOUSAND_SEPARATOR
from data_manager import delete_expense_by_index

def money_fmt(value: float) -> str:
    # Muestra miles con punto (ej: 1.234) y sin decimales
    return f"{CURRENCY_SYMBOL}{format(int(round(value)), ',').replace(',', THOUSAND_SEPARATOR)}"

def render_expense_row(idx, row):
    cols = st.columns([2.2, 1.4, 2.6, 2.0, 1.0])
    cols[0].write(row["Fecha"])
    cols[1].write(money_fmt(row["Monto"]))
    cols[2].write(row["Nombre"])
    cols[3].write(row["Categoría"])
    if cols[4].button("🗑️", key=f"del_{idx}", help="Eliminar este gasto"):
        if delete_expense_by_index(idx):
            st.success("✅ Gasto eliminado.")
            st.rerun()
        else:
            st.error("No se pudo eliminar el gasto.")
