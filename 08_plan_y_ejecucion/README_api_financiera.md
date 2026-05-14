# API FastAPI · Inteligencia Financiera Bancaria

## Objetivo

Esta API permite consultar el dataset financiero limpio y los resultados de modelos desde endpoints HTTP.

Trabaja sobre los archivos generados en:

```text
01_datos_procesados/
01_datos_procesados/modelos/
```

## Ubicación de archivos

Colocar el archivo principal en:

```text
02_scripts/api_financiera.py
```

## Instalación de dependencias

Agrega estas dependencias al `requirements.txt` o instálalas desde `requirements_api.txt`:

```bash
pip install -r requirements_api.txt
```

Contenido sugerido:

```text
fastapi==0.115.6
uvicorn==0.32.1
pydantic==2.10.4
```

También necesitas tener instaladas las dependencias del proyecto:

```text
pandas
numpy
pyarrow
```

## Ejecutar la API

Desde la raíz del proyecto `GRUPO_02`:

```bash
python -m uvicorn api_financiera:app --reload --app-dir 02_scripts
```

La API se abrirá en:

```text
http://127.0.0.1:8000
```

Documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

Documentación ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Endpoints principales

### Estado de la API

```http
GET /health
```

### Metadatos del dataset

```http
GET /financials/metadata
```

### Listar bancos

```http
GET /financials/banks
```

### Listar periodos

```http
GET /financials/periods
```

### Listar indicadores

```http
GET /financials/metrics
```

---

## Consultar KPIs de un banco

```http
GET /financials/bank?name=PICHINCHA
```

Con periodo específico:

```http
GET /financials/bank?name=PICHINCHA&period=2025-12
```

Devuelve todos los KPIs disponibles del banco para ese periodo.

---

## Consultar historial de un banco por indicador

```http
GET /financials/history?name=PICHINCHA&metric=roe
```

Con año:

```http
GET /financials/history?name=PICHINCHA&metric=assets&year=2025
```

Alias permitidos:

| Alias | Indicador real |
|---|---|
| `assets`, `activos` | `activos_totales` |
| `liabilities`, `pasivos` | `pasivos_totales` |
| `equity`, `patrimonio` | `patrimonio` |
| `roe` | `roe` |
| `morosidad`, `npl` | `morosidad` |
| `solvencia`, `solvency` | `solvencia_proxy` |

---

## Ranking por indicador

Ranking mensual, último periodo disponible:

```http
GET /financials/rank?metric=assets
```

Ranking mensual con periodo específico:

```http
GET /financials/rank?metric=roe&period=2025-12&top=10
```

Ranking anual promedio:

```http
GET /financials/rank?metric=morosidad&year=2025&top=10
```

> En morosidad, el ranking se ordena de menor a mayor porque menor morosidad es mejor.

---

## Promedio del sistema

```http
GET /financials/system-average?metric=roe&period=2025-12
```

O por año:

```http
GET /financials/system-average?metric=solvencia&year=2025
```

---

## Score inteligente de salud financiera

Requiere ejecutar previamente:

```text
03_cuadernos/04_score_salud_bancaria_v2.ipynb
```

Score de todos los bancos del último año:

```http
GET /financials/score
```

Score de un banco:

```http
GET /financials/score?name=PICHINCHA
```

Score por año:

```http
GET /financials/score?year=2020&top=10
```

---

## Proyecciones Prophet

Requiere ejecutar previamente:

```text
03_cuadernos/03_modelado_ml.ipynb
```

Forecast con histórico:

```http
GET /financials/forecast?name=PICHINCHA&metric=assets
```

Solo proyección futura:

```http
GET /financials/forecast?name=PICHINCHA&metric=morosidad&include_history=false
```

---

## Recargar caché

Si regeneras los archivos Parquet/CSV mientras la API está levantada, ejecuta:

```http
POST /admin/reload
```

Esto limpia la caché y obliga a la API a leer nuevamente los archivos.

## Estructura recomendada

```text
GRUPO_02/
├── 01_datos_procesados/
│   ├── dataset_financiero_limpio.parquet
│   └── modelos/
│       ├── score_salud_bancaria.parquet
│       └── prophet_forecast.parquet
│
├── 02_scripts/
│   ├── api_financiera.py
│   └── README_api_financiera.md
│
└── requirements_api.txt
```

## Nota metodológica

La API no recalcula modelos. Solo expone los resultados ya generados por notebooks.  
Esto mantiene la API rápida, simple y estable.
