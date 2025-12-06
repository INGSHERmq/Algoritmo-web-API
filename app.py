# app.py - LANDING PROFESIONAL 100% FUNCIONAL (Streamlit + tu API en Render)
import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

# ================================= CONFIGURACIÓN =================================
st.set_page_config(
    page_title="Alerta Dengue Chincha Alta 2026",
    page_icon="https://ibb.co/tw3k8t8L",
    layout="centered"
)

st.image("https://i.ibb.co/5k5j3kR/dengue-banner.jpg", use_column_width=True)  # opcional
st.title("Sistema de Alerta Temprana de Dengue")
st.markdown("### Distrito de Chincha Alta – Pronóstico 2026")
st.markdown("**Sube tu archivo oficial del MINSA (Excel o CSV)** y obtén el pronóstico en segundos.")
st.markdown("---")

# =================================== API URL =====================================
API_URL = "https://algoritmo-web-api.onrender.com/predict"

# =================================== SUBIR ARCHIVO ================================
file = st.file_uploader(
    "Archivo de casos de dengue",
    type=["xlsx", "csv"],
    help="Cualquier reporte oficial del MINSA sirve"
)

if file:
    with st.spinner("Procesando datos con inteligencia artificial..."):
        try:
            # ¡¡¡LÍNEA MÁGICA QUE ARREGLA TODO!!!
            files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
            headers = {}  # no hace falta Content-Type, requests lo pone solo
            response = requests.post(API_URL, files=files, headers=headers, timeout=90)

            if response.status_code == 200:
                r = response.json()["results"]

                st.success("¡Análisis completado exitosamente!")
                st.markdown(f"**Período analizado:** {r['periodo']} | {r['total_años']} años")

                # ==================== TARJETAS PRINCIPALES ====================
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Pronóstico 2026", f"{r['pronostico']['casos_pronosticados']:,} casos")
                with col2:
                    clas = r['pronostico']['clasificacion']
                    color = "#d32f2f" if "ALTA" in clas else "#388e3c"
                    st.markdown(f"<h2 style='text-align:center; color:{color};'>{clas}</h2>", unsafe_allow_html=True)
                with col3:
                    prob = r['pronostico']['probabilidad_brote_%']
                    st.metric("Probabilidad de brote", f"{prob}%")

                st.markdown("---")

                # ==================== GRÁFICO BONITO ====================
                years = list(r["casos_historicos"].keys())
                cases = list(r["casos_historicos"].values())

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=years,
                    y=cases,
                    name="Casos reales",
                    marker_color="lightblue",
                    text=cases,
                    textposition="outside"
                ))
                fig.add_trace(go.Scatter(
                    x=[years[-1], r['pronostico']['año']],
                    y=[cases[-1], max(r['pronostico']['casos_pronosticados'], 0)],
                    mode="lines+markers",
                    name="Pronóstico 2026",
                    line=dict(color="red", width=6),
                    marker=dict(size=16)
                ))
                fig.add_hline(
                    y=r['umbral_alerta'],
                    line_dash="dash",
                    line_color="orange",
                    annotation_text=f"Umbral de alerta ({r['umbral_alerta']:,} casos)"
                )
                fig.update_layout(
                    title="Evolución histórica y pronóstico de casos de dengue",
                    xaxis_title="Año",
                    yaxis_title="Número de casos",
                    height=550,
                    template="simple_white"
                )
                st.plotly_chart(fig, use_container_width=True)

                # ==================== KPIs DETALLADOS ====================
                with st.expander("Indicadores técnicos y KPIs"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Picos históricos**")
                        st.write(f"• Año con más casos: **{r['kpis']['Año Pico']}** ({r['kpis']['Casos Máximos Históricos']:,} casos)")
                        st.write(f"• Índice de severidad: **{r['kpis']['Índice de Severidad (%)']}%**")
                    with col2:
                        st.write("**Tendencia**")
                        tasa = r['kpis']['Tasa de Crecimiento Anual Promedio (%)']
                        st.write(f"• Tasa de crecimiento anual: **{tasa:+.2f}%**")
                        st.write(f"• Intervalo de confianza 90%: {r['pronostico']['intervalo_confianza_90'][0]:,} – {r['pronostico']['intervalo_confianza_90'][1]:,} casos")

                st.info(r["mensaje"])

                st.caption(f"Análisis generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Modelo: Regresión polinómica + umbral percentil 75")

            else:
                st.error("Error del servidor. Inténtalo de nuevo en unos segundos.")
                st.code(response.text)

        except requests.exceptions.RequestException as e:
            st.error("No se pudo conectar con el servidor de predicción.")
            st.write("Revisa tu conexión o intenta más tarde.")

else:
    st.info("Sube tu archivo para comenzar el análisis")
    st.markdown("""
    ### ¿Cómo funciona?
    1. Descarga cualquier reporte oficial de dengue del MINSA  
    2. Súbelo aquí arriba  
    3. En segundos sabrás si Chincha Alta tendrá brote en 2026
    """)

# ================================= FOOTER =================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 14px;'>
    Sistema de Vigilancia Epidemiológica Predictiva<br>
    Modelo desarrollado con datos oficiales 2020–2025 | DIRESA Ica - Perú
</div>
""", unsafe_allow_html=True)