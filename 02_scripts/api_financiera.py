"""
API FastAPI para el Sistema de Inteligencia Financiera Bancaria.

Ubicación sugerida dentro del proyecto:
    02_scripts/api_financiera.py

Ejecución desde la raíz del proyecto:
    python -m uvicorn api_financiera:app --reload --app-dir 02_scripts

Dataset principal requerido:
    01_datos_procesados/dataset_financiero_limpio.parquet
    o, como respaldo:
    01_datos_procesados/dataset_financiero_limpio.csv

Estructura esperada:
    periodo | banco_estandarizado | indicador | valor | unidad | sentido
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# =============================================================================
# 1. Configuración de la aplicación
# =============================================================================

app = FastAPI(
    title="API de Inteligencia Financiera Bancaria",
    description=(
        "API para consultar KPIs financieros, rankings, scores y proyecciones "
        "del sistema de inteligencia financiera de bancos privados ecuatorianos."
    ),
    version="1.0.0",
)

# CORS permite que un frontend externo, por ejemplo Streamlit u otra app web,
# pueda consumir esta API durante desarrollo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# 2. Catálogos y alias
# =============================================================================

# Indicadores válidos en el dataset limpio.
INDICADORES_VALIDOS = {
    "activos_totales",
    "pasivos_totales",
    "patrimonio",
    "roe",
    "morosidad",
    "solvencia_proxy",
}

# Alias para permitir consultas más naturales desde la API.
# Ejemplo: /financials/rank?metric=assets
ALIAS_INDICADORES = {
    "assets": "activos_totales",
    "asset": "activos_totales",
    "activos": "activos_totales",
    "activo": "activos_totales",
    "activos_totales": "activos_totales",

    "liabilities": "pasivos_totales",
    "pasivos": "pasivos_totales",
    "pasivo": "pasivos_totales",
    "pasivos_totales": "pasivos_totales",

    "equity": "patrimonio",
    "patrimonio": "patrimonio",

    "roe": "roe",
    "rentabilidad": "roe",

    "morosidad": "morosidad",
    "npl": "morosidad",
    "mora": "morosidad",

    "solvencia": "solvencia_proxy",
    "solvency": "solvencia_proxy",
    "solvencia_proxy": "solvencia_proxy",
}

# En estos indicadores, mayor valor representa mejor posición.
INDICADORES_MAYOR_ES_MEJOR = {
    "activos_totales",
    "pasivos_totales",
    "patrimonio",
    "roe",
    "solvencia_proxy",
}

# En morosidad, menor valor es mejor.
INDICADORES_MENOR_ES_MEJOR = {
    "morosidad",
}


# =============================================================================
# 3. Utilidades generales
# =============================================================================

def encontrar_raiz_proyecto() -> Path:
    """
    Busca la raíz del proyecto identificando la carpeta 01_datos_procesados.

    Esto permite ejecutar la API desde la raíz del proyecto o desde 02_scripts.
    """

    # Ruta actual desde donde se ejecuta el proceso.
    actual = Path.cwd().resolve()

    # Ruta donde está este archivo.
    archivo_actual = Path(__file__).resolve()

    # Candidatos: cwd, padres de cwd, carpeta del script y padres del script.
    candidatos = [actual] + list(actual.parents) + [archivo_actual.parent] + list(archivo_actual.parents)

    # Recorro candidatos hasta encontrar 01_datos_procesados.
    for ruta in candidatos:
        if (ruta / "01_datos_procesados").exists():
            return ruta

    # Si no se encuentra, se lanza un error claro.
    raise FileNotFoundError(
        "No se encontró la carpeta 01_datos_procesados. "
        "Ejecuta la API desde la raíz del proyecto GRUPO_02."
    )


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto para comparar nombres de bancos e indicadores.
    """

    return str(texto).strip().upper()


def normalizar_indicador(metric: str) -> str:
    """
    Convierte un alias recibido por API al indicador real del dataset.
    """

    metric_norm = str(metric).strip().lower()

    if metric_norm not in ALIAS_INDICADORES:
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": "Indicador no reconocido.",
                "metric_recibido": metric,
                "indicadores_validos": sorted(INDICADORES_VALIDOS),
                "alias_validos": sorted(ALIAS_INDICADORES.keys()),
            },
        )

    return ALIAS_INDICADORES[metric_norm]


