# Bitácora de interacción con IA

**Proyecto:** Ciencia de Datos Seminario 2026  
**Usuario:** Eddy Trejo  
**IA:** ChatGPT GPT-5.5 Thinking  
**Formato solicitado:** fecha de consulta, nombre del usuario, nombre de la IA, prompt resumido, salida aceptada, salida rechazada o corregida y verificador.

---

## Bitácora

| Fecha de la consulta | Nombre | Nombre de la IA | Prompt resumido | Salida que aceptamos | Salida que rechazamos o corregimos | Quién verificó |
|---|---|---|---|---|---|---|
| 2026-04-27 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Analizar un boletín Excel de bancos privados para identificar hojas, celdas e indicadores importantes: activos, ROE, morosidad y solvencia. | Resumen técnico del archivo, identificación de hojas clave (`BALANCE`, `INDICADORES`, `RK`, `COMPOS CART`), celdas relevantes y explicación financiera de cada indicador. | Se corrigió la interpretación de solvencia: el archivo no tenía una celda literal llamada `Índice de Solvencia`; se propuso usar `IF114`/suficiencia patrimonial o capitalización como referencia metodológica según disponibilidad. | Eddy Trejo |
| 2026-04-27 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Modificar el enfoque para buscar morosidad, ROE y solvencia por código de indicador y no por nombre textual. | Notebook de exploración por código, usando `IF013` para morosidad, `IF295` para ROE e `IF114` para solvencia. | Se reemplazó el enfoque basado únicamente en nombres, porque los textos variaban entre archivos. | Eddy Trejo |
| 2026-04-28 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Adaptar el notebook para que la fecha salga solo de Balance o de la cabecera `ESTADO DE SITUACIÓN`, generar dataset largo y acelerar la lectura de 205 archivos. | Notebook de extracción financiera por código, fecha desde Balance, dataset largo con activos, pasivos, patrimonio, ROE, morosidad y solvencia. | Se corrigió la estrategia para no tomar fechas desde hojas no autorizadas ni desde el nombre del archivo. | Eddy Trejo |
| 2026-04-28 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Mejorar el notebook para que, si no encuentra ROE, morosidad o solvencia por código, los busque por nombre y variantes; además distinguir banco inexistente de banco sin dato declarado. | Notebook híbrido robusto con búsqueda por código y fallback por nombre, conservación de `NaN` cuando el banco existe pero no declara, y generación de datasets auxiliares de bancos y periodos. | Se corrigió el enfoque anterior que podía generar nulos si el código no aparecía o si el indicador tenía otro nombre. | Eddy Trejo |
| 2026-04-28 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Optimizar el paso 16 porque el procesamiento de 205 archivos tardaba cerca de 15 minutos y crear `dataset_financiero_limpio` solo con columnas finales. | Se propuso procesamiento paralelo y se definió `dataset_financiero_limpio` con las columnas `periodo`, `banco_estandarizado`, `indicador`, `valor`, `unidad`, `sentido`. | La primera optimización con `ProcessPoolExecutor` no fue aceptada operativamente porque devolvió 0 filas en el entorno de notebook. | Eddy Trejo |
| 2026-04-28 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Corregir el paso 16 porque con `ProcessPoolExecutor` procesó los archivos pero devolvió 0 filas. | Se propuso reemplazar el paso 16 por `ThreadPoolExecutor`, más estable en notebooks de VS Code/Jupyter. | La salida seguía dando 0 filas, por lo que se investigó una segunda causa. | Eddy Trejo |
| 2026-04-28 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Corregir nuevamente el paso 16 porque tampoco extrajo filas con `ThreadPoolExecutor`. | Se identificó que el paso 16 llamaba a una función incorrecta (`procesar_archivo_excel`) y se corrigió para llamar a `procesar_archivo_financiero`. | Se rechazó/corrigió la llamada anterior a una función inexistente o no usada en el notebook. | Eddy Trejo |
| 2026-05-04 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Normalizar nombres de bancos duplicados: `BPDINERS`, `BP D MIRO`, `BP FINCA`, `VISIONFUND`, `CODESARROLLO`, entre otros. | Se agregó lógica de normalización bancaria para consolidar variantes en nombres estándar como `DINERS`, `D-MIRO`, `FINCA`, `VISIONFUND ECUADOR` y `DESARROLLO DE LOS PUEBLOS S.A`. | Se corrigió la salida anterior donde el dataset de bancos podía tener duplicados por variaciones históricas o sufijos societarios. | Eddy Trejo |
| 2026-05-04 | Eddy Trejo | ChatGPT GPT-5.5 Thinking | Modificar el notebook para tomar nombres de bancos únicamente desde la fila oficial de Balance con `CUENTA` y de Indicadores con `NOMBRE DEL INDICADOR`. | Se modificó la detección de encabezados oficiales para que los bancos solo salgan de esas filas, evitando nombres tomados desde filas incorrectas. | Se corrigió la detección flexible anterior que podía tomar bancos desde otras filas cercanas al indicador. | Eddy Trejo |

---

## Resumen de decisiones aceptadas

1. Usar formato largo para el dataset financiero final.
2. Tomar fecha del periodo únicamente desde Balance o desde hoja con `ESTADO DE SITUACIÓN`.
3. Extraer indicadores financieros por código como primera opción.
4. Usar búsqueda por nombre y variantes solo como respaldo.
5. Resolver duplicados seleccionando la fila con valores reales bajo bancos.
6. No crear filas para bancos que no aparecen en el periodo.
7. Mantener `NaN` cuando el banco existe en el encabezado pero no reporta valor.
8. Normalizar nombres de bancos para evitar duplicados en filtros y rankings.
9. Leer bancos únicamente desde encabezados oficiales: `CUENTA` y `NOMBRE DEL INDICADOR`.
10. Exportar datasets principales y auxiliares en CSV y Parquet.

---

## Formato estándar para futuras bitácoras

Para próximas solicitudes, se mantendrá esta estructura:

| Fecha de la consulta | Nombre | Nombre de la IA | Prompt resumido | Salida que aceptamos | Salida que rechazamos o corregimos | Quién verificó |
|---|---|---|---|---|---|---|
| `YYYY-MM-DD` | `Nombre del usuario` | `Nombre de la IA` | `Resumen breve de la pregunta o solicitud` | `Resultado aceptado` | `Resultado descartado, corregido o ajustado` | `Nombre de quien validó` |
