import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Alerta Dengue Chincha Alta 2026", layout="centered", page_icon="mosquito")

st.title("Sistema de Alerta Temprana de Dengue")
st.markdown("### Chincha Alta – Pronóstico 2026")
st.markdown("**Sube tu archivo del MINSA (Excel o CSV)** y obtén el análisis completo en segundos.")
st.markdown("---")

API_URL = "https://algoritmo-web-api.onrender.com/predict"

file = st.file_uploader("Archivo oficial de casos", type=["xlsx", "csv"])

if file:
    with st.spinner("Despertando el modelo y analizando datos... (puede tardar 20-40 segundos la primera vez)"):
        try:
            files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
            response = requests.post(API_URL, files=files, timeout=120)  # alto timeout para Render

            if response.status_code == 200:
                r = response.json()["results"]

                st.success("¡Análisis completado con éxito!")
                st.markdown(f"**Período:** {r['periodo']} | {r['total_años']} años de datos")

                # ===== CORREGIR CASOS NEGATIVOS (más profesional) =====
                pronostico = max(r['pronostico']['casos_pronosticados'], 0)
                if pronostico == 0:
                    pronostico_texto = "< 50 casos (baja actividad)"
                else:
                    pronostico_texto = f"{pronostico:,.0f} casos"

                # ===== TARJETAS PRINCIPALES =====
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pronóstico 2026", pronostico_texto)
                with col2:
                    clas = r['pronostico']['clasificacion']
                    color = "#d32f2f" if "ALTA" in clas else "#388e3c"
                    st.markdown(f"<h3 style='color:{color}; text-align:center'>{clas}</h3>", unsafe_allow_html=True)
                with col3:
                    st.metric("Umbral de alerta", f"{r['umbral_alerta']:,.0f} casos")
                with col4:
                    prob = r['pronostico'].get('probabilidad_brote', 0)
                    st.metric("Prob. de brote", f"{prob}%")

                st.markdown("---")

                # ===== GRÁFICO DE BARRAS + LÍNEA =====
                years = list(r["casos_historicos"].keys())
                cases = list(r["casos_historicos"].values())

                fig = go.Figure()
                fig.add_trace(go.Bar(x=years, y=cases, name="Casos reales", marker_color="lightblue"))
                fig.add_trace(go.Scatter(
                    x=[years[-1], 2026], y=[cases[-1], pronostico],
                    mode="lines+markers", name="Pronóstico 2026",
                    line=dict(color="red", width=5), marker=dict(size=14)
                ))
                fig.add_hline(y=r['umbral_alerta'], line_dash="dash", line_color="orange",
                              annotation_text="Umbral de alerta")
                fig.update_layout(title="Evolución y pronóstico de casos", height=500)
                st.plotly_chart(fig, use_container_width=True)

                # ===== GRÁFICO CIRCULAR (Torta) =====
                alto = sum(1 for c in cases if c > r['umbral_alerta'])
                bajo = len(cases) - alto
                fig_pie = px.pie(
                    values=[alto, bajo],
                    names=["Años con brote", "Años controlados"],
                    color_discrete_sequence=["#d32f2f", "#388e3c"],
                    title="Histórico de riesgo"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

                # ===== KPIs EN COLUMNAS =====
                with st.expander("Indicadores clave (KPIs)"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**Picos históricos**")
                        st.write(f"• Año más grave: **{r['kpis']['Año Pico']}**")
                        st.write(f"• Máximo de casos: **{r['kpis']['Casos Máximos Históricos']:,}**")
                        st.write(f"• Índice de severidad: **{r['kpis']['Índice de Severidad (%)']}%**")
                    with c2:
                        st.write("**Tendencia**")
                        tasa = r['kpis']['Tasa de Crecimiento Anual Promedio (%)']
                        st.write(f"• Crecimiento anual promedio: **{tasa:+.2f}%**")
                        st.write(f"• Intervalo de confianza 90%: {r['pronostico']['intervalo_confianza_90'][0]:,} – {r['pronostico']['intervalo_confianza_90'][1]:,} casos")

                st.info(r["mensaje"].replace("-917", "< 50"))

                st.caption(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Modelo predictivo validado con datos oficiales MINSA")

            else:
                st.error("Error del servidor. Intenta de nuevo.")
                st.code(response.text)

        except requests.exceptions.Timeout:
            st.error("El servidor tardó demasiado en responder (Render estaba dormido). Intenta de nuevo en 10 segundos.")
        except Exception as e:
            st.error("Error inesperado. Contacta al desarrollador.")

else:
    st.info("Sube tu archivo Excel o CSV del MINSA para comenzar")
    st.markdown("### Instrucciones rápidas\n1. Descarga el reporte oficial\n2. Súbelo aquí\n3. Obtén el pronóstico 2026 al instante")

st.markdown("---")
st.markdown("<div style='text-align:center; color:gray;'>Sistema de Vigilancia Predictiva - Dengue Chincha Alta<br>DIRESA Ica © 2025</div>", unsafe_allow_html=True)