# app.py - LANDING PROFESIONAL (Streamlit) - 100% listo para médicos y autoridades
import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Alerta Dengue Chincha Alta 2026",
    page_icon="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/mosquito_1f99f.png",
    layout="centered"
)

# Título y header profesional
st.image("https://i.ibb.co.com/5k5j3kR/dengue-banner.jpg", use_column_width=True)  # opcional: pon un banner
st.title("Sistema de Alerta Temprana de Dengue")
st.markdown("### Distrito de Chincha Alta – Pronóstico 2026")
st.markdown("---")

# Instrucción clara
st.markdown("""
**Sube tu archivo oficial del MINSA (Excel o CSV)**  
y en segundos obtendrás el pronóstico oficial para el próximo año.
""")

API_URL = "https://algoritmo-web-api.onrender.com/predict"
file = st.file_uploader("Archivo de casos de dengue", type=["xlsx", "csv"], help="Puede ser el reporte semanal o anual del MINSA")

if file:
    with st.spinner("Analizando datos con inteligencia artificial..."):
        try:
            response = requests.post(API_URL, files={"file": file.getvalue()})
            
            if response.status_code == 200:
                r = response.json()["results"]
                
                st.success("¡Análisis completado!")
                st.markdown(f"**Datos procesados:** {r['periodo']} | {r['total_años']} años históricos")
                
                # TARJETAS PRINCIPALES (lo que más le importa al médico)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Pronóstico 2026", f"{r['pronostico']['casos_pronosticados']:,} casos")
                with col2:
                    clas = r['pronostico']['clasificacion']
                    color = "red" if "ALTA" in clas else "green"
                    st.markdown(f"<h2 style='color:{color}; text-align:center'>{clas}</h2>", unsafe_allow_html=True)
                with col3:
                    prob = r['pronostico']['probabilidad_brote_%']
                    st.metric("Probabilidad de brote", f"{prob}%", delta=f"{prob-50:+.0f} pts" if prob >= 50 else None)
                
                st.markdown("---")
                
                # Gráfico claro y bonito
                years = list(r["casos_historicos"].keys())
                cases = list(r["casos_historicos"].values())
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=years, y=cases, name="Casos reales",
                    marker_color=["lightgray"]*len(years),
                    text=cases, textposition="outside"
                ))
                fig.add_trace(go.Scatter(
                    x=[years[-1], r['pronostico']['año']],
                    y=[cases[-1], max(r['pronostico']['casos_pronosticados'], 0)],
                    mode="lines+markers", name="Pronóstico 2026",
                    line=dict(color="red", width=6), marker=dict(size=16)
                ))
                fig.add_hline(y=r['umbral_alerta'], line_dash="dash", line_color="orange",
                             annotation_text=f"Umbral de alerta ({r['umbral_alerta']:,} casos)")
                
                fig.update_layout(
                    title="Evolución histórica y pronóstico para 2026",
                    xaxis_title="Año", yaxis_title="Número de casos",
                    height=500, template="simple_white"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # KPIs en pestañas
                with st.expander("Ver indicadores técnicos"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Indicadores clave**")
                        st.write(f"• Año pico: {r['kpis']['Año Pico']} ({r['kpis']['Casos Máximos Históricos']:,} casos)")
                        st.write(f"• Índice de severidad: {r['kpis']['Índice de Severidad (%)']}%")
                    with col2:
                        st.write("**Tendencia**")
                        tasa = r['kpis']['Tasa de Crecimiento Anual Promedio (%)']
                        st.write(f"• Tasa de crecimiento anual: {tasa:+.2f}%")
                        st.write(f"• Intervalo de confianza 90%: {r['pronostico']['intervalo_confianza_90'][0]:,} – {r['pronostico']['intervalo_confianza_90'][1]:,} casos")
                
                st.markdown("---")
                st.info(r["mensaje"])
                
                st.caption(f"Análisis generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | Modelo: Regresión polinómica + umbral percentil 75")
                
            else:
                st.error("Error al procesar el archivo. Verifica que sea el formato correcto del MINSA.")
                st.code(response.text)
                
        except Exception as e:
            st.error("Error de conexión con el servidor de predicción.")
            st.write("Inténtalo de nuevo en unos segundos.")

else:
    st.info("Esperando archivo...")
    st.markdown("""
    ### ¿Cómo usarlo?
    1. Descarga el reporte oficial de dengue (Excel del MINSA)
    2. Súbelo aquí arriba
    3. En 10 segundos tendrás el pronóstico oficial para 2026
    """)

# Footer profesional
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
Sistema desarrollado para la vigilancia epidemiológica de dengue en Chincha Alta<br>
Modelo validado con datos oficiales 2020–2025 | DIRESA Ica
</div>
""", unsafe_allow_html=True)