def limpiar_json(obj: Any) -> Any:
    """
    Convierte valores NumPy/Pandas a tipos compatibles con JSON.

    Evita devolver NaN, NaT o tipos no serializables.
    """

    if isinstance(obj, dict):
        return {k: limpiar_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [limpiar_json(v) for v in obj]

    if isinstance(obj, tuple):
        return tuple(limpiar_json(v) for v in obj)

    if pd.isna(obj):
        return None

    if isinstance(obj, (np.integer,)):
        return int(obj)

    if isinstance(obj, (np.floating,)):
        return float(obj)

    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()

    return obj


def dataframe_to_json(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convierte un DataFrame a lista de diccionarios JSON-safe.
    """

    df_tmp = df.copy()
    df_tmp = df_tmp.replace({np.nan: None})
    return limpiar_json(df_tmp.to_dict(orient="records"))


# =============================================================================
# 4. Carga de datasets con caché
# =============================================================================

@lru_cache(maxsize=1)
def cargar_dataset_financiero() -> pd.DataFrame:
    """
    Carga el dataset financiero limpio desde Parquet o CSV.

    Se usa caché para no leer el archivo en cada petición.
    """

    raiz = encontrar_raiz_proyecto()

    ruta_parquet = raiz / "01_datos_procesados" / "dataset_financiero_limpio.parquet"
    ruta_csv = raiz / "01_datos_procesados" / "dataset_financiero_limpio.csv"

    if ruta_parquet.exists():
        df = pd.read_parquet(ruta_parquet)
    elif ruta_csv.exists():
        df = pd.read_csv(ruta_csv)
    else:
        raise FileNotFoundError(
            "No se encontró dataset_financiero_limpio.parquet ni dataset_financiero_limpio.csv "
            "en 01_datos_procesados."
        )

    columnas_requeridas = {
        "periodo",
        "banco_estandarizado",
        "indicador",
        "valor",
        "unidad",
        "sentido",
    }

    faltantes = columnas_requeridas - set(df.columns)

    if faltantes:
        raise ValueError(f"El dataset no tiene las columnas requeridas: {sorted(faltantes)}")

    df = df.copy()

    # Normalizo columnas principales.
    df["periodo"] = df["periodo"].astype(str).str.strip()
    df["banco_estandarizado"] = df["banco_estandarizado"].astype(str).str.strip().str.upper()
    df["indicador"] = df["indicador"].astype(str).str.strip().str.lower()
    df["unidad"] = df["unidad"].astype(str).str.strip().str.lower()
    df["sentido"] = df["sentido"].astype(str).str.strip().str.lower()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Columnas temporales auxiliares.
    df["periodo_dt"] = pd.to_datetime(df["periodo"] + "-01", errors="coerce")
    df["anio"] = df["periodo_dt"].dt.year
    df["mes"] = df["periodo_dt"].dt.month

    # Mantengo solo indicadores conocidos.
    df = df[df["indicador"].isin(INDICADORES_VALIDOS)].copy()

    return df


@lru_cache(maxsize=4)
def cargar_resultado_modelo(nombre_base: str) -> pd.DataFrame:
    """
    Carga resultados adicionales generados por notebooks de modelos.

    Busca primero Parquet y luego CSV dentro de:
        01_datos_procesados/modelos/
    """

    raiz = encontrar_raiz_proyecto()
    carpeta_modelos = raiz / "01_datos_procesados" / "modelos"

    ruta_parquet = carpeta_modelos / f"{nombre_base}.parquet"
    ruta_csv = carpeta_modelos / f"{nombre_base}.csv"

    if ruta_parquet.exists():
        return pd.read_parquet(ruta_parquet)

    if ruta_csv.exists():
        return pd.read_csv(ruta_csv)

    return pd.DataFrame()


def limpiar_cache_datos() -> None:
    """
    Limpia caché de datasets.
    Útil si se regeneran archivos sin reiniciar la API.
    """

    cargar_dataset_financiero.cache_clear()
    cargar_resultado_modelo.cache_clear()


# =============================================================================
# 5. Endpoints básicos
# =============================================================================

@app.get("/")
def root() -> dict[str, Any]:
    """
    Endpoint raíz de la API.
    """

    return {
        "mensaje": "API de Inteligencia Financiera Bancaria",
        "version": "1.0.0",
        "documentacion_swagger": "/docs",
        "documentacion_redoc": "/redoc",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    """
    Verifica si la API puede cargar el dataset principal.
    """

    try:
        df = cargar_dataset_financiero()

        return {
            "status": "ok",
            "filas": int(len(df)),
            "bancos": int(df["banco_estandarizado"].nunique()),
            "periodos": int(df["periodo"].nunique()),
            "indicadores": sorted(df["indicador"].dropna().unique().tolist()),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "mensaje": "No se pudo cargar el dataset principal.",
                "detalle": repr(e),
            },
        )


@app.post("/admin/reload")
def reload_data() -> dict[str, str]:
    """
    Limpia caché de datos para recargar archivos Parquet/CSV regenerados.
    """

    limpiar_cache_datos()

    return {
        "mensaje": "Caché limpiada correctamente. La próxima consulta recargará los datasets."
    }


# =============================================================================
# 6. Endpoints de metadatos
# =============================================================================

@app.get("/financials/metadata")
def metadata() -> dict[str, Any]:
    """
    Devuelve metadatos generales del dataset financiero.
    """

    df = cargar_dataset_financiero()

    return limpiar_json(
        {
            "filas": len(df),
            "bancos": df["banco_estandarizado"].nunique(),
            "periodos": df["periodo"].nunique(),
            "periodo_min": df["periodo"].min(),
            "periodo_max": df["periodo"].max(),
            "indicadores": sorted(df["indicador"].dropna().unique().tolist()),
            "unidades": sorted(df["unidad"].dropna().unique().tolist()),
        }
    )


@app.get("/financials/banks")
def listar_bancos() -> dict[str, Any]:
    """
    Lista bancos disponibles en el dataset.
    """

    df = cargar_dataset_financiero()

    bancos = sorted(df["banco_estandarizado"].dropna().unique().tolist())

    return {
        "total": len(bancos),
        "bancos": bancos,
    }


@app.get("/financials/periods")
def listar_periodos() -> dict[str, Any]:
    """
    Lista periodos disponibles en el dataset.
    """

    df = cargar_dataset_financiero()

    periodos = sorted(df["periodo"].dropna().unique().tolist())
    anios = sorted(df["anio"].dropna().astype(int).unique().tolist())

    return {
        "total_periodos": len(periodos),
        "periodo_min": periodos[0] if periodos else None,
        "periodo_max": periodos[-1] if periodos else None,
        "anios": anios,
        "periodos": periodos,
    }


@app.get("/financials/metrics")
def listar_indicadores() -> dict[str, Any]:
    """
    Lista indicadores financieros disponibles y alias permitidos.
    """

    return {
        "indicadores": sorted(INDICADORES_VALIDOS),
        "alias": ALIAS_INDICADORES,
        "nota": "En morosidad, menor es mejor. En los demás indicadores principales, mayor suele ser mejor.",
    }


# =============================================================================
# 7. Endpoints financieros principales
# =============================================================================

@app.get("/financials/bank")
def obtener_kpis_banco(
    name: str = Query(..., description="Nombre del banco. Ejemplo: PICHINCHA"),
    period: str | None = Query(None, description="Periodo YYYY-MM. Si se omite, usa el último periodo disponible del banco."),
) -> dict[str, Any]:
    """
    Devuelve todos los KPIs disponibles de un banco para un periodo.

    Ejemplo:
        GET /financials/bank?name=pichincha
        GET /financials/bank?name=pichincha&period=2025-12
    """

    df = cargar_dataset_financiero()

    banco = normalizar_texto(name)

    df_banco = df[df["banco_estandarizado"] == banco].copy()

    if df_banco.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "Banco no encontrado.",
                "banco_recibido": name,
                "sugerencia": "Consulta /financials/banks para ver bancos disponibles.",
            },
        )

    if period is None:
        period = df_banco["periodo"].max()

    df_periodo = df_banco[df_banco["periodo"] == period].copy()

    if df_periodo.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "No hay datos para el banco en el periodo solicitado.",
                "banco": banco,
                "periodo": period,
                "periodos_disponibles_banco": sorted(df_banco["periodo"].dropna().unique().tolist()),
            },
        )

    registros = dataframe_to_json(
        df_periodo[["periodo", "banco_estandarizado", "indicador", "valor", "unidad", "sentido"]]
        .sort_values("indicador")
    )

    kpis = {
        fila["indicador"]: {
            "valor": fila["valor"],
            "unidad": fila["unidad"],
            "sentido": fila["sentido"],
        }
        for fila in registros
    }

    return {
        "banco": banco,
        "periodo": period,
        "kpis": kpis,
        "registros": registros,
    }


@app.get("/financials/history")
def obtener_historial_banco(
    name: str = Query(..., description="Nombre del banco. Ejemplo: PICHINCHA"),
    metric: str = Query(..., description="Indicador o alias. Ejemplo: assets, roe, morosidad, solvencia"),
    year: int | None = Query(None, description="Año opcional para filtrar. Ejemplo: 2025"),
) -> dict[str, Any]:
    """
    Devuelve la serie histórica de un KPI para un banco.
    """

    df = cargar_dataset_financiero()

    banco = normalizar_texto(name)
    indicador = normalizar_indicador(metric)

    filtro = (
        (df["banco_estandarizado"] == banco)
        & (df["indicador"] == indicador)
    )

    if year is not None:
        filtro = filtro & (df["anio"] == year)

    serie = df[filtro].copy().sort_values("periodo")

    if serie.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "No se encontró historial para los filtros enviados.",
                "banco": banco,
                "indicador": indicador,
                "year": year,
            },
        )

    return {
        "banco": banco,
        "indicador": indicador,
        "year": year,
        "total": int(len(serie)),
        "data": dataframe_to_json(
            serie[["periodo", "anio", "mes", "banco_estandarizado", "indicador", "valor", "unidad", "sentido"]]
        ),
    }


@app.get("/financials/rank")
def obtener_ranking(
    metric: str = Query(..., description="Indicador o alias. Ejemplo: assets, roe, morosidad, solvencia"),
    period: str | None = Query(None, description="Periodo YYYY-MM. Si se omite, usa el último periodo disponible del indicador."),
    year: int | None = Query(None, description="Año para ranking anual promedio. No usar junto con period."),
    top: int = Query(24, ge=1, le=100, description="Número de bancos a devolver."),
) -> dict[str, Any]:
    """
    Devuelve ranking de bancos por indicador.

    Ejemplos:
        GET /financials/rank?metric=assets
        GET /financials/rank?metric=roe&period=2025-12&top=10
        GET /financials/rank?metric=morosidad&year=2025&top=10
    """

    if period is not None and year is not None:
        raise HTTPException(
            status_code=400,
            detail="Usa period o year, pero no ambos en la misma consulta.",
        )

    df = cargar_dataset_financiero()
    indicador = normalizar_indicador(metric)

    if year is not None:
        base = (
            df[(df["indicador"] == indicador) & (df["anio"] == year)]
            .groupby(["anio", "banco_estandarizado", "indicador", "unidad", "sentido"], dropna=False)
            .agg(valor=("valor", "mean"))
            .reset_index()
        )
        contexto = {"tipo": "ranking_anual_promedio", "year": year}

    else:
        df_indicador = df[df["indicador"] == indicador].copy()

        if df_indicador.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No existen datos para el indicador {indicador}.",
            )

        if period is None:
            period = df_indicador["periodo"].max()

        base = df_indicador[df_indicador["periodo"] == period].copy()
        contexto = {"tipo": "ranking_mensual", "period": period}

    base = base[base["valor"].notna()].copy()

    if base.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "No hay datos para construir el ranking.",
                "indicador": indicador,
                "period": period,
                "year": year,
            },
        )

    ascendente = indicador in INDICADORES_MENOR_ES_MEJOR

    base = base.sort_values("valor", ascending=ascendente).reset_index(drop=True)
    base["ranking"] = base.index + 1

    resultado = base.head(top).copy()

    columnas = [
        c for c in [
            "ranking",
            "periodo",
            "anio",
            "banco_estandarizado",
            "indicador",
            "valor",
            "unidad",
            "sentido",
        ]
        if c in resultado.columns
    ]

    return {
        "indicador": indicador,
        "orden": "ascendente_menor_es_mejor" if ascendente else "descendente_mayor_es_mejor",
        "contexto": contexto,
        "top": top,
        "total_bancos_ranking": int(len(base)),
        "data": dataframe_to_json(resultado[columnas]),
    }


@app.get("/financials/system-average")
def promedio_sistema(
    metric: str = Query(..., description="Indicador o alias. Ejemplo: assets, roe, morosidad, solvencia"),
    period: str | None = Query(None, description="Periodo YYYY-MM opcional."),
    year: int | None = Query(None, description="Año opcional."),
) -> dict[str, Any]:
    """
    Devuelve promedio del sistema para un indicador.
    """

    if period is not None and year is not None:
        raise HTTPException(status_code=400, detail="Usa period o year, pero no ambos.")

    df = cargar_dataset_financiero()
    indicador = normalizar_indicador(metric)

    base = df[df["indicador"] == indicador].copy()

    if period is not None:
        base = base[base["periodo"] == period].copy()

    if year is not None:
        base = base[base["anio"] == year].copy()

    if base.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "No hay datos para calcular promedio.",
                "indicador": indicador,
                "period": period,
                "year": year,
            },
        )

    promedio = base["valor"].mean()

    return limpiar_json(
        {
            "indicador": indicador,
            "period": period,
            "year": year,
            "promedio_sistema": promedio,
            "unidad": base["unidad"].dropna().iloc[0] if not base["unidad"].dropna().empty else None,
            "bancos_con_dato": base["banco_estandarizado"].nunique(),
        }
    )


# =============================================================================
# 8. Endpoints de modelos y score
# =============================================================================

@app.get("/financials/score")
def obtener_score(
    name: str | None = Query(None, description="Nombre del banco opcional. Ejemplo: PICHINCHA"),
    year: int | None = Query(None, description="Año opcional. Si se omite, usa el último año disponible."),
    top: int = Query(24, ge=1, le=100, description="Top N si no se envía banco."),
) -> dict[str, Any]:
    """
    Consulta el score inteligente de salud financiera.

    Requiere haber ejecutado:
        03_cuadernos/04_score_salud_bancaria_v2.ipynb
    """

    df_score = cargar_resultado_modelo("score_salud_bancaria")

    if df_score.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "No se encontró score_salud_bancaria. "
                "Ejecuta 04_score_salud_bancaria_v2.ipynb."
            ),
        )

    df_score = df_score.copy()
    df_score["banco_estandarizado"] = df_score["banco_estandarizado"].astype(str).str.strip().str.upper()
    df_score["score_salud"] = pd.to_numeric(df_score["score_salud"], errors="coerce")

    if "anio" in df_score.columns:
        df_score["anio"] = pd.to_numeric(df_score["anio"], errors="coerce")
        if year is None:
            year = int(df_score["anio"].max())
        df_score = df_score[df_score["anio"] == year].copy()

    if df_score.empty:
        raise HTTPException(
            status_code=404,
            detail={"mensaje": "No existe score para el año solicitado.", "year": year},
        )

    if name is not None:
        banco = normalizar_texto(name)
        fila = df_score[df_score["banco_estandarizado"] == banco].copy()

        if fila.empty:
            raise HTTPException(
                status_code=404,
                detail={
                    "mensaje": "No existe score para el banco solicitado.",
                    "banco": banco,
                    "year": year,
                },
            )

        return {
            "year": year,
            "banco": banco,
            "data": dataframe_to_json(fila),
        }

    df_score = df_score.sort_values("score_salud", ascending=False).head(top)

    return {
        "year": year,
        "top": top,
        "data": dataframe_to_json(df_score),
    }


@app.get("/financials/forecast")
def obtener_forecast(
    name: str = Query(..., description="Nombre del banco. Ejemplo: PICHINCHA"),
    metric: str = Query(..., description="Indicador o alias. Ejemplo: assets, roe, morosidad, solvencia"),
    include_history: bool = Query(True, description="Si True, incluye histórico ajustado además de proyección."),
) -> dict[str, Any]:
    """
    Consulta proyecciones Prophet para banco e indicador.

    Requiere haber ejecutado:
        03_cuadernos/03_modelado_ml.ipynb
    """

    df_forecast = cargar_resultado_modelo("prophet_forecast")

    if df_forecast.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "No se encontró prophet_forecast. "
                "Ejecuta 03_modelado_ml.ipynb con Prophet habilitado."
            ),
        )

    banco = normalizar_texto(name)
    indicador = normalizar_indicador(metric)

    df_forecast = df_forecast.copy()
    df_forecast["banco_estandarizado"] = df_forecast["banco_estandarizado"].astype(str).str.strip().str.upper()
    df_forecast["indicador"] = df_forecast["indicador"].astype(str).str.strip().str.lower()

    filtro = (
        (df_forecast["banco_estandarizado"] == banco)
        & (df_forecast["indicador"] == indicador)
    )

    if not include_history and "tipo" in df_forecast.columns:
        filtro = filtro & (df_forecast["tipo"] == "proyeccion")

    resultado = df_forecast[filtro].copy()

    if resultado.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "No se encontró forecast para los filtros enviados.",
                "banco": banco,
                "indicador": indicador,
            },
        )

    columnas = [
        c for c in [
            "periodo",
            "anio",
            "mes",
            "banco_estandarizado",
            "indicador",
            "valor_real",
            "yhat",
            "yhat_lower",
            "yhat_upper",
            "trend",
            "tipo",
        ]
        if c in resultado.columns
    ]

    resultado = resultado.sort_values("periodo")

    return {
        "banco": banco,
        "indicador": indicador,
        "include_history": include_history,
        "total": int(len(resultado)),
        "data": dataframe_to_json(resultado[columnas]),
    }


# =============================================================================
# 9. Ejecución directa opcional
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_financiera:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
