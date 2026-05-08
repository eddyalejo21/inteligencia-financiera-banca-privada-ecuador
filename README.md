# Sistema de Inteligencia Financiera para el Análisis del Sector Bancario Ecuatoriano

## Integrantes

- Eddy Alejandro Trejo Mejia
- Cristian Vinicio Morales Quinga
- Misael Abisai Valarezo Bracho

> Proyecto desarrollado por el **Grupo 02** para el seminario de Ciencia de Datos 2026.

---

## Descripción del caso

La Superintendencia de Bancos del Ecuador publica mensualmente boletines estadísticos con información financiera de los bancos privados del país. Estos boletines se encuentran en archivos Excel con estructuras institucionales complejas: encabezados multinivel, celdas fusionadas, nombres de bancos con variaciones históricas y bancos organizados como columnas en lugar de filas.

El objetivo del proyecto es transformar esos boletines en un dataset analítico limpio y consolidado que permita comparar, rankear y analizar el desempeño de las instituciones bancarias por indicadores clave como activos totales, pasivos totales, patrimonio, ROE, morosidad y solvencia proxy.

---

## Objetivo del proyecto

Construir un sistema de inteligencia financiera que permita:

- Consolidar información histórica de boletines financieros mensuales.
- Transformar archivos Excel institucionales a formato analítico largo.
- Estandarizar nombres de bancos y periodos.
- Generar datasets limpios en CSV y Parquet.
- Analizar rankings financieros por banco, periodo e indicador.
- Preparar insumos para un dashboard interactivo en Streamlit.

---

## Estructura del proyecto

```text
GRUPO_02/
├── 00_datos_crudos/
│   ├── INSTRUCCIONES_DESCARGA_DATOS.md
│   └── .gitkeep
│
├── 01_datos_procesados/
│   ├── auditoria/
│   ├── analisis/
│   ├── dataset_financiero_limpio.csv
│   ├── dataset_financiero_limpio.parquet
│   ├── dataset_bancos.csv
│   ├── dataset_bancos.parquet
│   ├── dataset_periodos.csv
│   └── dataset_periodos.parquet
│
├── 02_scripts/
├── 03_cuadernos/
│   ├── 01_exploracion_y_limpieza.ipynb
│   └── 02_eda_rankings.ipynb
│
├── 04_modelos/
├── 05_referencias/
├── 06_archivo/
├── 07_contexto/
│   └── resumen_del_caso.md
│
├── 08_plan_y_ejecucion/
│   ├── preparacion_datos.md
│   └── bitacora_interaccion_ia.md
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Dataset final

El dataset principal generado por el pipeline se encuentra en:

```text
01_datos_procesados/dataset_financiero_limpio.csv
01_datos_procesados/dataset_financiero_limpio.parquet
```

Estructura final:

```text
periodo | banco_estandarizado | indicador | valor | unidad | sentido
```

Ejemplo:

```csv
periodo,banco_estandarizado,indicador,valor,unidad,sentido
2009-01,AUSTRO,activos_totales,640.62,millones_usd,mayor_es_tamano
2009-01,AUSTRO,roe,10.11,porcentaje,mayor_es_mejor
2009-01,AUSTRO,morosidad,6.10,porcentaje,menor_es_mejor
2009-01,AUSTRO,solvencia_proxy,8.95,porcentaje,mayor_es_mejor
```

---

## Indicadores incluidos

| Indicador | Descripción | Unidad | Sentido |
|---|---|---|---|
| `activos_totales` | Tamaño financiero del banco medido por total de activos. | `millones_usd` | Mayor indica mayor tamaño. |
| `pasivos_totales` | Obligaciones y fuentes de financiamiento del banco. | `millones_usd` | Informativo. |
| `patrimonio` | Respaldo patrimonial contable de la institución. | `millones_usd` | Mayor es mejor. |
| `roe` | Rentabilidad sobre patrimonio. | `porcentaje` | Mayor es mejor. |
| `morosidad` | Calidad de cartera medida por cartera problemática frente a cartera total. | `porcentaje` | Menor es mejor. |
| `solvencia_proxy` | Proxy de solvencia basado en el índice de capitalización neto FK/FI. | `porcentaje` | Mayor es mejor. |

---

## Instrucciones de instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/sistema-inteligencia-financiera-banca-privada.git
cd sistema-inteligencia-financiera-banca-privada
```

