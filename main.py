# main.py - API FastAPI para predicción de dengue
import io  # Para leer CSV en memoria
import pandas as pd
import numpy as np
import statsmodels.api as sm
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Para que Streamlit lo llame
from pydantic import BaseModel
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

app = FastAPI(title="API Predictiva Dengue Chincha Alta")

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, restringe a tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tu CONFIG original (adaptada)
CONFIG = {
    'percentile_threshold': 75,
    'confidence_level': 0.90,
    'min_data_points': 4
}

# Tus funciones originales (copia-pega aquí: load_dengue_data, calculate_dynamic_threshold, etc.)
# ... (Incluye TODAS las funciones de tu script: fit_*, predict_*, rolling_validation, calculate_metrics, etc.)
# Para brevidad, asumo que las pegas. Cambia load_dengue_data para CSV:

def load_dengue_data_from_csv(csv_content: bytes) -> pd.Series:
    """Adaptada para CSV en memoria (formato: fila1=años, fila2=Casos totales + valores)"""
    try:
        df = pd.read_csv(io.StringIO(csv_content.decode('utf-8')), header=None)
        
        # Buscar fila "Casos totales"
        mask = df.iloc[:, 0].astype(str).str.contains('Casos totales', case=False, na=False)
        if not mask.any():
            raise ValueError("No se encontró la fila 'Casos totales' en el CSV")
        
        row_index = mask.idxmax()
        
        # Extraer años (fila 0, cols 1+)
        years = []
        for i in range(1, df.shape[1]):
            try:
                year = int(df.iloc[0, i])
                if 2000 <= year <= 2100:
                    years.append(year)
                else:
                    break
            except (ValueError, TypeError):
                break
        
        # Extraer casos
        cases = pd.to_numeric(df.iloc[row_index, 1:1+len(years)], errors='coerce').tolist()
        cases_series = pd.Series(cases, index=years).dropna()
        
        if len(cases_series) < CONFIG['min_data_points']:
            raise ValueError(f"Datos insuficientes: {len(cases_series)} años")
        
        return cases_series
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al cargar CSV: {str(e)}")

# Función principal adaptada (devuelve JSON)
def run_analysis(cases_series: pd.Series) -> Dict[str, Any]:
    threshold = calculate_dynamic_threshold(cases_series, method='percentile')
    validation_results = rolling_validation(cases_series, threshold, model_type='polynomial')
    next_year = cases_series.index.max() + 1
    future_prediction = predict_future_year(cases_series, next_year, threshold, model_type='polynomial')
    metrics = calculate_metrics(validation_results)
    efficiency_metrics = measure_computational_efficiency(validation_results, validation_results.get('execution_times', []))
    final_model = future_prediction['model']
    feature_names = ['Intercepto', 'Año', 'Año²']
    interpretability_metrics = analyze_model_interpretability(final_model, feature_names)
    
    # KPIs nuevos (basados en tus datos)
    growth_rate = ((cases_series.iloc[-1] / cases_series.iloc[0]) ** (1 / (len(cases_series) - 1)) - 1) * 100 if len(cases_series) > 1 else 0
    outbreak_prob = 100 if future_prediction['ci_upper'] > threshold else 0  # % si IC superior > umbral
    severity_index = (cases_series.max() / cases_series.mean()) * 100 if cases_series.mean() > 0 else 0
    early_alert_coverage = (sum([1 for i in range(len(validation_results['actual_class'])) if validation_results['pred_class'][i] == 1 and validation_results['actual_class'][i] == 1]) / max(len(validation_results['actual_class']), 1)) * 100
    
    kpis = {
        'Tasa Crecimiento Anual Promedio (%)': round(growth_rate, 2),
        'Probabilidad Brote 2026 (%)': round(outbreak_prob, 2),
        'Índice de Severidad (%)': round(severity_index, 2),
        'Cobertura Alerta Temprana (%)': round(early_alert_coverage, 2)
    }
    
    # Datos para gráficos (JSON serializable)
    trend_data = {
        'historical': {'years': cases_series.index.tolist(), 'cases': cases_series.tolist()},
        'validation': {'years': validation_results['years'], 'forecast': validation_results['forecast']},
        'future': {'year': [next_year], 'forecast': [future_prediction['forecast']]}
    }
    
    return {
        'threshold': threshold,
        'future_prediction': future_prediction,
        'metrics': metrics,
        'kpis': kpis,
        'trend_data': trend_data,
        'summary': f"Predicción {next_year}: {future_prediction['forecast']:.0f} casos (Clase: {'Alta' if future_prediction['pred_class'] == 1 else 'Baja'})"
    }

# Modelo Pydantic para respuesta
class AnalysisResponse(BaseModel):
    results: Dict[str, Any]

# Endpoint principal
@app.post("/predict", response_model=AnalysisResponse)
async def predict_dengue(file: UploadFile = File(...)):
    # Aceptamos tanto .csv como .xlsx
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Solo archivos CSV o Excel (.xlsx) permitidos")
    
    content = await file.read()
    cases_series = load_dengue_data_from_csv(content)
    results = run_analysis(cases_series)
    
    return AnalysisResponse(results=results)

# Endpoint de prueba (para docs)
@app.get("/")
async def root():
    return {"message": "API Predictiva Dengue Chincha Alta - Sube un CSV a /predict"}

# Para correr local: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)