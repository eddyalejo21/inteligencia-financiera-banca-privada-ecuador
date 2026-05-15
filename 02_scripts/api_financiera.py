
"""
API mínima para Score Inteligente del Sistema de Inteligencia Financiera Bancaria.

Archivo sugerido:
    02_scripts/api_financiera_minimal.py

Ejecución local:
    python -m uvicorn api_financiera_minimal:app --reload --app-dir 02_scripts

Ejecución Render:
    python -m uvicorn api_financiera_minimal:app --host 0.0.0.0 --port $PORT --app-dir 02_scripts

Endpoints:
    GET /health
    GET /banks
    GET /score?name=PICHINCHA&year=2026
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="API mínima · Score Financiero Bancario",
    description="API mínima para consultar bancos y score inteligente desde el dashboard.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def encontrar_raiz_proyecto() -> Path:
    """
    Busca la raíz del proyecto encontrando la carpeta 01_datos_procesados.
    Funciona ejecutando desde la raíz o desde 02_scripts.
    """
    actual = Path.cwd().resolve()
    archivo_actual = Path(__file__).resolve()

    candidatos = [actual] + list(actual.parents) + [archivo_actual.parent] + list(archivo_actual.parents)

    for ruta in candidatos:
        if (ruta / "01_datos_procesados").exists():
            return ruta

    raise FileNotFoundError(
        "No se encontró la carpeta 01_datos_procesados. "
        "Ejecuta la API desde la raíz del proyecto."
    )


def limpiar_json(valor: Any) -> Any:
    """
    Convierte NaN, NumPy y Pandas types a valores compatibles con JSON.
    """
    if isinstance(valor, dict):
        return {k: limpiar_json(v) for k, v in valor.items()}

    if isinstance(valor, list):
        return [limpiar_json(v) for v in valor]

    if pd.isna(valor):
        return None

    if isinstance(valor, np.integer):
        return int(valor)

    if isinstance(valor, np.floating):
        return float(valor)

    if isinstance(valor, pd.Timestamp):
        return valor.isoformat()

    return valor


@lru_cache(maxsize=1)
def cargar_dataset_financiero() -> pd.DataFrame:
    """
    Carga el dataset financiero limpio para validar health y listar bancos.
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
            "No existe dataset_financiero_limpio.parquet ni dataset_financiero_limpio.csv."
        )

    df = df.copy()
    df["banco_estandarizado"] = df["banco_estandarizado"].astype(str).str.strip().str.upper()
    df["periodo"] = df["periodo"].astype(str).str.strip()
    df["indicador"] = df["indicador"].astype(str).str.strip().str.lower()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["periodo_dt"] = pd.to_datetime(df["periodo"] + "-01", errors="coerce")
    df["anio"] = df["periodo_dt"].dt.year

    return df


@lru_cache(maxsize=1)
def cargar_score() -> pd.DataFrame:
    """
    Carga el score inteligente generado por 04_score_salud_bancaria_v2.ipynb.
    """
    raiz = encontrar_raiz_proyecto()
    carpeta = raiz / "01_datos_procesados" / "modelos"

    ruta_parquet = carpeta / "score_salud_bancaria.parquet"
    ruta_csv = carpeta / "score_salud_bancaria.csv"

    if ruta_parquet.exists():
        df = pd.read_parquet(ruta_parquet)
    elif ruta_csv.exists():
        df = pd.read_csv(ruta_csv)
    else:
        raise FileNotFoundError(
            "No existe score_salud_bancaria.parquet ni score_salud_bancaria.csv. "
            "Ejecuta 04_score_salud_bancaria_v2.ipynb."
        )

    df = df.copy()
    df["banco_estandarizado"] = df["banco_estandarizado"].astype(str).str.strip().str.upper()
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")
    df["score_salud"] = pd.to_numeric(df["score_salud"], errors="coerce")

    return df


