from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import numpy as np
import statsmodels.api as sm
import io
import warnings
warnings.filterwarnings('ignore')

app = FastAPI(
    title="API Predictiva Dengue Chincha Alta",
    description="Sube tu archivo Excel o CSV del MINSA y obtén pronóstico 2026 + KPIs",
    version="2.0"
)

# Permitir que Streamlit (o cualquier frontend) llame a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
CONFIG = {
    'percentile_threshold': 75,
    'confidence_level': 0.90,
    'min_data_points': 4
}

# ==================== CARGA INTELIGENTE DE ARCHIVOS ====================
def load_dengue_data(file_content: bytes, filename: str) -> pd.Series:
    try:
        # Detectar si es Excel o CSV
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content), header=None)
        else:
            # Intentar varias codificaciones comunes en archivos del MINSA
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(io.BytesIO(file_content), header=None, encoding=encoding)
                    break
                except:
                    continue
            else:
                raise ValueError("No se pudo leer el CSV con ninguna codificación")

        # Buscar fila "Casos totales"
        mask = df.iloc[:, 0].astype(str).str.contains('Casos totales', case=False, na=False)
        if not mask.any():
            raise ValueError("No se encontró la fila 'Casos totales'")

        row_index = mask.idxmax()

        # Extraer años desde la primera fila
        years = []
        for i in range(1, df.shape[1]):
            val = df.iloc[0, i]
            try:
                year = int(val)
                if 2000 <= year <= 2100:
                    years.append(year)
                else:
                    break
            except:
                break

        if len(years) < CONFIG['min_data_points']:
            raise ValueError(f"No se encontraron suficientes años válidos (mínimo {CONFIG['min_data_points']})")

        # Extraer casos
        cases_raw = df.iloc[row_index, 1:1+len(years)]
        cases = pd.to_numeric(cases_raw, errors='coerce')
        series = pd.Series(cases.values, index=years).dropna()

        if len(series) < CONFIG['min_data_points']:
            raise ValueError(f"Solo {len(series)} años tienen datos válidos")

        return series

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar archivo: {str(e)}")


# ==================== MODELOS Y PREDICCIÓN ====================
def fit_polynomial_model(years, cases, degree=2):
    X = np.column_stack([years**i for i in range(1, degree + 1)])
    X = sm.add_constant(X)
    return sm.OLS(cases, X).fit()

def predict_with_confidence(model, next_year, degree=2):
    if degree == 1:
        X_pred = np.array([[1, next_year]])
    else:
        X_pred = np.array([[1] + [next_year**i for i in range(1, degree + 1)]])
    pred = model.get_prediction(X_pred)
    forecast = pred.predicted_mean[0]
    ci = pred.conf_int(alpha=1-CONFIG['confidence_level'])[0]
    return forecast, ci[0], ci[1]

def calculate_dynamic_threshold(cases_series):
    return np.percentile(cases_series, CONFIG['percentile_threshold'])

def run_analysis(cases_series: pd.Series) -> Dict[str, Any]:
    threshold = calculate_dynamic_threshold(cases_series)
    next_year = int(cases_series.index.max()) + 1

    # Modelo final con todos los datos
    model = fit_polynomial_model(cases_series.index.values, cases_series.values, degree=2)
    forecast, ci_low, ci_high = predict_with_confidence(model, next_year, degree=2)
    pred_class = 1 if forecast > threshold else 0

    # KPIs nuevos
    if len(cases_series) > 1:
        growth_rate = ((cases_series.iloc[-1] / cases_series.iloc[0]) ** (1/(len(cases_series)-1)) - 1) * 100
    else:
        growth_rate = 0
    severity_index = (cases_series.max() / cases_series.mean()) * 100 if cases_series.mean() > 0 else 0
    outbreak_prob = 100 if ci_high > threshold else 0

    return {
        "periodo": f"{cases_series.index.min()}-{cases_series.index.max()}",
        "total_años": len(cases_series),
        "casos_historicos": cases_series.to_dict(),
        "umbral_alerta": round(threshold, 2),
        "pronostico": {
            "año": next_year,
            "casos_pronosticados": round(forecast, 0),
            "intervalo_confianza_90": [round(ci_low, 0), round(ci_high, 0)],
            "clasificacion": "ALTA INCIDENCIA" if pred_class else "BAJA INCIDENCIA",
            "probabilidad_brote": round(outbreak_prob, 1)
        },
        "kpis": {
            "Tasa de Crecimiento Anual Promedio (%)": round(growth_rate, 2),
            "Índice de Severidad (%)": round(severity_index, 1),
            "Casos Máximos Históricos": int(cases_series.max()),
            "Año Pico": int(cases_series.idxmax())
        },
        "mensaje": f"Pronóstico {next_year}: {int(forecast)} casos → {'ALERTA TEMPRANA' if pred_class else 'Bajo riesgo'}"
    }


# ==================== ENDPOINTS ====================
class PredictionResponse(BaseModel):
    results: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "API Predictiva Dengue Chincha Alta - Sube un archivo a /predict"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_dengue(file: UploadFile = File(...)):
    content = await file.read()
    cases_series = load_dengue_data(content, file.filename)
    results = run_analysis(cases_series)
    return PredictionResponse(results=results)