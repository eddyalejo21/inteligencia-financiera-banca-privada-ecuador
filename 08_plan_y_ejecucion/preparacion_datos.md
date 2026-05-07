# Preparación de Datos

## Objetivo general
Transformar los 205 archivos Excel ubicados en `00_datos_crudos` en un dataset limpio, consolidado y estructurado en formato largo para analizar el desempeño financiero de los bancos privados.

## Estructura final del dataset
Generar un dataset con la siguiente estructura:

```text
periodo | nombre_original | nombre_normalizado | indicador | valor | unidad
```

## Indicadores consolidados
Conservar únicamente los indicadores necesarios para el análisis financiero:

- activos_totales
- pasivos_totales
- patrimonio
- roe
- morosidad
- solvencia

## Fase 1. Lectura de archivos crudos
**Objetivo:** Leer automáticamente los 205 archivos Excel almacenados en `00_datos_crudos`.

- Identificar archivos con extensión `.xls`, `.xlsx` y `.xlsm`.
- Recorrer todos los archivos sin depender de una lista manual.
- Registrar el nombre de cada archivo procesado.

## Fase 2. Exploración de hojas
**Objetivo:** Explorar las hojas disponibles en cada archivo Excel.

- Listar los nombres de hojas existentes por archivo.
- Detectar si existen hojas llamadas `Balance` e `Indicadores`.

## Fase 3. Detección de hojas clave
**Objetivo:** Ubicar correctamente las hojas necesarias aunque sus nombres cambien.

- Buscar la hoja `Balance` por nombre directo.
- Buscar el texto `Estado de Situación` si no existe una hoja llamada `Balance`.
- Buscar la hoja `Indicadores` por nombre directo.
- Buscar el texto `Indicadores Financieros` si no existe una hoja llamada `Indicadores`.

## Fase 4. Extracción del período
**Objetivo:** Obtener el período financiero de cada archivo procesado.

- Mantener las funciones existentes para extraer fechas.
- Normalizar la fecha al formato `YYYY-MM`.
- Asociar cada registro financiero con su período correspondiente.

## Fase 5. Limpieza de bancos
**Objetivo:** Estandarizar los nombres de bancos para evitar duplicados.

- Extraer los bancos desde las filas de encabezado válidas.
- Conservar el nombre original del banco.
- Normalizar el nombre eliminando `BP`, comillas simples y comillas dobles.
- Limpiar espacios innecesarios y diferencias de escritura.
- Excluir categorías agregadas que no representan bancos individuales.

## Fase 6. Extracción de cuentas de balance
**Objetivo:** Extraer los valores principales de tamaño financiero desde la hoja `Balance`.

- Buscar la fila `Total Activo` o `Total Activos`.
- Buscar la fila `Total Pasivo` o `Total Pasivos`.
- Buscar la fila `Total Patrimonio`.
- Convertir cada cuenta encontrada en un indicador del dataset final.

## Fase 7. Extracción de indicadores financieros
**Objetivo:** Extraer los indicadores clave desde la hoja `Indicadores`.

- Buscar `RESULTADOS DEL EJERCICIO / PATRIMONIO PROMEDIO` en la sección `Rentabilidad`.
- Buscar `MOROSIDAD DE LA CARTERA TOTAL` en la sección `Índices de morosidad`.
- Buscar `(PATRIMONIO + RESULTADOS) / ACTIVOS INMOVILIZADOS NETOS` en la sección `Suficiencia patrimonial`.
- Asignar los nombres normalizados `roe`, `morosidad` y `solvencia`.

## Fase 8. Construcción del dataset largo
**Objetivo:** Consolidar la información en una estructura tidy data.

- Transformar los bancos de columnas a filas.
- Unificar balance e indicadores en una sola tabla.
- Crear las columnas `periodo`, `nombre_original`, `nombre_normalizado`, `indicador`, `valor` y `unidad`.
- Mantener los valores numéricos respetando el formato original del boletín.

## Fase 9. Validación de calidad
**Objetivo:** Revisar que el dataset final sea consistente y utilizable.

- Validar archivos procesados correctamente.
- Identificar archivos sin hojas clave.
- Revisar bancos duplicados por problemas de normalización.
- Confirmar que solo existan los indicadores requeridos.

## Fase 10. Exportación de resultados
**Objetivo:** Guardar el dataset limpio para análisis, API y dashboard.

- Crear la carpeta `01_datos_procesados` si no existe.
- Exportar el dataset final en formato `.csv`.
- Exportar el dataset final en formato `.parquet`.

## Resultado final
Obtener un dataset limpio, histórico y estandarizado que permita comparar bancos por tamaño, rentabilidad, morosidad y solvencia, listo para análisis exploratorio, rankings financieros y visualización en Streamlit.