def construir_lectura_prophet(fila: pd.Series) -> dict[str, Any]:
    """
    Construye un resumen específico de Prophet usando cambios proyectados
    que ya vienen en score_salud_bancaria.
    """
    cambios = {
        "activos_pct": fila.get("cambio_proyectado_pct_activos_totales"),
        "roe_puntos": fila.get("cambio_proyectado_roe"),
        "morosidad_puntos": fila.get("cambio_proyectado_morosidad"),
        "solvencia_puntos": fila.get("cambio_proyectado_solvencia_proxy"),
    }

    partes: list[str] = []

    activos = cambios["activos_pct"]
    if pd.notna(activos):
        if activos > 0:
            partes.append(f"Prophet proyecta crecimiento de activos cercano a {activos:.2f}%.")
        elif activos < 0:
            partes.append(f"Prophet proyecta contracción de activos cercana a {abs(activos):.2f}%.")
        else:
            partes.append("Prophet proyecta activos prácticamente estables.")

    roe = cambios["roe_puntos"]
    if pd.notna(roe):
        if roe > 0:
            partes.append(f"El ROE proyectado mejora en {roe:.2f} puntos porcentuales.")
        elif roe < 0:
            partes.append(f"El ROE proyectado disminuye en {abs(roe):.2f} puntos porcentuales.")

    mora = cambios["morosidad_puntos"]
    if pd.notna(mora):
        if mora > 0:
            partes.append(f"La morosidad proyectada aumenta en {mora:.2f} puntos porcentuales; requiere seguimiento.")
        elif mora < 0:
            partes.append(f"La morosidad proyectada disminuye en {abs(mora):.2f} puntos porcentuales.")
        else:
            partes.append("La morosidad proyectada se mantiene estable.")

    solvencia = cambios["solvencia_puntos"]
    if pd.notna(solvencia):
        if solvencia > 0:
            partes.append(f"La solvencia proxy proyectada mejora en {solvencia:.2f} puntos porcentuales.")
        elif solvencia < 0:
            partes.append(f"La solvencia proxy proyectada cae en {abs(solvencia):.2f} puntos porcentuales.")

    if not partes:
        partes.append(
            "Este año no incorpora componentes Prophet o no existen proyecciones suficientes para el banco seleccionado."
        )

    return limpiar_json(
        {
            "cambios": cambios,
            "interpretacion": " ".join(partes),
        }
    )


@app.get("/health")
def health() -> dict[str, Any]:
    """
    Verifica si la API puede leer el dataset limpio y el score.
    """
    try:
        df = cargar_dataset_financiero()
        score = cargar_score()

        return limpiar_json(
            {
                "status": "ok",
                "dataset": {
                    "filas": len(df),
                    "bancos": df["banco_estandarizado"].nunique(),
                    "periodos": df["periodo"].nunique(),
                    "anio_min": int(df["anio"].min()) if df["anio"].notna().any() else None,
                    "anio_max": int(df["anio"].max()) if df["anio"].notna().any() else None,
                },
                "score": {
                    "filas": len(score),
                    "anios": sorted(score["anio"].dropna().astype(int).unique().tolist()),
                },
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "mensaje": "La API no pudo leer los datos requeridos.",
                "detalle": repr(e),
            },
        )


@app.get("/banks")
def banks() -> dict[str, Any]:
    """
    Lista bancos disponibles para usar en el dashboard.
    """
    df = cargar_dataset_financiero()
    bancos = sorted(df["banco_estandarizado"].dropna().unique().tolist())

    return {
        "total": len(bancos),
        "bancos": bancos,
    }


@app.get("/score")
def score(
    name: str = Query(..., description="Nombre del banco. Ejemplo: PICHINCHA"),
    year: int | None = Query(None, description="Año del score. Si se omite, usa el último año disponible."),
) -> dict[str, Any]:
    """
    Devuelve score inteligente, componentes e interpretación ejecutiva.

    Este endpoint está pensado para ser consumido por la pestaña Score Inteligente del dashboard.
    """
    df_score = cargar_score()

    banco = str(name).strip().upper()

    if year is None:
        year = int(df_score["anio"].max())

    base_year = df_score[df_score["anio"] == year].copy()

    if base_year.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "No existe score para el año solicitado.",
                "year": year,
                "anios_disponibles": sorted(df_score["anio"].dropna().astype(int).unique().tolist()),
            },
        )

    fila = base_year[base_year["banco_estandarizado"] == banco].copy()

    if fila.empty:
        raise HTTPException(
            status_code=404,
            detail={
                "mensaje": "No existe score para el banco y año solicitados.",
                "banco": banco,
                "year": year,
                "bancos_disponibles": sorted(base_year["banco_estandarizado"].dropna().unique().tolist()),
            },
        )

    fila = fila.iloc[0]

    componentes = {
        "roe_real_vs_estimado": fila.get("puntaje_roe_modelo"),
        "perfil_kmeans": fila.get("puntaje_cluster"),
        "tendencia_futura": fila.get("puntaje_tendencia_general"),
        "morosidad_proyectada": fila.get("puntaje_morosidad_proyectada"),
        "solvencia_proyectada": fila.get("puntaje_solvencia_proyectada"),
    }

    ranking = None
    if "ranking_score" in base_year.columns:
        ranking = fila.get("ranking_score")
    else:
        base_year = base_year.sort_values("score_salud", ascending=False).reset_index(drop=True)
        ranking = int(base_year.index[base_year["banco_estandarizado"] == banco][0]) + 1

    respuesta = {
        "banco": banco,
        "year": year,
        "score_salud": fila.get("score_salud"),
        "lectura_score": fila.get("lectura_score"),
        "ranking_score": ranking,
        "tipo_score": fila.get("tipo_score"),
        "perfil_cluster": fila.get("perfil_cluster"),
        "componentes": componentes,
        "roe": {
            "roe_real": fila.get("roe_real"),
            "roe_estimado": fila.get("roe_estimado"),
            "error_roe": fila.get("error_roe"),
        },
        "prophet": construir_lectura_prophet(fila),
        "analisis_ejecutivo": fila.get("analisis_ejecutivo"),
    }

    return limpiar_json(respuesta)
