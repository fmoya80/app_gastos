import streamlit as st
from data_manager import load_expenses
from ui_helpers import money_fmt
# si usabas render_expense_row, ahora mostramos columnas personalizadas para incluir Tipo

def render_tab(usuario: str):
    st.subheader("Movimientos del usuario")
    df_all = load_expenses()
    df_user = df_all[df_all["Usuario"] == usuario].copy()

    if df_user.empty:
        st.info("No hay movimientos para este usuario.")
        return

    # Filtros
    with st.expander("Filtros"):
        f1, f2 = st.columns(2)
        fecha_desde = f1.text_input("Desde (YYYY-MM-DD)", value="")
        fecha_hasta = f2.text_input("Hasta (YYYY-MM-DD)", value="")
        if fecha_desde.strip():
            df_user = df_user[df_user["Fecha"] >= fecha_desde]
        if fecha_hasta.strip():
            df_user = df_user[df_user["Fecha"] <= f"{fecha_hasta} 99:99"]

        tipos = st.multiselect("Tipo", ["Gasto", "Ingreso"], default=["Gasto", "Ingreso"])
        if tipos:
            df_user = df_user[df_user["Tipo"].isin(tipos)]

        cats_disp = sorted(df_user["Categoría"].dropna().unique().tolist())
        cats_sel = st.multiselect("Categorías", cats_disp)
        if cats_sel:
            df_user = df_user[df_user["Categoría"].isin(cats_sel)]

    # Resumen
    total_ing = df_user[df_user["Tipo"] == "Ingreso"]["Monto"].sum()
    total_gas = df_user[df_user["Tipo"] == "Gasto"]["Monto"].sum()
    saldo = total_ing - total_gas

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos",  money_fmt(total_ing))
    c2.metric("Gastos",    money_fmt(total_gas))
    c3.metric("Saldo",     money_fmt(saldo))

    # Tabla con botón borrar por fila
    header = st.columns([1.2, 2.0, 1.4, 2.6, 2.0, 1.0])
    header[0].markdown("**Tipo**")
    header[1].markdown("**Fecha**")
    header[2].markdown("**Monto**")
    header[3].markdown("**Nombre**")
    header[4].markdown("**Categoría**")
    header[5].markdown("**Acción**")

    from data_manager import delete_expense_by_index
    for idx, row in df_user.iterrows():
        cols = st.columns([1.2, 2.0, 1.4, 2.6, 2.0, 1.0])
        cols[0].write("🟢 Ingreso" if row["Tipo"] == "Ingreso" else "🔴 Gasto")
        cols[1].write(row["Fecha"])
        monto_txt = f"+ {money_fmt(row['Monto'])}" if row["Tipo"] == "Ingreso" else f"- {money_fmt(row['Monto'])}"
        cols[2].write(monto_txt)
        cols[3].write(row["Nombre"])
        cols[4].write(row["Categoría"])
        if cols[5].button("🗑️", key=f"del_{idx}", help="Eliminar este movimiento"):
            if delete_expense_by_index(idx):
                st.success("✅ Movimiento eliminado.")
                st.rerun()
            else:
                st.error("No se pudo eliminar el movimiento.")

    # Descarga solo del usuario (con filtros aplicados)
    st.download_button(
        label="⬇️ Descargar CSV (este usuario)",
        data=df_user.to_csv(index=False),
        file_name=f"movimientos_{usuario}.csv",
        mime="text/csv"
    )
