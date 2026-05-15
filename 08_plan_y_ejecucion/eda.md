# Análisis Exploratorio de Datos

## Objetivo

Analizar el dataset financiero limpio para comprender su estructura, calidad y comportamiento histórico.

El notebook principal de esta fase es:

```text
03_cuadernos/02_eda_rankings.ipynb
```

---

## Dataset utilizado

```text
01_datos_procesados/dataset_financiero_limpio.parquet
```

o, como respaldo:

```text
01_datos_procesados/dataset_financiero_limpio.csv
```

---

## Actividades realizadas

### 1. Carga y validación inicial

Se validó que el dataset contenga las columnas esperadas:

```text
periodo | banco_estandarizado | indicador | valor | unidad | sentido
```

También se revisaron:

- cantidad de filas;
- bancos disponibles;
- periodos disponibles;
- indicadores existentes;
- tipos de datos.

---

### 2. Estadísticas descriptivas

Se calcularon medidas descriptivas por indicador:

| Métrica | Uso |
|---|---|
| registros | Total de filas por indicador. |
| no_nulos | Cantidad de valores disponibles. |
| media | Promedio del indicador. |
| mediana | Valor central. |
| mínimo | Valor más bajo. |
| percentiles | Distribución del indicador. |
| máximo | Valor más alto. |
| desviación estándar | Dispersión de los valores. |

---

### 3. Revisión de nulos

Se revisaron valores nulos por:

- indicador;
- banco;
- periodo.

Se mantuvo `NaN` cuando un banco existía en un periodo pero no reportaba un valor. Esto permite diferenciar entre:

```text
valor faltante != valor cero
```

---

### 4. Análisis por KPI

Se analizaron los indicadores clave:

| KPI | Interpretación |
|---|---|
| activos_totales | Tamaño financiero. |
| roe | Rentabilidad sobre patrimonio. |
| morosidad | Calidad de cartera. |
| solvencia_proxy | Fortaleza patrimonial aproximada. |

---

### 5. Rankings

Se generaron rankings por indicador.

Criterio de orden:

| Indicador | Orden |
|---|---|
| activos_totales | Mayor a menor. |
| roe | Mayor a menor. |
| morosidad | Menor a mayor. |
| solvencia_proxy | Mayor a menor. |

---

### 6. Banco vs sistema

Se calculó el promedio del sistema para comparar el desempeño de cada banco frente al conjunto de bancos.

Esto permite responder:

```text
¿El banco está por encima o por debajo del promedio del sistema?
```

---

### 7. Análisis anual

Se construyeron vistas anuales mediante promedio de los meses disponibles.

Esto permitió:

- reducir ruido mensual;
- visualizar tendencias históricas;
- comparar bancos por año;
- alimentar gráficos del dashboard.

---

### 8. Detección inicial de outliers

Se revisaron valores extremos en indicadores como:

- ROE;
- morosidad;
- solvencia proxy;
- activos totales.

Los outliers no fueron eliminados automáticamente, sino identificados para revisión analítica.

---

## Resultado

La fase EDA permitió validar que el dataset era adecuado para:

- rankings financieros;
- visualizaciones comparativas;
- análisis banco vs sistema;
- modelos de Machine Learning;
- construcción de score financiero.
