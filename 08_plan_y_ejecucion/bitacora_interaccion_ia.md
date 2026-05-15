# Bitácora de interacción con IA

**Proyecto:** Ciencia de Datos Seminario 2026  
**Usuario:** Eddy Trejo  
**IA:** ChatGPT GPT-5.5 Thinking  
**Formato solicitado:** fecha de consulta, nombre del usuario, nombre de la IA, prompt resumido, salida aceptada, salida rechazada o corregida y verificador.

---

---

## Criterio de selección

Esta bitácora no incluye todas las preguntas realizadas durante el proyecto.  
Se registran únicamente las interacciones que tuvieron impacto directo en:

- extracción y preparación de datos;
- calidad del dataset final;
- definición de indicadores financieros;
- construcción del EDA;
- creación del dashboard;
- implementación de modelos de Machine Learning;
- construcción del score inteligente;
- creación de la API FastAPI;
- despliegue y configuración del proyecto.

---

## Bitácora consolidada de consultas validadas

| Fecha de la consulta | Nombre | Nombre de la IA | Prompt resumido | Salida que aceptamos | Salida que rechazamos o corregimos | Quién verificó |
|---|---|---|---|---|---|---|
| 2026-04-27 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Analizar un boletín Excel de bancos privados para identificar hojas, celdas e indicadores importantes: activos, ROE, morosidad y solvencia. | Se identificaron hojas clave como `BALANCE`, `INDICADORES`, `RK` y `COMPOS CART`; se explicó la función financiera de activos, ROE, morosidad y solvencia. | Se corrigió la interpretación inicial de solvencia porque el archivo no contenía una celda literal llamada `Índice de Solvencia`; se planteó trabajar con indicadores proxy disponibles. | Vinicio Morales |
| 2026-04-27 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Cambiar la búsqueda de ROE, morosidad y solvencia para que use códigos de indicadores y no únicamente nombres textuales. | Se aceptó el enfoque de búsqueda por código como primera opción para reducir errores por variación de nombres entre archivos. | Se descartó depender solo de nombres textuales porque los boletines tenían etiquetas variables entre periodos. | Misael Valarezo |
| 2026-04-28 | Vinicio Morales | ChatGPT GPT-5.5 Thinking | Extraer la fecha del periodo únicamente desde la hoja `Balance` o desde una hoja con cabecera `ESTADO DE SITUACIÓN`. | Se aceptó que el periodo se obtenga desde la fuente oficial del boletín y se normalice a formato `YYYY-MM`. | Se corrigió la estrategia anterior que podía tomar fechas desde hojas no autorizadas o desde el nombre del archivo. | Eddy Trejo |
| 2026-04-28 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Construir el dataset final en formato largo con activos, pasivos, patrimonio, ROE, morosidad y solvencia. | Se aceptó la estructura `periodo`, `banco_estandarizado`, `indicador`, `valor`, `unidad`, `sentido`, adecuada para EDA, dashboard y modelos. | Se rechazó mantener una estructura ancha porque dificultaba filtros, rankings y visualizaciones históricas. | Eddy Trejo |
| 2026-04-28 | Misael Valarzo | ChatGPT GPT-5.5 Thinking | Agregar búsqueda alternativa por nombre si no se encuentran indicadores por código, y resolver duplicados seleccionando filas con valores reales. | Se aceptó una lógica híbrida: primero código, luego nombre/variantes, y si hay duplicados elegir la fila que tenga valores bajo columnas de bancos. | Se corrigió el riesgo de obtener valores nulos cuando el código no aparecía o el indicador cambiaba de nombre. | Eddy Trejo |
| 2026-04-28 | Vinicio Morales | ChatGPT GPT-5.5 Thinking | Distinguir entre banco inexistente en un periodo y banco existente sin dato declarado. | Se aceptó no crear filas para bancos que no aparecen en el encabezado del periodo y conservar `NaN` si el banco existe pero no declara valor. | Se corrigió la posibilidad de llenar ceros o crear registros artificiales para bancos que no existían en ese periodo. | Vinicio Morales |
| 2026-04-28 | Misael Valarezo | ChatGPT GPT-5.5 Thinking | Optimizar el paso de procesamiento de aproximadamente 205 archivos Excel porque tardaba cerca de 15 minutos. | Se revisaron alternativas de paralelización y se ajustó el proceso para hacerlo más estable en notebook. | `ProcessPoolExecutor` y una primera alternativa con `ThreadPoolExecutor` fueron corregidas porque devolvían 0 filas; se detectó que se llamaba a la función incorrecta. | Eddy Trejo |
| 2026-04-28 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Corregir el paso 16 del notebook porque seguía sin extraer filas. | Se identificó que el proceso llamaba a `procesar_archivo_excel` en lugar de la función correcta `procesar_archivo_financiero`. | Se descartó la llamada anterior porque no correspondía con el flujo funcional del notebook. | Eddy Trejo |
| 2026-05-04 | Vinicio Morales | ChatGPT GPT-5.5 Thinking | Normalizar nombres bancarios duplicados: `BPDINERS`, `BP D MIRO`, `BP FINCA`, `VISIONFUND`, `CODESARROLLO`, entre otros. | Se aceptó una lógica de homologación que consolidó nombres como `DINERS`, `D-MIRO`, `FINCA`, `VISIONFUND ECUADOR` y `DESARROLLO DE LOS PUEBLOS S.A`. | Se corrigió la salida previa donde un mismo banco aparecía repetido con variantes históricas o sufijos societarios. | Eddy Trejo |
| 2026-05-04 | Vinicio Morales | ChatGPT GPT-5.5 Thinking | Modificar la extracción para tomar bancos únicamente desde la fila `CUENTA` en Balance y `NOMBRE DEL INDICADOR` en Indicadores. | Se aceptó restringir la detección de bancos a filas oficiales de encabezado para evitar capturar textos de otras zonas del Excel. | Se corrigió la detección flexible anterior que podía tomar nombres desde filas incorrectas. | Eddy Trejo |
| 2026-05-05 | Misael Valarezo | ChatGPT GPT-5.5 Thinking | Crear `resumen_del_caso.md` con contexto, pregunta de negocio, métricas, diccionario e hipótesis. | Se aceptó el documento del caso con pregunta principal, preguntas secundarias, KPIs, hipótesis y contexto del dominio. | Se ajustó el contenido para que sea claro, concreto y alineado con el objetivo del proyecto. | Eddy Trejo |
| 2026-05-05 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Iniciar el análisis exploratorio de datos y generar un notebook EDA. | Se aceptó el notebook de EDA con estadísticas descriptivas, revisión de nulos, rankings, comparaciones banco vs sistema y detección inicial de outliers. | Se corrigieron errores de ejecución en la fase de outliers y se ajustaron las columnas esperadas. | Eddy Trejo |
| 2026-05-06 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Evaluar si los valores monetarios debían mantenerse en miles o convertirse a millones de USD. | Se aceptó estandarizar valores monetarios en `millones_usd`, más apropiado para bancos y dashboards ejecutivos. | Se corrigió la unidad previa `miles_usd` para evitar valores visualmente extensos y difíciles de interpretar. | Eddy Trejo |
| 2026-05-06 | Vinicio Morales | ChatGPT GPT-5.5 Thinking | Corregir porcentajes de Excel porque valores como `8,95%` se estaban guardando como `0.09`. | Se aceptó almacenar ROE, morosidad y solvencia como porcentaje directo con dos decimales, por ejemplo `8.95`. | Se corrigió el cálculo que interpretaba porcentajes de Excel como proporciones decimales. | Vinicio Morales |
| 2026-05-06 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Revisar la solvencia porque se estaba usando una fila no adecuada como índice de solvencia. | Se aceptó cambiar la solvencia a `solvencia_proxy`, usando `IF112` o el nombre `ÍNDICE DE CAPITALIZACIÓN NETO: FK / FI`; si no existe, calcular `(IF41 / IF111) * 100`. | Se descartó usar `IF114` como solvencia principal porque correspondía a suficiencia patrimonial y no era el mejor proxy para este objetivo. | Eddy Trejo |
| 2026-05-07 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Crear el dashboard inicial en Streamlit para responder las hipótesis del proyecto. | Se aceptó un dashboard con vistas de banco vs sistema, ranking, riesgo financiero y tabla comparativa, usando gráficos claros y sin pastel. | Se ajustó la propuesta para evitar gráficos complejos y priorizar barras, líneas, dispersión y heatmaps. | Eddy Trejo |
| 2026-05-07 | Vinicio Morales | ChatGPT GPT-5.5 Thinking | Mejorar el dashboard con pestañas específicas para Banco vs Sistema y Ranking histórico. | Se aceptó una versión con filtros por KPI, banco, año, Top N configurable y evolución histórica anual. | Se corrigió el diseño para que la pestaña de ranking no dependa del banco seleccionado. | Eddy Trejo |
| 2026-05-08 | Vinicio Morales | ChatGPT GPT-5.5 Thinking | Explicar si el proyecto usaba modelos y proponer modelos de Machine Learning. | Se aceptó incorporar tres modelos principales: `RandomForestRegressor` para ROE, `KMeans` para segmentación bancaria y `Prophet` para proyecciones. | Se descartó agregar modelos innecesarios o poco defendibles para el alcance del proyecto. | Eddy Trejo |
| 2026-05-08 | Misale Valarezo | ChatGPT GPT-5.5 Thinking | Generar notebook de modelado con RandomForestRegressor, KMeans y Prophet, comentado en español. | Se aceptó `03_modelado_ml` con pasos documentados, exportación de resultados y modelos serializados. | Se corrigieron problemas de compatibilidad de Prophet con NumPy/CmdStan y se simplificó el enfoque a tres modelos. | Eddy Trejo |
| 2026-05-09 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Actualizar el dashboard para visualizar los resultados de los modelos. | Se aceptaron pestañas para Modelo ROE, Clusters KMeans y Proyecciones Prophet. | Se corrigió un error de Plotly con `add_vline` y fechas `Timestamp`, reemplazándolo por `add_shape` y `add_annotation`. | Eddy Trejo |
`04_score_salud_bancaria_v2`, con score para todos los años y score actual con Prophet solo en el último año. | Se corrigió el riesgo de fuga temporal: Prophet no se aplica a años históricos. | Eddy Trejo |
| 2026-05-11 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Crear API FastAPI dentro del mismo proyecto. | Se aceptó `api_financiera.py` con endpoints para health, bancos, periodos, indicadores, KPIs, rankings, score y forecast. | Se ajustó la API para que lea Parquet/CSV y no recalcule modelos en tiempo de consulta. | Eddy Trejo |
| 2026-05-11 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Generar documentación final por fases y requirements del proyecto. | Se aceptaron archivos en `08_plan_y_ejecucion`: preparación de datos, EDA, modelos, dashboard y FastAPI; además se generó `requirements.txt`. | Se corrigió la necesidad de usar versiones fijas compatibles con el proyecto. | Eddy Trejo |
| 2026-05-12 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Preparar el proyecto para GitHub y despliegue en Streamlit Cloud. | Se aceptó un `requirements.txt` único para Streamlit Cloud con dependencias necesarias para ejecutar `app_dashboard.py`. | Se corrigió el error `ModuleNotFoundError: No module named 'plotly'` agregando dependencias faltantes. | Eddy Trejo |
| 2026-05-13 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Corregir despliegue de API en Render porque estaba usando Python 3.14. | Se aceptó crear `.python-version` con `3.12.13` y actualizar `requirements_api.txt` con pandas, numpy y pyarrow. | Se corrigió el error de `pydantic-core` provocado por Python 3.14 y luego el error `No module named numpy`. | Eddy Trejo |
| 2026-05-15 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Revisar dashboard y API finales para crear una alternativa más clara con enfoque de storytelling con datos. | Se aceptó un dashboard alternativo `app_dashboard_storytelling.py` con siete pestañas clave y una API mínima `api_financiera_minimal.py` con endpoints `/health`, `/banks` y `/score`. | Se simplificó la API original, que tenía más endpoints de los necesarios para la versión ejecutiva del dashboard; también se eliminó la pestaña de tabla comparativa. | Eddy Trejo |

