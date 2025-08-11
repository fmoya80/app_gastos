import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuración ---
st.set_page_config(page_title="Registro de Gastos", page_icon="💰", layout="centered")

st.title("💰 Registro de Gastos")

# --- Selección de usuario ---
usuario = st.text_input("👤 Nombre de usuario", placeholder="Ej: Felipe")

if usuario.strip() != "":
    # --- Entrada de datos ---
    monto = st.number_input("Monto", min_value=0.0, step=100.0, format="%.2f")
    nombre = st.text_input("Nombre del gasto")
    categoria = st.selectbox("Categoría", ["Comida", "Transporte", "Ocio", "Otros"])

    # --- Guardar gasto ---
    if st.button("Registrar gasto"):
        if monto > 0 and nombre.strip() != "":
            nuevo_gasto = pd.DataFrame(
                [[usuario, datetime.now().strftime("%Y-%m-%d %H:%M"), monto, nombre, categoria]],
                columns=["Usuario", "Fecha", "Monto", "Nombre", "Categoría"]
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
            df_usuario = df[df["Usuario"] == usuario]

            if not df_usuario.empty:
                st.dataframe(df_usuario)

                # Total gastado
                total_gastado = df_usuario["Monto"].sum()
                st.subheader(f"💵 Total gastado: ${total_gastado:,.0f}")

                # Selección para borrar gasto
                gasto_a_borrar = st.selectbox("Selecciona un gasto para eliminar",
                    df_usuario.apply(lambda x: f"{x['Fecha']} - {x['Nombre']} (${x['Monto']})", axis=1)
                )

                if st.button("🗑 Borrar gasto"):
                    index_a_borrar = df_usuario[df_usuario.apply(
                        lambda x: f"{x['Fecha']} - {x['Nombre']} (${x['Monto']})" == gasto_a_borrar,
                        axis=1
                    )].index

                    df = df.drop(index_a_borrar)
                    df.to_csv("gastos.csv", index=False)
                    st.success("✅ Gasto eliminado.")
                    st.experimental_rerun()

                # Botón para descargar CSV del usuario
                st.download_button(
                    label="⬇️ Descargar CSV",
                    data=df_usuario.to_csv(index=False),
                    file_name=f"gastos_{usuario}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No hay gastos registrados para este usuario.")
        except FileNotFoundError:
            st.info("Aún no hay gastos registrados.")
else:
    st.warning("Por favor ingresa un nombre de usuario para comenzar.")
