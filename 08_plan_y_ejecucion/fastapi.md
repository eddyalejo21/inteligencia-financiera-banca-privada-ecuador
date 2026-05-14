# API FastAPI

## Objetivo

Exponer el dataset financiero limpio y los resultados de modelos mediante endpoints HTTP.

Archivo principal:

```text
02_scripts/api_financiera.py
```

---

## Ejecución

Desde la raíz del proyecto:

```bash
python -m uvicorn api_financiera:app --reload --app-dir 02_scripts
```

La API queda disponible en:

```text
http://127.0.0.1:8000
```

Documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## Datasets utilizados

Dataset principal:

```text
01_datos_procesados/dataset_financiero_limpio.parquet
```

Resultados de modelos:

```text
01_datos_procesados/modelos/
```

La API no recalcula modelos. Solo expone resultados previamente generados.

---

## Endpoints principales

### Estado de API

```http
GET /health
```

Valida que el dataset principal se pueda cargar correctamente.

---

### Metadatos

```http
GET /financials/metadata
```

Devuelve:

- cantidad de filas;
- bancos;
- periodos;
- indicadores;
- periodo mínimo;
- periodo máximo.

---

### Bancos

```http
GET /financials/banks
```

Lista los bancos disponibles.

---

### Periodos

```http
GET /financials/periods
```

Lista periodos y años disponibles.

---

### Indicadores

```http
GET /financials/metrics
```

Lista indicadores y alias permitidos.

---

### KPIs de un banco

```http
GET /financials/bank?name=PICHINCHA
```

Con periodo:

```http
GET /financials/bank?name=PICHINCHA&period=2025-12
```

---

### Historial de un indicador

```http
GET /financials/history?name=PICHINCHA&metric=roe
```

Con año:

```http
GET /financials/history?name=PICHINCHA&metric=assets&year=2025
```

---

### Ranking

```http
GET /financials/rank?metric=assets
```

Con periodo:

```http
GET /financials/rank?metric=roe&period=2025-12&top=10
```

Con año:

```http
GET /financials/rank?metric=morosidad&year=2025&top=10
```

---

### Promedio del sistema

```http
GET /financials/system-average?metric=roe&period=2025-12
```

---

### Score inteligente

```http
GET /financials/score
```

Por banco:

```http
GET /financials/score?name=PICHINCHA
```

Por año:

```http
GET /financials/score?year=2020&top=10
```

---

### Proyecciones Prophet

```http
GET /financials/forecast?name=PICHINCHA&metric=assets
```

Solo proyección:

```http
GET /financials/forecast?name=PICHINCHA&metric=morosidad&include_history=false
```

---

### Recargar caché

```http
POST /admin/reload
```

Permite limpiar caché si se regeneran los archivos Parquet/CSV.

---

## Resultado

La API permite consumir el sistema desde otras aplicaciones, dashboards o servicios.

Con esto el proyecto queda con una arquitectura completa:

```text
Excel crudo
    ↓
Pipeline de limpieza
    ↓
Dataset limpio
    ↓
EDA + Modelos ML + Score
    ↓
Dashboard Streamlit
    ↓
API FastAPI
```
