# Dashboard V2 + Modelos ML + Score V2

## Cambio principal

Esta versión del dashboard ya está preparada para leer `score_salud_bancaria` generado por:

```text
03_cuadernos/04_score_salud_bancaria_v2.ipynb
```

La pestaña **Score inteligente** ahora incluye:

- filtro de año;
- score histórico;
- score actual con Prophet;
- ranking por año;
- evolución histórica del score del banco seleccionado;
- análisis ejecutivo automático.

## Orden de ejecución recomendado

```text
1. 03_cuadernos/03_modelado_ml.ipynb
2. 03_cuadernos/04_score_salud_bancaria_v2.ipynb
3. streamlit run 02_scripts/app_dashboard_v2_modelos_ml_score_v2.py
```

## Nota metodológica

- Score histórico: RandomForestRegressor + KMeans.
- Score actual: RandomForestRegressor + KMeans + Prophet.