Si el proyecto se mantiene localmente con el nombre `GRUPO_02`, también puedes entrar directamente a esa carpeta:

```bash
cd GRUPO_02
```

---

### 2. Crear entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4. Registrar kernel para Jupyter

```bash
python -m ipykernel install --user --name grupo02-financiero --display-name "Python Grupo 02 Financiero"
```

Luego abre los notebooks desde VS Code o Jupyter y selecciona el kernel:

```text
Python Grupo 02 Financiero
```

---

## Instrucciones para descarga de datos

Los archivos Excel originales no se versionan en GitHub porque son numerosos y pueden aumentar innecesariamente el tamaño del repositorio.

La carpeta `00_datos_crudos/` sí se mantiene en el repositorio, pero los archivos `.xls`, `.xlsx` y `.xlsm` están excluidos mediante `.gitignore`.

### Pasos para obtener los datos crudos

1. Ingresar al portal oficial de estadísticas de la Superintendencia de Bancos del Ecuador.
2. Descargar los boletines financieros mensuales de banca privada.
3. Colocar los archivos descargados dentro de:

```text
00_datos_crudos/
```

4. Verificar que los archivos tengan extensiones soportadas:

```text
.xls
.xlsx
.xlsm
```

5. No modificar manualmente la estructura interna de los boletines.

### Enlace de descarga

Colocar aquí el enlace oficial o compartido de descarga de datos:

```text
COLOCAR_AQUI_EL_ENLACE_DE_DESCARGA
```

También se incluye una guía específica en:

```text
00_datos_crudos/INSTRUCCIONES_DESCARGA_DATOS.md
```

---

## Ejecución del pipeline

### 1. Exploración, extracción y limpieza

Ejecutar el notebook:

```text
03_cuadernos/01_exploracion_y_limpieza.ipynb
```

Este notebook realiza:

- lectura de los archivos Excel;
- detección de hoja Balance e Indicadores;
- extracción del periodo;
- extracción de activos, pasivos, patrimonio, ROE, morosidad y solvencia proxy;
- normalización de bancos;
- conversión de valores monetarios a millones de dólares;
- redondeo de porcentajes a dos decimales;
- generación del dataset financiero limpio;
- generación de datasets auxiliares de bancos y periodos;
- generación de archivos de auditoría.

---

### 2. Análisis exploratorio y rankings

Ejecutar el notebook:

```text
03_cuadernos/02_eda_rankings.ipynb
```

Este notebook realiza:

- validación del dataset limpio;
- estadísticas descriptivas;
- análisis de nulos;
- rankings por último periodo;
- rankings históricos;
- comparación contra promedio del sistema;
- detección inicial de outliers;
- evolución temporal de indicadores;
- generación de archivos derivados para dashboard.

---

## Archivos generados

### Dataset limpio

```text
01_datos_procesados/dataset_financiero_limpio.csv
01_datos_procesados/dataset_financiero_limpio.parquet
```

### Datasets auxiliares

```text
01_datos_procesados/dataset_bancos.csv
01_datos_procesados/dataset_bancos.parquet
01_datos_procesados/dataset_periodos.csv
01_datos_procesados/dataset_periodos.parquet
```

### Auditoría

```text
01_datos_procesados/auditoria/
```

### Resultados de análisis

```text
01_datos_procesados/analisis/
```

---

## Buenas prácticas de versionamiento

Este proyecto usa `.gitignore` para excluir:

- archivos Excel crudos;
- archivos comprimidos;
- entornos virtuales;
- cachés de Python;
- checkpoints de Jupyter;
- archivos temporales del sistema operativo.

La carpeta `00_datos_crudos` se conserva mediante `.gitkeep` y contiene instrucciones para descargar los datos.

---

## Estado del proyecto

- Preparación de datos: completada.
- Dataset limpio: generado.
- EDA y rankings: en desarrollo/completado según ejecución local.
- Dashboard Streamlit: siguiente fase recomendada.

---

## Mantenimiento

Proyecto mantenido por:

```text
Grupo 02
Eddy Trejo
```