---

## Decisiones críticas validadas

1. El dataset final se construye en formato largo.
2. El periodo se extrae desde Balance o desde una hoja con cabecera `ESTADO DE SITUACIÓN`.
3. Los indicadores se buscan primero por código y luego por nombre como respaldo.
4. Las filas duplicadas de indicadores se resuelven tomando la fila con valores bajo bancos.
5. No se generan registros para bancos inexistentes en un periodo.
6. Si el banco existe pero no declara valor, se conserva `NaN`.
7. Los bancos se normalizan para evitar duplicados históricos.
8. Los nombres de bancos se toman solo desde filas oficiales de encabezado.
9. Los valores monetarios se expresan en `millones_usd`.
10. Los indicadores porcentuales se guardan como porcentaje directo, por ejemplo `8.95`.
11. La solvencia se trabaja como `solvencia_proxy`, priorizando `IF112` o el cálculo `(IF41 / IF111) * 100`.
12. El dashboard evita gráficos de pastel y prioriza gráficos interpretables.
13. Los modelos aceptados son `RandomForestRegressor`, `KMeans` y `Prophet`.
14. El score inteligente se calcula históricamente sin Prophet y en el último año con Prophet.
15. La API mínima se usa para que la pestaña Score Inteligente consuma un endpoint y no lea directamente el dataset de score.

---

## Observación final

El historial evidencia que el proyecto no se construyó únicamente como una visualización, sino como un flujo completo de ciencia de datos:

```text
Datos crudos Excel
    ↓
Preparación y limpieza
    ↓
Dataset analítico limpio
    ↓
EDA y validación
    ↓
Modelos de Machine Learning
    ↓
Score inteligente
    ↓
Dashboard ejecutivo
    ↓
API FastAPI
    ↓
Despliegue en GitHub / Streamlit Cloud / Render
```

