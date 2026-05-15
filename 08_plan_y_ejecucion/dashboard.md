# Dashboard Streamlit

## Objetivo

Construir una interfaz interactiva para explorar, comparar y analizar el desempeño financiero de los bancos privados ecuatorianos.

Archivo principal:

```text
02_scripts/app_dashboard.py
```

---

## Dataset utilizado

```text
01_datos_procesados/dataset_financiero_limpio.parquet
```

y resultados de modelos ubicados en:

```text
01_datos_procesados/modelos/
```

---

## Ejecución

Desde la raíz del proyecto:

```bash
streamlit run 02_scripts/app_dashboard.py
```

---

## Pestañas principales

### 1. Banco vs Sistema

Permite seleccionar:

- banco;
- KPI;
- año.

Muestra:

- valor del banco;
- promedio del sistema;
- ranking;
- variación anual;
- gráfico mensual enero-diciembre;
- evolución histórica anual banco vs sistema.

---

### 2. Ranking

Permite visualizar rankings por KPI.

Incluye:

- selección de indicador;
- selección de año;
- Top N configurable;
- barras horizontales;
- evolución anual del indicador;
- evolución histórica del ranking.

---

### 3. Riesgo financiero

Cruza indicadores financieros para identificar señales relativas de riesgo.

Visualización principal:

```text
Morosidad vs Solvencia proxy
```

con:

- tamaño por activos;
- color por ROE;
- líneas de promedio del sistema.

---

### 4. Tabla comparativa

Incluye:

- tabla interactiva y ordenable;
- todos los bancos simultáneamente;
- heatmap normalizado;
- comparación por año.

---

### 5. Modelo ROE

Muestra resultados del modelo `RandomForestRegressor`.

Incluye:

- métricas MAE, RMSE y R²;
- gráfico ROE real vs ROE estimado;
- importancia de variables;
- bancos/periodos con mayor diferencia.

---

### 6. Clusters KMeans

Muestra segmentación bancaria.

Incluye:

- gráfico PCA 2D;
- bancos coloreados por cluster;
- resumen de perfiles;
- tabla de bancos segmentados;
- evolución histórica del cluster de un banco.

---

### 7. Proyecciones Prophet

Muestra proyecciones exploratorias por:

```text
banco + indicador
```

Incluye:

- serie histórica;
- forecast;
- banda de incertidumbre;
- métricas de ajuste;
- últimos valores históricos y proyectados.

---

### 8. Score inteligente

Muestra el score de salud financiera.

Incluye:

- filtro por año;
- filtro por banco;
- gauge del score;
- ranking Top N;
- componentes del score;
- evolución histórica del score;
- lectura ejecutiva automática.

---

## Decisiones de diseño

- No se utilizaron gráficos de pastel.
- Se priorizaron barras, líneas, scatter, heatmap y gauge.
- Los valores monetarios se muestran en millones de USD.
- Los porcentajes se muestran como valores directos.
- El score se presenta como herramienta exploratoria, no como calificación oficial.

---

## Resultado

El dashboard permite responder preguntas de negocio como:

- ¿Qué bancos lideran por activos?
- ¿Qué bancos tienen mejor ROE?
- ¿Qué bancos presentan menor morosidad?
- ¿Qué bancos tienen mejor solvencia proxy?
- ¿Qué bancos muestran mejor salud financiera según el score?
- ¿Cómo se proyecta el comportamiento futuro de un banco?
