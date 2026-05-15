
# ============================================================
# Dashboard Storytelling
# Sistema de Inteligencia Financiera Bancaria
# ============================================================
# Ejecutar desde la raíz del proyecto:
# streamlit run 02_scripts/app_dashboard_storytelling.py
# ============================================================

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ============================================================
# Configuración visual general
# ============================================================

st.set_page_config(
    page_title="Inteligencia Financiera Bancaria",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLOR_PRINCIPAL = "#2563EB"
COLOR_SECUNDARIO = "#94A3B8"
COLOR_TEXTO = "#0F172A"
COLOR_SUAVE = "#F8FAFC"
COLOR_POSITIVO = "#16A34A"
COLOR_ALERTA = "#EA580C"
COLOR_NEGATIVO = "#DC2626"

MESES_ES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

KPI_CONFIG = {
    "activos_totales": {
        "label": "Activos",
        "label_largo": "Activos totales",
        "unidad": "millones_usd",
        "formato": "dinero",
        "orden_ascendente": False,
        "sentido": "mayor_es_tamano",
        "color": COLOR_PRINCIPAL,
        "mensaje": "Mide tamaño financiero y capacidad de escala.",
    },
    "roe": {
        "label": "ROE",
        "label_largo": "ROE",
        "unidad": "porcentaje",
        "formato": "porcentaje",
        "orden_ascendente": False,
        "sentido": "mayor_es_mejor",
        "color": "#7C3AED",
        "mensaje": "Mide rentabilidad sobre patrimonio.",
    },
    "morosidad": {
        "label": "Morosidad",
        "label_largo": "Morosidad",
        "unidad": "porcentaje",
        "formato": "porcentaje",
        "orden_ascendente": True,
        "sentido": "menor_es_mejor",
        "color": COLOR_NEGATIVO,
        "mensaje": "Mide calidad de cartera; menor es mejor.",
    },
    "solvencia_proxy": {
        "label": "Solvencia",
        "label_largo": "Solvencia proxy",
        "unidad": "porcentaje",
        "formato": "porcentaje",
        "orden_ascendente": False,
        "sentido": "mayor_es_mejor",
        "color": COLOR_ALERTA,
        "mensaje": "Aproxima fortaleza patrimonial relativa.",
    },
}

KPI_PRINCIPALES = list(KPI_CONFIG.keys())
KPI_TODOS = ["activos_totales", "pasivos_totales", "patrimonio", "roe", "morosidad", "solvencia_proxy"]

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.25rem;
        font-weight: 850;
        color: #0F172A;
        margin-bottom: 0.15rem;
    }
    .subtitle {
        font-size: 1.02rem;
        color: #475569;
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1.32rem;
        font-weight: 850;
        color: #0F172A;
        margin-top: 0.25rem;
        margin-bottom: 0.25rem;
    }
    .section-note {
        color: #64748B;
        font-size: .94rem;
        margin-bottom: 1rem;
    }
    .insight-box {
        background: #EFF6FF;
        border-left: 5px solid #2563EB;
        border-radius: 14px;
        padding: 1rem 1.15rem;
        color: #0F172A;
        margin: 0.75rem 0 1.1rem 0;
    }
    .warning-box {
        background: #FFF7ED;
        border-left: 5px solid #EA580C;
        border-radius: 14px;
        padding: 1rem 1.15rem;
        color: #7C2D12;
        margin: 0.75rem 0 1.1rem 0;
    }
    .metric-card {
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        border-radius:18px;
        padding:16px 17px;
        box-shadow:0 8px 22px rgba(15,23,42,.045);
        min-height:124px;
    }
    .metric-label {color:#64748B;font-size:.84rem;font-weight:750;margin-bottom:.35rem;}
    .metric-value {color:#0F172A;font-size:1.55rem;font-weight:850;margin-bottom:.1rem;}
    .metric-caption {color:#64748B;font-size:.8rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Funciones de carga
# ============================================================

def encontrar_raiz_proyecto() -> Path:
    actual = Path.cwd().resolve()
    for ruta in [actual] + list(actual.parents):
        if (ruta / "01_datos_procesados").exists():
            return ruta

    script_path = Path(__file__).resolve()
    for ruta in [script_path.parent] + list(script_path.parents):
        if (ruta / "01_datos_procesados").exists():
            return ruta

    raise FileNotFoundError("No se encontró la carpeta 01_datos_procesados. Ejecuta desde la raíz del proyecto.")


@st.cache_data(show_spinner=False)
def cargar_dataset() -> pd.DataFrame:
    raiz = encontrar_raiz_proyecto()
    ruta_parquet = raiz / "01_datos_procesados" / "dataset_financiero_limpio.parquet"
    ruta_csv = raiz / "01_datos_procesados" / "dataset_financiero_limpio.csv"

    if ruta_parquet.exists():
        df = pd.read_parquet(ruta_parquet)
    elif ruta_csv.exists():
        df = pd.read_csv(ruta_csv)
    else:
        raise FileNotFoundError("No se encontró dataset_financiero_limpio.parquet ni dataset_financiero_limpio.csv.")

    df = df.copy()
    df["periodo"] = df["periodo"].astype(str).str.strip()
    df["banco_estandarizado"] = df["banco_estandarizado"].astype(str).str.strip().str.upper()
    df["indicador"] = df["indicador"].astype(str).str.strip().str.lower()
    df["unidad"] = df["unidad"].astype(str).str.strip().str.lower()
    df["sentido"] = df["sentido"].astype(str).str.strip().str.lower()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["periodo_dt"] = pd.to_datetime(df["periodo"] + "-01", errors="coerce")
    df["anio"] = df["periodo_dt"].dt.year
    df["mes"] = df["periodo_dt"].dt.month
    df["mes_nombre"] = df["mes"].map(MESES_ES)

    return df[df["indicador"].isin(KPI_TODOS)].copy()


@st.cache_data(show_spinner=False)
def preparar_datos_anuales(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["anio", "banco_estandarizado", "indicador"], dropna=False)
        .agg(
            valor=("valor", "mean"),
            unidad=("unidad", lambda s: s.dropna().iloc[0] if s.dropna().size else None),
            meses_con_dato=("valor", "count"),
        )
        .reset_index()
    )


@st.cache_data(show_spinner=False)
def cargar_resultado_modelo(nombre_base: str) -> pd.DataFrame | None:
    raiz = encontrar_raiz_proyecto()
    carpeta = raiz / "01_datos_procesados" / "modelos"

    ruta_parquet = carpeta / f"{nombre_base}.parquet"
    ruta_csv = carpeta / f"{nombre_base}.csv"

    if ruta_parquet.exists():
        return pd.read_parquet(ruta_parquet)

    if ruta_csv.exists():
        return pd.read_csv(ruta_csv)

    return None


def preparar_fecha_modelo(df_modelo: pd.DataFrame | None) -> pd.DataFrame | None:
    if df_modelo is None:
        return None

    df_tmp = df_modelo.copy()

    if "periodo_dt" in df_tmp.columns:
        df_tmp["periodo_dt"] = pd.to_datetime(df_tmp["periodo_dt"], errors="coerce")
    elif "periodo" in df_tmp.columns:
        df_tmp["periodo_dt"] = pd.to_datetime(df_tmp["periodo"].astype(str) + "-01", errors="coerce")

    if "ds" in df_tmp.columns:
        df_tmp["ds"] = pd.to_datetime(df_tmp["ds"], errors="coerce")

    if "anio" in df_tmp.columns:
        df_tmp["anio"] = pd.to_numeric(df_tmp["anio"], errors="coerce")

    if "banco_estandarizado" in df_tmp.columns:
        df_tmp["banco_estandarizado"] = df_tmp["banco_estandarizado"].astype(str).str.strip().str.upper()

    if "indicador" in df_tmp.columns:
        df_tmp["indicador"] = df_tmp["indicador"].astype(str).str.strip().str.lower()

    return df_tmp


# ============================================================
# Funciones de análisis y visualización
# ============================================================

def formato_valor(valor: float, indicador: str) -> str:
    if pd.isna(valor):
        return "N/D"
    if KPI_CONFIG[indicador]["formato"] == "dinero":
        return f"USD {valor:,.2f} M"
    if KPI_CONFIG[indicador]["formato"] == "porcentaje":
        return f"{valor:,.2f}%"
    return f"{valor:,.2f}"


def formato_delta(valor: float, indicador: str) -> str:
    if pd.isna(valor):
        return "N/D"
    unidad = "p.p." if KPI_CONFIG[indicador]["formato"] == "porcentaje" else "M"
    return f"{valor:+,.2f} {unidad}"


def tarjeta_html(label: str, value: str, caption: str = "") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-caption">{caption}</div>
    </div>
    """


def insight(texto: str, tipo: str = "normal") -> None:
    clase = "warning-box" if tipo == "warning" else "insight-box"
    st.markdown(f"<div class='{clase}'>{texto}</div>", unsafe_allow_html=True)


def ordenar_por_kpi(df_base: pd.DataFrame, indicador: str) -> pd.DataFrame:
    return df_base.sort_values("valor", ascending=KPI_CONFIG[indicador]["orden_ascendente"])


def ranking_anual(df_anual: pd.DataFrame, anio: int, indicador: str) -> pd.DataFrame:
    base = df_anual[
        (df_anual["anio"] == anio)
        & (df_anual["indicador"] == indicador)
        & (df_anual["valor"].notna())
    ].copy()
    base = ordenar_por_kpi(base, indicador).reset_index(drop=True)
    base["ranking"] = base.index + 1
    return base


def ranking_anual_historico(df_anual: pd.DataFrame, indicador: str) -> pd.DataFrame:
    partes = []
    for anio, grupo in df_anual[df_anual["indicador"] == indicador].groupby("anio"):
        grupo = grupo[grupo["valor"].notna()].copy()
        if grupo.empty:
            continue
        grupo = ordenar_por_kpi(grupo, indicador).reset_index(drop=True)
        grupo["ranking"] = grupo.index + 1
        partes.append(grupo)
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def promedio_sistema_mensual(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["periodo", "periodo_dt", "anio", "mes", "mes_nombre", "indicador"], dropna=False)
        .agg(promedio_sistema=("valor", "mean"))
        .reset_index()
    )


def promedio_sistema_anual(df_anual: pd.DataFrame) -> pd.DataFrame:
    return (
        df_anual.groupby(["anio", "indicador"], dropna=False)
        .agg(promedio_sistema=("valor", "mean"))
        .reset_index()
    )


def ultimo_periodo_disponible(df: pd.DataFrame, anio: int, indicador: str) -> str | None:
    periodos = (
        df[(df["anio"] == anio) & (df["indicador"] == indicador)]["periodo"]
        .dropna()
        .sort_values()
        .unique()
    )
    return None if len(periodos) == 0 else periodos[-1]


def pivot_anual(df_anual: pd.DataFrame, anio: int) -> pd.DataFrame:
    tabla = (
        df_anual[df_anual["anio"] == anio]
        .pivot_table(index="banco_estandarizado", columns="indicador", values="valor", aggfunc="first")
        .reset_index()
    )
    for indicador in KPI_TODOS:
        if indicador not in tabla.columns:
            tabla[indicador] = np.nan
    return tabla[["banco_estandarizado"] + KPI_TODOS]


def clasificar_riesgo(row: pd.Series, mor_prom: float, solv_prom: float, roe_prom: float) -> str:
    if pd.isna(row.get("morosidad")) or pd.isna(row.get("solvencia_proxy")) or pd.isna(row.get("roe")):
        return "Sin datos suficientes"
    if row["morosidad"] > mor_prom and row["solvencia_proxy"] < solv_prom and row["roe"] < roe_prom:
        return "Mayor riesgo relativo"
    if row["morosidad"] <= mor_prom and row["solvencia_proxy"] >= solv_prom and row["roe"] >= roe_prom:
        return "Mejor posición relativa"
    return "Zona intermedia"


def contar_tendencia(serie: pd.DataFrame, indicador: str) -> str:
    serie = serie.sort_values("anio").dropna(subset=["valor"])
    if len(serie) < 2:
        return "No hay suficiente historia para describir tendencia."
    primero = serie["valor"].iloc[0]
    ultimo = serie["valor"].iloc[-1]
    cambio = ultimo - primero

    if indicador == "morosidad":
        if cambio < 0:
            return "La tendencia histórica mejora porque la morosidad baja frente al inicio de la serie."
        if cambio > 0:
            return "La tendencia histórica se deteriora porque la morosidad sube frente al inicio de la serie."
    else:
        if cambio > 0:
            return "La tendencia histórica es creciente frente al inicio de la serie."
        if cambio < 0:
            return "La tendencia histórica es decreciente frente al inicio de la serie."

    return "La tendencia histórica se mantiene prácticamente estable."


def grafico_linea_banco_vs_sistema(mensual: pd.DataFrame, banco: str, indicador: str, anio: int) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=mensual["mes_nombre"],
            y=mensual["promedio_sistema"],
            mode="lines+markers",
            name="Promedio sistema",
            line=dict(color=COLOR_SECUNDARIO, width=3, dash="dash"),
            marker=dict(size=7),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=mensual["mes_nombre"],
            y=mensual["valor"],
            mode="lines+markers",
            name=banco,
            line=dict(color=KPI_CONFIG[indicador]["color"], width=4),
            marker=dict(size=9),
        )
    )

    mensual_gap = mensual.dropna(subset=["valor", "promedio_sistema"]).copy()
    if not mensual_gap.empty:
        mensual_gap["gap_abs"] = (mensual_gap["valor"] - mensual_gap["promedio_sistema"]).abs()
        punto = mensual_gap.sort_values("gap_abs", ascending=False).iloc[0]
        fig.add_annotation(
            x=punto["mes_nombre"],
            y=punto["valor"],
            text="Mayor diferencia",
            showarrow=True,
            arrowhead=2,
            ax=20,
            ay=-45,
            bgcolor="#FFFFFF",
            bordercolor=KPI_CONFIG[indicador]["color"],
            borderwidth=1,
        )

    fig.update_layout(
        height=470,
        title=f"{KPI_CONFIG[indicador]['label_largo']} · {banco} vs sistema · {anio}",
        xaxis_title="Mes",
        yaxis_title="Millones USD" if KPI_CONFIG[indicador]["formato"] == "dinero" else "Porcentaje",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=65, b=10),
        legend=dict(orientation="h", y=1.12),
        plot_bgcolor="white",
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E2E8F0")
    return fig


def grafico_ranking(ranking_top: pd.DataFrame, indicador: str, top_n: int) -> go.Figure:
    datos = ranking_top.sort_values("ranking", ascending=False).copy()

    colores = [KPI_CONFIG[indicador]["color"] if r == 1 else "#CBD5E1" for r in datos["ranking"]]
    texto = [formato_valor(v, indicador) for v in datos["valor"]]

    fig = go.Figure(
        go.Bar(
            x=datos["valor"],
            y=datos["banco_estandarizado"],
            orientation="h",
            marker=dict(color=colores),
            text=texto,
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Valor: %{x:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        height=470,
        title=f"Top {top_n} por {KPI_CONFIG[indicador]['label_largo']}",
        xaxis_title="Millones USD" if KPI_CONFIG[indicador]["formato"] == "dinero" else "Porcentaje",
        yaxis_title="",
        margin=dict(l=10, r=40, t=65, b=10),
        plot_bgcolor="white",
    )
    fig.update_xaxes(gridcolor="#E2E8F0")
    fig.update_yaxes(showgrid=False)

    return fig


def consultar_score_api(api_url: str, banco: str, anio: int) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = requests.get(
            f"{api_url.rstrip('/')}/score",
            params={"name": banco, "year": anio},
            timeout=8,
        )
        if response.status_code != 200:
            return None, f"API respondió {response.status_code}: {response.text[:300]}"
        return response.json(), None
    except Exception as e:
        return None, repr(e)


# ============================================================
# Carga de datos
# ============================================================

try:
    df = cargar_dataset()
    df_anual = preparar_datos_anuales(df)
except Exception as e:
    st.error(f"No se pudo cargar el dataset: {e}")
    st.stop()

anios = sorted(df["anio"].dropna().astype(int).unique())
bancos = sorted(df["banco_estandarizado"].dropna().unique())

if not anios or not bancos:
    st.error("El dataset no contiene años o bancos suficientes.")
    st.stop()

anio_default = max(anios)
df_prom_mensual = promedio_sistema_mensual(df)
df_prom_anual = promedio_sistema_anual(df_anual)

df_roe_predicciones = preparar_fecha_modelo(cargar_resultado_modelo("modelo_roe_predicciones"))
df_roe_metricas = cargar_resultado_modelo("modelo_roe_metricas")
df_roe_importancia = cargar_resultado_modelo("modelo_roe_importancia_variables")

df_clusters = preparar_fecha_modelo(cargar_resultado_modelo("clusters_bancos_anual"))
df_clusters_resumen = cargar_resultado_modelo("clusters_resumen")

df_prophet_forecast = preparar_fecha_modelo(cargar_resultado_modelo("prophet_forecast"))
df_prophet_metricas = cargar_resultado_modelo("prophet_metricas_ajuste")


# ============================================================
# Encabezado
# ============================================================

st.markdown('<div class="main-title">Sistema de Inteligencia Financiera Bancaria</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Dashboard storytelling: comparación, rankings, riesgo, modelos ML, proyecciones y score inteligente.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Configuración")
    api_default = os.getenv("API_SCORE_URL", "https://inteligencia-financiera-banca-privada.onrender.com")
    api_url = st.text_input("URL API Score", value=api_default)
    st.caption("La pestaña Score Inteligente consume el endpoint `/score` de esta API.")

with st.expander("Cómo leer este dashboard", expanded=False):
    st.markdown(
        """
        Este dashboard está organizado para responder las preguntas principales del proyecto:
        **comparar bancos**, **rankear desempeño**, **detectar señales relativas de riesgo** y **agregar una lectura inteligente con modelos**.

        La lógica visual sigue principios de *storytelling con datos*: cada gráfico resalta el punto importante,
        reduce elementos innecesarios y acompaña la visualización con una interpretación breve.
        """
    )


tab_banco, tab_ranking, tab_riesgo, tab_modelo_roe, tab_clusters, tab_prophet, tab_score = st.tabs(
    [
        "Banco vs Sistema",
        "Ranking",
        "Riesgo financiero",
        "Modelo de ROE",
        "Cluster KMeans",
        "Proyecciones Prophet",
        "Score Inteligente",
    ]
)


# ============================================================
# 1. Banco vs Sistema
# ============================================================

with tab_banco:
    st.markdown('<div class="section-title">Banco vs Sistema</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Compara un banco contra el promedio del sistema y resalta dónde se separa más del conjunto.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1.2, 1, .75])
    with c1:
        banco_sel = st.selectbox("Banco", bancos, index=bancos.index("PICHINCHA") if "PICHINCHA" in bancos else 0)
    with c2:
        kpi_sel = st.selectbox("Indicador", KPI_PRINCIPALES, format_func=lambda x: KPI_CONFIG[x]["label_largo"])
    with c3:
        anio_sel = st.selectbox("Año", anios, index=anios.index(anio_default))

    ultimo_periodo = ultimo_periodo_disponible(df, anio_sel, kpi_sel)

    if ultimo_periodo is None:
        st.warning("No hay información para el banco/año/KPI seleccionado.")
    else:
        valor_banco = df[
            (df["periodo"] == ultimo_periodo)
            & (df["banco_estandarizado"] == banco_sel)
            & (df["indicador"] == kpi_sel)
        ]["valor"]

        valor_banco = valor_banco.iloc[0] if not valor_banco.empty else np.nan

        promedio = df[(df["periodo"] == ultimo_periodo) & (df["indicador"] == kpi_sel)]["valor"].mean()
        gap = valor_banco - promedio if pd.notna(valor_banco) and pd.notna(promedio) else np.nan

        rank = ranking_anual(df_anual, anio_sel, kpi_sel)
        fila_rank = rank[rank["banco_estandarizado"] == banco_sel]
        posicion = int(fila_rank["ranking"].iloc[0]) if not fila_rank.empty else None

        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(tarjeta_html(f"{KPI_CONFIG[kpi_sel]['label_largo']} · {ultimo_periodo}", formato_valor(valor_banco, kpi_sel), "Valor observado del banco"), unsafe_allow_html=True)
        m2.markdown(tarjeta_html("Promedio sistema", formato_valor(promedio, kpi_sel), "Referencia del sistema bancario"), unsafe_allow_html=True)
        m3.markdown(tarjeta_html("Diferencia vs sistema", formato_delta(gap, kpi_sel), "Banco menos promedio"), unsafe_allow_html=True)
        m4.markdown(tarjeta_html("Ranking anual", "N/D" if posicion is None else f"#{posicion}", f"de {len(rank)} bancos"), unsafe_allow_html=True)

        mensual_banco = df[
            (df["anio"] == anio_sel)
            & (df["banco_estandarizado"] == banco_sel)
            & (df["indicador"] == kpi_sel)
        ][["periodo", "mes", "mes_nombre", "valor"]].copy()

        mensual_sistema = df_prom_mensual[
            (df_prom_mensual["anio"] == anio_sel)
            & (df_prom_mensual["indicador"] == kpi_sel)
        ][["periodo", "mes", "mes_nombre", "promedio_sistema"]].copy()

        mensual = mensual_banco.merge(mensual_sistema, on=["periodo", "mes", "mes_nombre"], how="outer").sort_values("mes")

        fig = grafico_linea_banco_vs_sistema(mensual, banco_sel, kpi_sel, anio_sel)
        st.plotly_chart(fig, width="stretch")

        texto_gap = ""
        if pd.notna(gap):
            direccion = "por encima" if gap > 0 else "por debajo"
            if kpi_sel == "morosidad":
                lectura = "esto es favorable" if gap < 0 else "esto requiere seguimiento"
            else:
                lectura = "esto es favorable" if gap > 0 else "esto requiere seguimiento"
            texto_gap = f"En el último periodo disponible, **{banco_sel}** está **{direccion} del sistema** por {formato_delta(gap, kpi_sel)}; {lectura} para este KPI."

        anual_banco = df_anual[
            (df_anual["banco_estandarizado"] == banco_sel)
            & (df_anual["indicador"] == kpi_sel)
        ][["anio", "valor"]].copy()

        tendencia = contar_tendencia(anual_banco, kpi_sel)
        insight(f"{texto_gap} {tendencia}")

        anual_sistema = df_prom_anual[df_prom_anual["indicador"] == kpi_sel][["anio", "promedio_sistema"]].copy()

        fig_anual = go.Figure()
        fig_anual.add_trace(
            go.Scatter(
                x=anual_sistema["anio"],
                y=anual_sistema["promedio_sistema"],
                mode="lines+markers",
                name="Promedio sistema",
                line=dict(color=COLOR_SECUNDARIO, width=3, dash="dash"),
            )
        )
        fig_anual.add_trace(
            go.Scatter(
                x=anual_banco["anio"],
                y=anual_banco["valor"],
                mode="lines+markers",
                name=banco_sel,
                line=dict(color=KPI_CONFIG[kpi_sel]["color"], width=4),
            )
        )
        fig_anual.update_layout(
            height=430,
            title=f"Evolución anual · {KPI_CONFIG[kpi_sel]['label_largo']}",
            xaxis_title="Año",
            yaxis_title="Millones USD" if KPI_CONFIG[kpi_sel]["formato"] == "dinero" else "Porcentaje",
            hovermode="x unified",
            margin=dict(l=10, r=10, t=65, b=10),
            legend=dict(orientation="h", y=1.12),
            plot_bgcolor="white",
        )
        fig_anual.update_yaxes(gridcolor="#E2E8F0")
        fig_anual.update_xaxes(showgrid=False)
        st.plotly_chart(fig_anual, width="stretch")


# ============================================================
# 2. Ranking
# ============================================================

with tab_ranking:
    st.markdown('<div class="section-title">Ranking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Identifica líderes y muestra si el liderazgo es persistente o circunstancial.</div>',
        unsafe_allow_html=True,
    )

    r1, r2, r3 = st.columns([1, .75, .75])
    with r1:
        kpi_rank = st.selectbox("Indicador", KPI_PRINCIPALES, format_func=lambda x: KPI_CONFIG[x]["label_largo"], key="rank_kpi")
    with r2:
        anio_rank = st.selectbox("Año", anios, index=anios.index(anio_default), key="rank_anio")
    with r3:
        top_n = st.slider("Top N", min_value=3, max_value=10, value=10, key="rank_top")

    rank_year = ranking_anual(df_anual, anio_rank, kpi_rank)
    rank_top = rank_year.head(top_n).copy()

    if rank_top.empty:
        st.warning("No hay datos para construir el ranking.")
    else:
        lider = rank_top.iloc[0]
        segundo = rank_top.iloc[1] if len(rank_top) > 1 else None
        fig_rank = grafico_ranking(rank_top, kpi_rank, top_n)
        st.plotly_chart(fig_rank, width="stretch")

        if segundo is not None:
            brecha = lider["valor"] - segundo["valor"]
            if kpi_rank == "morosidad":
                brecha = segundo["valor"] - lider["valor"]
            insight(
                f"El líder del ranking es **{lider['banco_estandarizado']}** con {formato_valor(lider['valor'], kpi_rank)}. "
                f"La brecha frente al segundo lugar es de {formato_valor(abs(brecha), kpi_rank)}. "
                f"Recuerda: en **morosidad** el menor valor es mejor; en los demás KPI, el mayor valor lidera."
            )

        bancos_top = rank_top["banco_estandarizado"].tolist()
        hist_top = df_anual[
            (df_anual["indicador"] == kpi_rank)
            & (df_anual["banco_estandarizado"].isin(bancos_top))
        ].copy()

        fig_hist = go.Figure()
        for banco in bancos_top:
            serie = hist_top[hist_top["banco_estandarizado"] == banco].sort_values("anio")
            color = KPI_CONFIG[kpi_rank]["color"] if banco == lider["banco_estandarizado"] else "#CBD5E1"
            ancho = 4 if banco == lider["banco_estandarizado"] else 2
            fig_hist.add_trace(
                go.Scatter(
                    x=serie["anio"],
                    y=serie["valor"],
                    mode="lines+markers",
                    name=banco,
                    line=dict(color=color, width=ancho),
                    opacity=1 if banco == lider["banco_estandarizado"] else 0.65,
                )
            )
        fig_hist.update_layout(
            height=480,
            title=f"Evolución histórica del Top {top_n} actual",
            xaxis_title="Año",
            yaxis_title="Millones USD" if KPI_CONFIG[kpi_rank]["formato"] == "dinero" else "Porcentaje",
            hovermode="x unified",
            margin=dict(l=10, r=10, t=65, b=10),
            plot_bgcolor="white",
        )
        fig_hist.update_yaxes(gridcolor="#E2E8F0")
        st.plotly_chart(fig_hist, width="stretch")


# ============================================================
# 3. Riesgo financiero
# ============================================================

with tab_riesgo:
    st.markdown('<div class="section-title">Riesgo financiero</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Cruza morosidad, solvencia y ROE para identificar bancos que requieren seguimiento relativo.</div>',
        unsafe_allow_html=True,
    )

    anio_riesgo = st.selectbox("Año", anios, index=anios.index(anio_default), key="riesgo_anio")

    riesgo = pivot_anual(df_anual, anio_riesgo)
    mor_prom = riesgo["morosidad"].mean()
    solv_prom = riesgo["solvencia_proxy"].mean()
    roe_prom = riesgo["roe"].mean()
    riesgo["senal"] = riesgo.apply(lambda row: clasificar_riesgo(row, mor_prom, solv_prom, roe_prom), axis=1)

    colores = riesgo["senal"].map(
        {
            "Mayor riesgo relativo": COLOR_NEGATIVO,
            "Mejor posición relativa": COLOR_POSITIVO,
            "Zona intermedia": "#CBD5E1",
            "Sin datos suficientes": "#94A3B8",
        }
    )

    fig_r = go.Figure()

    fig_r.add_trace(
        go.Scatter(
            x=riesgo["morosidad"],
            y=riesgo["solvencia_proxy"],
            mode="markers+text",
            text=riesgo["banco_estandarizado"],
            textposition="top center",
            marker=dict(
                size=np.sqrt(riesgo["activos_totales"].fillna(0).clip(lower=0)) * 1.8 + 8,
                color=colores,
                opacity=0.78,
                line=dict(color="#0F172A", width=0.8),
            ),
            hovertemplate="<b>%{text}</b><br>Morosidad: %{x:.2f}%<br>Solvencia: %{y:.2f}%<extra></extra>",
            name="Bancos",
        )
    )

    fig_r.add_vline(x=mor_prom, line=dict(color=COLOR_SECUNDARIO, dash="dash", width=2))
    fig_r.add_hline(y=solv_prom, line=dict(color=COLOR_SECUNDARIO, dash="dash", width=2))

    fig_r.add_annotation(
        x=mor_prom,
        y=riesgo["solvencia_proxy"].max(),
        text="Morosidad promedio",
        showarrow=False,
        yshift=12,
        bgcolor="white",
    )
    fig_r.add_annotation(
        x=riesgo["morosidad"].max(),
        y=solv_prom,
        text="Solvencia promedio",
        showarrow=False,
        xshift=-10,
        bgcolor="white",
    )

    fig_r.update_layout(
        height=620,
        title=f"Mapa de riesgo relativo · {anio_riesgo}",
        xaxis_title="Morosidad (%) · menor es mejor",
        yaxis_title="Solvencia proxy (%) · mayor es mejor",
        margin=dict(l=10, r=10, t=65, b=10),
        plot_bgcolor="white",
    )
    fig_r.update_xaxes(gridcolor="#E2E8F0")
    fig_r.update_yaxes(gridcolor="#E2E8F0")
    st.plotly_chart(fig_r, width="stretch")

    total_alerta = int((riesgo["senal"] == "Mayor riesgo relativo").sum())
    insight(
        f"En {anio_riesgo}, **{total_alerta} banco(s)** caen en zona de mayor riesgo relativo: "
        "morosidad sobre el promedio, solvencia bajo el promedio y ROE bajo el promedio. "
        "Esta señal no es una calificación regulatoria; es una alerta exploratoria para revisión."
    )

    st.dataframe(
        riesgo[["banco_estandarizado", "activos_totales", "roe", "morosidad", "solvencia_proxy", "senal"]]
        .sort_values(["senal", "morosidad"], ascending=[True, False]),
        width="stretch",
        hide_index=True,
    )


# ============================================================
# 4. Modelo de ROE
# ============================================================

with tab_modelo_roe:
    st.markdown('<div class="section-title">Modelo de ROE · RandomForestRegressor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Compara ROE real vs ROE estimado para detectar desempeño superior o inferior a lo esperado.</div>',
        unsafe_allow_html=True,
    )

    if df_roe_predicciones is None or df_roe_metricas is None or df_roe_importancia is None:
        st.warning("No encuentro resultados del modelo ROE. Ejecuta 03_modelado_ml.ipynb.")
    else:
        roe_pred = df_roe_predicciones.copy()
        roe_pred["error_abs_roe"] = pd.to_numeric(roe_pred["error_abs_roe"], errors="coerce")

        bancos_roe = sorted(roe_pred["banco_estandarizado"].dropna().unique())
        anios_roe = sorted(roe_pred["anio"].dropna().astype(int).unique())

        c1, c2 = st.columns([1.2, .8])
        with c1:
            banco_roe = st.selectbox("Banco", bancos_roe, index=bancos_roe.index("PICHINCHA") if "PICHINCHA" in bancos_roe else 0, key="roe_banco")
        with c2:
            anio_roe = st.selectbox("Año", ["Todos"] + anios_roe, key="roe_anio")

        filtro_roe = roe_pred[roe_pred["banco_estandarizado"] == banco_roe].copy()
        if anio_roe != "Todos":
            filtro_roe = filtro_roe[filtro_roe["anio"] == int(anio_roe)].copy()

        if filtro_roe.empty:
            st.warning("No hay datos para el filtro seleccionado.")
        else:
            ultimo = filtro_roe.sort_values("periodo_dt").iloc[-1]
            error = ultimo["roe_real"] - ultimo["roe_estimado"]
            lectura = "por encima" if error > 0 else "por debajo"

            m1, m2, m3 = st.columns(3)
            m1.metric("ROE real reciente", f"{ultimo['roe_real']:,.2f}%")
            m2.metric("ROE estimado reciente", f"{ultimo['roe_estimado']:,.2f}%")
            m3.metric("Diferencia", f"{error:+,.2f} p.p.")

            fig_roe = go.Figure()
            fig_roe.add_trace(
                go.Scatter(
                    x=filtro_roe["periodo_dt"],
                    y=filtro_roe["roe_estimado"],
                    mode="lines",
                    name="ROE estimado",
                    line=dict(color=COLOR_SECUNDARIO, width=3, dash="dash"),
                )
            )
            fig_roe.add_trace(
                go.Scatter(
                    x=filtro_roe["periodo_dt"],
                    y=filtro_roe["roe_real"],
                    mode="lines+markers",
                    name="ROE real",
                    line=dict(color=COLOR_PRINCIPAL, width=4),
                    marker=dict(size=8),
                )
            )

            idx_error = filtro_roe["error_abs_roe"].idxmax()
            punto = filtro_roe.loc[idx_error]
            fig_roe.add_annotation(
                x=punto["periodo_dt"],
                y=punto["roe_real"],
                text="Mayor desviación",
                showarrow=True,
                arrowhead=2,
                ax=25,
                ay=-40,
                bgcolor="#FFFFFF",
                bordercolor=COLOR_PRINCIPAL,
            )

            fig_roe.update_layout(
                height=470,
                title=f"ROE real vs estimado · {banco_roe}",
                xaxis_title="Periodo",
                yaxis_title="ROE (%)",
                hovermode="x unified",
                margin=dict(l=10, r=10, t=65, b=10),
                legend=dict(orientation="h", y=1.12),
                plot_bgcolor="white",
            )
            fig_roe.update_yaxes(gridcolor="#E2E8F0")
            st.plotly_chart(fig_roe, width="stretch")

            insight(
                f"En el periodo más reciente del filtro, **{banco_roe}** tuvo un ROE real "
                f"**{lectura}** del ROE estimado por el modelo en {abs(error):.2f} puntos porcentuales. "
                "Esto ayuda a separar desempeño observado de desempeño esperado según sus variables financieras."
            )

            imp = df_roe_importancia.copy().sort_values("importancia", ascending=True)
            fig_imp = go.Figure(
                go.Bar(
                    x=imp["importancia"],
                    y=imp["variable"],
                    orientation="h",
                    marker=dict(color=[COLOR_PRINCIPAL if i == imp["importancia"].max() else "#CBD5E1" for i in imp["importancia"]]),
                    text=imp["importancia"].round(3),
                    textposition="outside",
                )
            )
            fig_imp.update_layout(
                height=360,
                title="Variable más influyente en la estimación del ROE",
                xaxis_title="Importancia relativa",
                yaxis_title="",
                margin=dict(l=10, r=40, t=65, b=10),
                plot_bgcolor="white",
            )
            st.plotly_chart(fig_imp, width="stretch")


# ============================================================
# 5. Cluster KMeans
# ============================================================

with tab_clusters:
    st.markdown('<div class="section-title">Cluster KMeans</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Segmenta bancos por comportamiento financiero similar y resalta el perfil dominante.</div>',
        unsafe_allow_html=True,
    )

    if df_clusters is None:
        st.warning("No encuentro clusters_bancos_anual. Ejecuta 03_modelado_ml.ipynb.")
    else:
        cl = df_clusters.copy()
        anios_cl = sorted(cl["anio"].dropna().astype(int).unique())
        anio_cl = st.selectbox("Año", anios_cl, index=len(anios_cl) - 1, key="cluster_anio")

        cl_anio = cl[cl["anio"] == anio_cl].copy()

        perfiles = cl_anio.groupby(["cluster", "perfil_cluster"], dropna=False).size().reset_index(name="bancos")
        perfil_dominante = perfiles.sort_values("bancos", ascending=False).iloc[0]

        fig_cl = go.Figure()

        for cluster, grupo in cl_anio.groupby("cluster"):
            fig_cl.add_trace(
                go.Scatter(
                    x=grupo["pca_1"],
                    y=grupo["pca_2"],
                    mode="markers+text",
                    text=grupo["banco_estandarizado"],
                    textposition="top center",
                    name=f"Cluster {cluster}",
                    marker=dict(size=15, opacity=0.82, line=dict(color="#0F172A", width=.8)),
                    hovertemplate="<b>%{text}</b><br>PCA1: %{x:.2f}<br>PCA2: %{y:.2f}<extra></extra>",
                )
            )

        fig_cl.update_layout(
            height=600,
            title=f"Mapa de segmentos financieros · {anio_cl}",
            xaxis_title="Componente PCA 1",
            yaxis_title="Componente PCA 2",
            margin=dict(l=10, r=10, t=65, b=10),
            plot_bgcolor="white",
        )
        fig_cl.update_xaxes(showgrid=False, zeroline=False)
        fig_cl.update_yaxes(showgrid=False, zeroline=False)
        st.plotly_chart(fig_cl, width="stretch")

        insight(
            f"El perfil más frecuente en {anio_cl} es **{perfil_dominante['perfil_cluster']}**, "
            f"con **{int(perfil_dominante['bancos'])} banco(s)**. "
            "KMeans no califica bancos; agrupa entidades con estructura financiera similar."
        )

        st.dataframe(
            cl_anio[
                ["banco_estandarizado", "cluster", "perfil_cluster", "activos_totales", "roe", "morosidad", "solvencia_proxy"]
            ].sort_values(["cluster", "banco_estandarizado"]),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# 6. Proyecciones Prophet
# ============================================================

with tab_prophet:
    st.markdown('<div class="section-title">Proyecciones Prophet</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Proyección exploratoria; muestra tendencia, valor real y banda de incertidumbre.</div>',
        unsafe_allow_html=True,
    )

    if df_prophet_forecast is None or df_prophet_forecast.empty:
        st.warning("No encuentro prophet_forecast o está vacío. Ejecuta 03_modelado_ml.ipynb con Prophet.")
    else:
        pf = df_prophet_forecast.copy()
        bancos_pf = sorted(pf["banco_estandarizado"].dropna().unique())
        indicadores_pf = [i for i in KPI_PRINCIPALES if i in pf["indicador"].dropna().unique()]

        p1, p2 = st.columns([1.2, 1])
        with p1:
            banco_pf = st.selectbox("Banco", bancos_pf, index=bancos_pf.index("PICHINCHA") if "PICHINCHA" in bancos_pf else 0, key="pf_banco")
        with p2:
            indicador_pf = st.selectbox("Indicador", indicadores_pf, format_func=lambda x: KPI_CONFIG[x]["label_largo"], key="pf_kpi")

        serie = pf[(pf["banco_estandarizado"] == banco_pf) & (pf["indicador"] == indicador_pf)].sort_values("ds").copy()

        if serie.empty:
            st.warning("No existe forecast para la combinación seleccionada.")
        else:
            historico = serie[serie["valor_real"].notna()].copy()
            proy = serie[serie["tipo"] == "proyeccion"].copy()

            ultimo_real = historico["valor_real"].iloc[-1] if not historico.empty else np.nan
            final_proy = proy["yhat"].iloc[-1] if not proy.empty else np.nan
            cambio = final_proy - ultimo_real if pd.notna(ultimo_real) and pd.notna(final_proy) else np.nan

            c1, c2, c3 = st.columns(3)
            c1.metric("Último valor real", formato_valor(ultimo_real, indicador_pf))
            c2.metric("Proyección final", formato_valor(final_proy, indicador_pf))
            c3.metric("Cambio esperado", formato_delta(cambio, indicador_pf))

            fig_p = go.Figure()

            fig_p.add_trace(
                go.Scatter(
                    x=serie["ds"],
                    y=serie["yhat_upper"],
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig_p.add_trace(
                go.Scatter(
                    x=serie["ds"],
                    y=serie["yhat_lower"],
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(37,99,235,0.16)",
                    line=dict(width=0),
                    name="Banda de incertidumbre",
                    hoverinfo="skip",
                )
            )
            fig_p.add_trace(
                go.Scatter(
                    x=serie["ds"],
                    y=serie["yhat"],
                    mode="lines",
                    name="Tendencia / Forecast",
                    line=dict(color=COLOR_PRINCIPAL, width=4),
                )
            )
            fig_p.add_trace(
                go.Scatter(
                    x=historico["ds"],
                    y=historico["valor_real"],
                    mode="markers",
                    name="Valor real",
                    marker=dict(color=COLOR_TEXTO, size=6),
                )
            )

            if not proy.empty:
                fecha_inicio = pd.to_datetime(proy["ds"].min()).strftime("%Y-%m-%d")
                fig_p.add_shape(
                    type="line",
                    x0=fecha_inicio,
                    x1=fecha_inicio,
                    y0=0,
                    y1=1,
                    xref="x",
                    yref="paper",
                    line=dict(color=COLOR_ALERTA, dash="dash", width=2),
                )
                fig_p.add_annotation(
                    x=fecha_inicio,
                    y=1,
                    xref="x",
                    yref="paper",
                    text="Inicio proyección",
                    showarrow=False,
                    yanchor="bottom",
                    xanchor="left",
                    bgcolor="#FFFFFF",
                )

            fig_p.update_layout(
                height=540,
                title=f"{KPI_CONFIG[indicador_pf]['label_largo']} · {banco_pf}",
                xaxis_title="Periodo",
                yaxis_title="Millones USD" if KPI_CONFIG[indicador_pf]["formato"] == "dinero" else "Porcentaje",
                hovermode="x unified",
                margin=dict(l=10, r=10, t=65, b=10),
                legend=dict(orientation="h", y=1.12),
                plot_bgcolor="white",
            )
            fig_p.update_yaxes(gridcolor="#E2E8F0")
            st.plotly_chart(fig_p, width="stretch")

            if pd.notna(cambio):
                if indicador_pf == "morosidad":
                    lectura = "favorable" if cambio < 0 else "de seguimiento"
                else:
                    lectura = "favorable" if cambio > 0 else "de seguimiento"
                insight(
                    f"Prophet proyecta un cambio de **{formato_delta(cambio, indicador_pf)}** para "
                    f"**{banco_pf}**. Para este KPI, la lectura es **{lectura}**."
                )


# ============================================================
# 7. Score Inteligente desde API
# ============================================================

with tab_score:
    st.markdown('<div class="section-title">Score Inteligente</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Esta pestaña consume la API mínima: /score?name=&year=. No lee directamente el dataset de score.</div>',
        unsafe_allow_html=True,
    )

    s1, s2 = st.columns([1.2, .8])
    with s1:
        banco_score = st.selectbox("Banco", bancos, index=bancos.index("PICHINCHA") if "PICHINCHA" in bancos else 0, key="score_banco_api")
    with s2:
        anio_score = st.selectbox("Año score", anios, index=anios.index(anio_default), key="score_anio_api")

    data_score, error_api = consultar_score_api(api_url, banco_score, anio_score)

    if error_api:
        st.error(
            "No se pudo consultar la API de score. "
            "Verifica que FastAPI esté ejecutándose y que la URL del sidebar sea correcta."
        )
        st.code(error_api)
        st.info("Ejecuta localmente: python -m uvicorn api_financiera_minimal:app --reload --app-dir 02_scripts")
    elif data_score is not None:
        score = data_score.get("score_salud")
        lectura = data_score.get("lectura_score")
        ranking = data_score.get("ranking_score")
        perfil = data_score.get("perfil_cluster")
        componentes = data_score.get("componentes", {}) or {}
        prophet = data_score.get("prophet", {}) or {}

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Score salud", "N/D" if score is None else f"{score:,.2f}/100")
        m2.metric("Lectura", lectura or "N/D")
        m3.metric("Ranking", "N/D" if ranking is None else f"#{int(ranking)}")
        m4.metric("Perfil KMeans", perfil or "N/D")

        col_gauge, col_comp = st.columns([1, 1.25])

        with col_gauge:
            fig_g = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=0 if score is None else score,
                    number={"suffix": "/100"},
                    title={"text": f"Score · {banco_score} · {anio_score}"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": COLOR_PRINCIPAL},
                        "steps": [
                            {"range": [0, 45], "color": "#FEE2E2"},
                            {"range": [45, 60], "color": "#FEF3C7"},
                            {"range": [60, 75], "color": "#DBEAFE"},
                            {"range": [75, 100], "color": "#DCFCE7"},
                        ],
                    },
                )
            )
            fig_g.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig_g, width="stretch")

        with col_comp:
            comp_df = pd.DataFrame(
                [
                    {"componente": "ROE real vs estimado", "puntaje": componentes.get("roe_real_vs_estimado")},
                    {"componente": "Perfil KMeans", "puntaje": componentes.get("perfil_kmeans")},
                    {"componente": "Tendencia futura", "puntaje": componentes.get("tendencia_futura")},
                    {"componente": "Morosidad proyectada", "puntaje": componentes.get("morosidad_proyectada")},
                    {"componente": "Solvencia proyectada", "puntaje": componentes.get("solvencia_proyectada")},
                ]
            ).dropna(subset=["puntaje"])

            if not comp_df.empty:
                comp_df = comp_df.sort_values("puntaje")
                fig_c = go.Figure(
                    go.Bar(
                        x=comp_df["puntaje"],
                        y=comp_df["componente"],
                        orientation="h",
                        marker=dict(color=[COLOR_PRINCIPAL if v == comp_df["puntaje"].max() else "#CBD5E1" for v in comp_df["puntaje"]]),
                        text=comp_df["puntaje"].map(lambda x: f"{x:.2f}"),
                        textposition="outside",
                    )
                )
                fig_c.update_layout(
                    height=360,
                    title="Componentes del score",
                    xaxis_title="Puntaje 0-100",
                    yaxis_title="",
                    xaxis=dict(range=[0, 100]),
                    margin=dict(l=10, r=40, t=65, b=10),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig_c, width="stretch")
            else:
                st.info("No hay componentes disponibles para graficar.")

        insight(data_score.get("analisis_ejecutivo") or "Sin análisis ejecutivo disponible.")
        insight(prophet.get("interpretacion") or "Sin lectura Prophet disponible.", tipo="warning")

        with st.expander("Respuesta cruda de la API"):
            st.json(data_score)


st.caption(
    "Dashboard Sistema BAncario Financiero. Valores monetarios en millones de USD; porcentajes en valor directo. "
    "El score inteligente se consume desde FastAPI."
)
