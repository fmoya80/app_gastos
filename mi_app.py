import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuración de la página ---
st.set_page_config(page_title="Registro de Gastos", page_icon="💰", layout="centered")

st.title("💰 Registro de Gastos")

# --- Entrada de datos ---
monto = st.number_input("Monto", min_value=0.0, step=100.0, format="%.2f")
nombre = st.text_input("Nombre del gasto")
categoria = st.selectbox("Categoría", ["Comida", "Transporte", "Ocio", "Otros"])

# --- Guardar gasto ---
if st.button("Registrar gasto"):
    if monto > 0 and nombre.strip() != "":
        nuevo_gasto = pd.DataFrame(
            [[datetime.now().strftime("%Y-%m-%d %H:%M"), monto, nombre, categoria]],
            columns=["Fecha", "Monto", "Nombre", "Categoría"]
        )

        try:
            df = pd.read_csv("gastos.csv")
            df = pd.concat([df, nuevo_gasto], ignore_index=True)
        except FileNotFoundError:
            df = nuevo_gasto

        df.to_csv("gastos.csv", index=False)
        st.success("✅ Gasto registrado.")
    else:
        st.warning("Por favor ingresa un monto y nombre válido.")

# --- Mostrar gastos ---
if st.checkbox("📋 Ver gastos registrados"):
    try:
        df = pd.read_csv("gastos.csv")
        st.dataframe(df)

        # Calcular total gastado
        total_gastado = df["Monto"].sum()
        st.subheader(f"💵 Total gastado: ${total_gastado:,.0f}")

        # Botón para descargar CSV
        st.download_button(
            label="⬇️ Descargar CSV",
            data=df.to_csv(index=False),
            file_name="gastos.csv",
            mime="text/csv"
        )

    except FileNotFoundError:
        st.info("Aún no hay gastos registrados.")
