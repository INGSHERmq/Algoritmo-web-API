# app.py - Frontend Streamlit
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# Config
API_URL = "http://localhost:8000/predict"  # Cambia a tu URL de Render después

st.set_page_config(page_title="Predictor Dengue Chincha Alta", layout="wide")

st.title("🔬 Predictor Visual de Incidencia de Dengue - Chincha Alta")
st.markdown("Sube tu CSV con datos de casos (formato: fila1=años, fila2=Casos totales) para ver predicciones, gráficos y KPIs.")

# Upload
uploaded_file = st.file_uploader("Elige un archivo CSV", type="csv")

if uploaded_file is not None:
    with st.spinner("Procesando... Enviando a API..."):
        files = {'file': uploaded_file.getvalue()}
        response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            results = response.json()['results']
            
            # KPIs en columnas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Umbral Alerta", f"{results['threshold']:.0f} casos")
            with col2:
                st.metric("Predicción 2026", f"{results['future_prediction']['forecast']:.0f} casos")
            with col3:
                st.metric("Clasificación", "🟢 Baja" if results['future_prediction']['pred_class'] == 0 else "🔴 Alta")
            with col4:
                st.metric("Sensibilidad", f"{results['metrics'].get('Sensibilidad (Recall)', 0):.1f}%")
            
            # KPIs nuevos en expander
            with st.expander("KPIs Avanzados"):
                kpi_df = pd.DataFrame(list(results['kpis'].items()), columns=['KPI', 'Valor'])
                st.dataframe(kpi_df, use_container_width=True)
            
            # Gráfico de tendencia (usando Plotly)
            trend_data = results['trend_data']
            fig = go.Figure()
            
            # Histórico
            fig.add_trace(go.Scatter(x=trend_data['historical']['years'], y=trend_data['historical']['cases'],
                                     mode='lines+markers', name='Casos Reales', line=dict(color='blue')))
            
            # Validación
            if trend_data['validation']['years']:
                fig.add_trace(go.Scatter(x=trend_data['validation']['years'], y=trend_data['validation']['forecast'],
                                         mode='lines+markers', name='Predicciones', line=dict(color='orange', dash='dash')))
            
            # Futuro
            fig.add_trace(go.Scatter(x=trend_data['future']['year'], y=trend_data['future']['forecast'],
                                     mode='markers', name='Pronóstico 2026', marker=dict(size=15, color='red')))
            
            # Umbral
            fig.add_hline(y=results['threshold'], line_dash="dot", line_color="red", annotation_text="Umbral Alerta")
            
            fig.update_layout(title="Tendencia de Casos de Dengue", xaxis_title="Año", yaxis_title="Casos",
                              height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de torta (proporción riesgo)
            classes = [1 if c > results['threshold'] else 0 for c in trend_data['historical']['cases']]
            high_risk = sum(classes)
            low_risk = len(classes) - high_risk
            fig_pie = px.pie(values=[high_risk, low_risk], names=['Alta Incidencia', 'Baja Incidencia'],
                             title="Proporción de Años de Riesgo")
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Métricas en tabla
            metrics_df = pd.DataFrame(list({k: v for k, v in results['metrics'].items() if isinstance(v, (int, float))}.items()),
                                      columns=['Métrica', 'Valor'])
            st.subheader("Métricas de Precisión")
            st.dataframe(metrics_df, use_container_width=True)
            
            st.success(results['summary'])
        else:
            st.error(f"Error en API: {response.text}")
else:
    st.info("👆 Sube un CSV para empezar el análisis.")