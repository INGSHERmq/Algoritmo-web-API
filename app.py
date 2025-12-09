import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Configuración de página con tema personalizado
st.set_page_config(
    page_title="Alerta Dengue Chincha Alta 2026", 
    layout="wide", 
    page_icon="🦟",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    /* Fondo sólido claro para mejor legibilidad */
    .stApp {
        background: #f8fafc;
    }
    
    /* Tarjetas con sombra y bordes redondeados */
    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Título principal */
    h1 {
        color: #1e3a8a;
        text-align: center;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Subtítulos */
    h3 {
        color: #475569;
    }
    
    /* Botones y elementos interactivos */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        border: none;
        font-weight: 600;
    }
    
    /* Área de carga de archivos con fondo blanco */
    .uploadedFile {
        background: white !important;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Mejorar contraste en elementos de Streamlit */
    .stFileUploader label {
        color: #1e3a8a !important;
        font-weight: 600 !important;
    }
    
    /* Tabs con mejor contraste */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: #1e3a8a !important;
        background-color: #e0f2fe !important;
        border-radius: 8px;
    }
    
    /* Información destacada */
    .info-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    /* Tarjeta de alerta */
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(238, 90, 111, 0.4);
    }
    
    /* Tarjeta de éxito */
    .success-card {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(55, 178, 77, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Header con diseño mejorado
col_logo1, col_title, col_logo2 = st.columns([1, 3, 1])
with col_title:
    st.markdown("<h1>🦟 Sistema de Alerta Temprana de Dengue</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#64748b;'>Chincha Alta – Pronóstico 2026</h3>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Instrucciones en una caja destacada
with st.container():
    st.markdown("""
    <div class='info-box'>
        <h4 style='margin-top:0; color:#1e40af;'>📊 ¿Cómo usar el sistema?</h4>
        <ol style='color:#475569; line-height:1.8;'>
            <li><b>Descarga</b> el reporte oficial del MINSA (formato Excel o CSV)</li>
            <li><b>Sube</b> el archivo en el campo inferior</li>
            <li><b>Obtén</b> el análisis predictivo completo en segundos</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

API_URL = "https://algoritmo-web-api.onrender.com/predict"

# Área de carga de archivo con mejor diseño y contraste
st.markdown("""
<div style='background:white; padding:20px; border-radius:15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom:30px;'>
    <h4 style='color:#1e3a8a; margin-bottom:15px;'>📁 Cargar datos oficiales</h4>
</div>
""", unsafe_allow_html=True)

file = st.file_uploader(
    "Selecciona el archivo de casos de dengue", 
    type=["xlsx", "csv"],
    help="Formatos aceptados: Excel (.xlsx) o CSV (.csv)",
    label_visibility="collapsed"
)

if file:
    with st.spinner("🔄 Despertando el modelo y analizando datos... (puede tardar 20-40 segundos la primera vez)"):
        try:
            files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
            response = requests.post(API_URL, files=files, timeout=120)

            if response.status_code == 200:
                r = response.json()["results"]

                st.balloons()
                st.success("✅ ¡Análisis completado con éxito!")
                
                # Información del período
                st.markdown(f"""
                <div style='text-align:center; padding:15px; background:white; border-radius:10px; margin:20px 0;'>
                    <span style='font-size:18px; color:#475569;'>
                        📅 <b>Período analizado:</b> {r['periodo']} | 
                        📊 <b>Datos históricos:</b> {r['total_años']} años
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Corregir casos negativos
                pronostico = max(r['pronostico']['casos_pronosticados'], 0)
                if pronostico == 0:
                    pronostico_texto = "< 50 casos"
                    pronostico_display = "Baja actividad"
                else:
                    pronostico_texto = f"{pronostico:,.0f}"
                    pronostico_display = f"{pronostico:,.0f} casos"

                # Tarjetas principales con diseño mejorado
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding:25px; border-radius:15px; text-align:center; color:white;
                                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);'>
                        <div style='font-size:14px; opacity:0.9; margin-bottom:8px;'>PRONÓSTICO 2026</div>
                        <div style='font-size:32px; font-weight:700;'>{pronostico_texto}</div>
                        <div style='font-size:12px; opacity:0.8; margin-top:5px;'>{pronostico_display if pronostico > 0 else 'esperados'}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    clas = r['pronostico']['clasificacion']
                    is_high = "ALTA" in clas
                    bg_color = "linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)" if is_high else "linear-gradient(135deg, #51cf66 0%, #37b24d 100%)"
                    icon = "⚠️" if is_high else "✅"
                    st.markdown(f"""
                    <div style='background:{bg_color}; 
                                padding:25px; border-radius:15px; text-align:center; color:white;
                                box-shadow: 0 4px 12px rgba(238, 90, 111, 0.4);'>
                        <div style='font-size:14px; opacity:0.9; margin-bottom:8px;'>CLASIFICACIÓN</div>
                        <div style='font-size:28px; font-weight:700;'>{icon} {clas}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                                padding:25px; border-radius:15px; text-align:center; color:white;
                                box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);'>
                        <div style='font-size:14px; opacity:0.9; margin-bottom:8px;'>UMBRAL DE ALERTA</div>
                        <div style='font-size:32px; font-weight:700;'>{r['umbral_alerta']:,.0f}</div>
                        <div style='font-size:12px; opacity:0.8; margin-top:5px;'>casos</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    prob = r['pronostico'].get('probabilidad_brote', 0)
                    prob_color = "#dc2626" if prob > 60 else "#f59e0b" if prob > 30 else "#16a34a"
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); 
                                padding:25px; border-radius:15px; text-align:center; color:white;
                                box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);'>
                        <div style='font-size:14px; opacity:0.9; margin-bottom:8px;'>PROB. DE BROTE</div>
                        <div style='font-size:32px; font-weight:700;'>{prob}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br><br>", unsafe_allow_html=True)

                # Gráficos en pestañas
                tab1, tab2, tab3 = st.tabs(["📈 Evolución y Pronóstico", "🥧 Análisis de Riesgo", "📊 Indicadores Clave"])
                
                with tab1:
                    years = list(r["casos_historicos"].keys())
                    cases = list(r["casos_historicos"].values())

                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=years, y=cases, name="Casos reales",
                        marker_color='rgba(99, 110, 250, 0.7)',
                        hovertemplate='<b>Año %{x}</b><br>Casos: %{y:,.0f}<extra></extra>'
                    ))
                    fig.add_trace(go.Scatter(
                        x=[years[-1], 2026], y=[cases[-1], pronostico],
                        mode="lines+markers", name="Pronóstico 2026",
                        line=dict(color="#ef4444", width=4, dash='dash'),
                        marker=dict(size=16, color='#dc2626', line=dict(color='white', width=2)),
                        hovertemplate='<b>Año %{x}</b><br>Pronóstico: %{y:,.0f}<extra></extra>'
                    ))
                    fig.add_hline(
                        y=r['umbral_alerta'], line_dash="dot", line_color="#f59e0b",
                        annotation_text="⚠️ Umbral de alerta", annotation_position="right"
                    )
                    fig.update_layout(
                        title={
                            'text': "Evolución Histórica y Pronóstico de Casos de Dengue",
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 20, 'color': '#1e3a8a', 'family': 'Arial Black'}
                        },
                        height=550,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='white',
                        xaxis_title="Año",
                        yaxis_title="Número de Casos",
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    alto = sum(1 for c in cases if c > r['umbral_alerta'])
                    bajo = len(cases) - alto
                    
                    fig_pie = px.pie(
                        values=[alto, bajo],
                        names=["Años con brote", "Años controlados"],
                        color_discrete_sequence=["#ef4444", "#22c55e"],
                        title="Distribución Histórica de Riesgo",
                        hole=0.4
                    )
                    fig_pie.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        textfont_size=14,
                        marker=dict(line=dict(color='white', width=3))
                    )
                    fig_pie.update_layout(
                        title={
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 20, 'color': '#1e3a8a', 'family': 'Arial Black'}
                        },
                        height=500,
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Estadísticas adicionales
                    col_stat1, col_stat2 = st.columns(2)
                    with col_stat1:
                        porcentaje_brote = (alto / len(cases)) * 100
                        st.markdown(f"""
                        <div style='background:white; padding:20px; border-radius:10px; border-left:5px solid #ef4444;'>
                            <h4 style='color:#dc2626; margin:0;'>🔴 Años con brote</h4>
                            <p style='font-size:32px; font-weight:700; color:#1e3a8a; margin:10px 0;'>{alto} años</p>
                            <p style='color:#64748b;'>{porcentaje_brote:.1f}% del período analizado</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_stat2:
                        porcentaje_control = (bajo / len(cases)) * 100
                        st.markdown(f"""
                        <div style='background:white; padding:20px; border-radius:10px; border-left:5px solid #22c55e;'>
                            <h4 style='color:#16a34a; margin:0;'>🟢 Años controlados</h4>
                            <p style='font-size:32px; font-weight:700; color:#1e3a8a; margin:10px 0;'>{bajo} años</p>
                            <p style='color:#64748b;'>{porcentaje_control:.1f}% del período analizado</p>
                        </div>
                        """, unsafe_allow_html=True)

                with tab3:
                    col_kpi1, col_kpi2 = st.columns(2)
                    
                    with col_kpi1:
                        st.markdown("""
                        <div style='background:white; padding:25px; border-radius:15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color:#1e3a8a; border-bottom:3px solid #3b82f6; padding-bottom:10px;'>
                                📍 Picos Históricos
                            </h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='background:white; padding:15px; margin-top:-15px; border-radius:0 0 15px 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <p style='font-size:16px; color:#475569; line-height:2;'>
                                🔸 <b>Año más grave:</b> <span style='color:#dc2626; font-weight:700;'>{r['kpis']['Año Pico']}</span><br>
                                🔸 <b>Casos máximos:</b> <span style='color:#dc2626; font-weight:700;'>{r['kpis']['Casos Máximos Históricos']:,}</span><br>
                                🔸 <b>Índice de severidad:</b> <span style='color:#f59e0b; font-weight:700;'>{r['kpis']['Índice de Severidad (%)']}%</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_kpi2:
                        tasa = r['kpis']['Tasa de Crecimiento Anual Promedio (%)']
                        tasa_color = "#dc2626" if tasa > 0 else "#16a34a"
                        tasa_icon = "📈" if tasa > 0 else "📉"
                        st.markdown(f"""
                        <div style='background:white; padding:25px; border-radius:15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color:#1e3a8a; border-bottom:3px solid #3b82f6; padding-bottom:10px;'>
                                📊 Tendencia
                            </h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='background:white; padding:15px; margin-top:-15px; border-radius:0 0 15px 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <p style='font-size:16px; color:#475569; line-height:2;'>
                                {tasa_icon} <b>Crecimiento anual:</b> <span style='color:{tasa_color}; font-weight:700;'>{tasa:+.2f}%</span><br>
                                🔸 <b>Intervalo de confianza 90%:</b><br>
                                <span style='color:#475569; font-weight:600;'>{r['pronostico']['intervalo_confianza_90'][0]:,} – {r['pronostico']['intervalo_confianza_90'][1]:,} casos</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                # Mensaje final con diseño mejorado
                mensaje_limpio = r["mensaje"].replace("-917", "< 50")
                if "ALTA" in r['pronostico']['clasificacion']:
                    st.markdown(f"""
                    <div class='alert-card'>
                        <h3 style='margin:0 0 15px 0;'>⚠️ ALERTA DE RIESGO ALTO</h3>
                        <p style='font-size:16px; line-height:1.6; margin:0;'>{mensaje_limpio}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='success-card'>
                        <h3 style='margin:0 0 15px 0;'>✅ RIESGO CONTROLADO</h3>
                        <p style='font-size:16px; line-height:1.6; margin:0;'>{mensaje_limpio}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Footer con timestamp
                st.markdown(f"""
                <div style='text-align:center; padding:20px; margin-top:30px; color:#64748b; background:white; border-radius:10px;'>
                    <small>📅 Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
                    🤖 Modelo predictivo validado con datos oficiales MINSA</small>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("❌ Error del servidor. Por favor, intenta de nuevo.")
                with st.expander("Ver detalles del error"):
                    st.code(response.text)

        except requests.exceptions.Timeout:
            st.warning("⏱️ El servidor tardó demasiado en responder (Render estaba inactivo). Por favor, intenta de nuevo en 10 segundos.")
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            st.info("💡 Contacta al desarrollador si el problema persiste.")

else:
    # Pantalla de bienvenida mejorada
    st.markdown("""
    <div style='background:white; padding:40px; border-radius:20px; text-align:center; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin:40px 0;'>
        <div style='font-size:80px; margin-bottom:20px;'>📤</div>
        <h3 style='color:#1e3a8a; margin-bottom:15px;'>Sube tu archivo para comenzar</h3>
        <p style='color:#64748b; font-size:16px; line-height:1.8;'>
            Arrastra y suelta tu archivo Excel o CSV del MINSA<br>
            o haz clic en el botón de arriba para seleccionarlo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Características del sistema
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        st.markdown("""
        <div style='background:white; padding:25px; border-radius:15px; text-align:center; 
                    box-shadow: 0 2px 6px rgba(0,0,0,0.08); height:200px;'>
            <div style='font-size:50px; margin-bottom:15px;'>⚡</div>
            <h4 style='color:#1e3a8a; margin-bottom:10px;'>Análisis Rápido</h4>
            <p style='color:#64748b; font-size:14px;'>Resultados en menos de 1 minuto</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_feat2:
        st.markdown("""
        <div style='background:white; padding:25px; border-radius:15px; text-align:center; 
                    box-shadow: 0 2px 6px rgba(0,0,0,0.08); height:200px;'>
            <div style='font-size:50px; margin-bottom:15px;'>🎯</div>
            <h4 style='color:#1e3a8a; margin-bottom:10px;'>Alta Precisión</h4>
            <p style='color:#64748b; font-size:14px;'>Modelo validado con datos oficiales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_feat3:
        st.markdown("""
        <div style='background:white; padding:25px; border-radius:15px; text-align:center; 
                    box-shadow: 0 2px 6px rgba(0,0,0,0.08); height:200px;'>
            <div style='font-size:50px; margin-bottom:15px;'>📊</div>
            <h4 style='color:#1e3a8a; margin-bottom:10px;'>Visualización Clara</h4>
            <p style='color:#64748b; font-size:14px;'>Gráficos interactivos y KPIs</p>
        </div>
        """, unsafe_allow_html=True)

# Footer final
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; padding:30px; background:white; border-radius:15px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
    <h4 style='color:#1e3a8a; margin-bottom:10px;'>🏥 Sistema de Vigilancia Predictiva</h4>
    <p style='color:#64748b; margin:0;'>Dengue Chincha Alta • DIRESA Ica © 2025</p>
</div>
""", unsafe_allow_html=True)