# ============================================================
# Dashboard Streamlit V2
# Sistema de Inteligencia Financiera - Banca Privada Ecuador
# ============================================================
# Ejecutar desde la raíz del proyecto:
# streamlit run 02_scripts/app_dashboard_v2.py
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Dashboard Financiero Bancario V2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

KPI_CONFIG = {
    "activos_totales": {
        "label": "Activos",
        "label_largo": "Activos totales",
        "unidad": "millones_usd",
        "formato": "dinero",
        "orden_ascendente": False,
        "sentido_negocio": "Mayor tamaño financiero y participación dentro del sistema.",
        "color": "#2563EB",
    },
    "pasivos_totales": {
        "label": "Pasivos",
        "label_largo": "Pasivos totales",
        "unidad": "millones_usd",
        "formato": "dinero",
        "orden_ascendente": False,
        "sentido_negocio": "Obligaciones y fondeo; se interpreta junto con activos y patrimonio.",
        "color": "#64748B",
    },
    "patrimonio": {
        "label": "Patrimonio",
        "label_largo": "Patrimonio",
        "unidad": "millones_usd",
        "formato": "dinero",
        "orden_ascendente": False,
        "sentido_negocio": "Mayor respaldo contable frente a riesgos y crecimiento.",
        "color": "#059669",
    },
    "roe": {
        "label": "ROE",
        "label_largo": "ROE",
        "unidad": "porcentaje",
        "formato": "porcentaje",
        "orden_ascendente": False,
        "sentido_negocio": "Mayor rentabilidad sobre patrimonio.",
        "color": "#7C3AED",
    },
    "morosidad": {
        "label": "Morosidad",
        "label_largo": "Morosidad",
        "unidad": "porcentaje",
        "formato": "porcentaje",
        "orden_ascendente": True,
        "sentido_negocio": "Menor morosidad implica mejor calidad de cartera.",
        "color": "#DC2626",
    },
    "solvencia_proxy": {
        "label": "Solvencia",
        "label_largo": "Solvencia proxy",
        "unidad": "porcentaje",
        "formato": "porcentaje",
        "orden_ascendente": False,
        "sentido_negocio": "Mayor solvencia proxy implica mayor fortaleza patrimonial relativa.",
        "color": "#EA580C",
    },
}

KPI_PRINCIPALES = ["activos_totales", "roe", "morosidad", "solvencia_proxy"]
KPI_TODOS = ["activos_totales", "pasivos_totales", "patrimonio", "roe", "morosidad", "solvencia_proxy"]
MESES_ES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}

st.markdown(
    """
    <style>
    .main-title {font-size:2.15rem;font-weight:850;color:#0F172A;margin-bottom:.15rem;}
    .subtitle {font-size:1rem;color:#475569;margin-bottom:1.1rem;}
    .section-title {font-size:1.25rem;font-weight:800;color:#0F172A;margin-top:.4rem;margin-bottom:.2rem;}
    .section-note {color:#64748B;font-size:.91rem;margin-bottom:1rem;}
    .metric-card {background:#F8FAFC;border:1px solid #E2E8F0;border-radius:18px;padding:16px 17px;box-shadow:0 8px 24px rgba(15,23,42,.055);min-height:128px;}
    .metric-label {color:#64748B;font-size:.84rem;font-weight:750;margin-bottom:.35rem;}
    .metric-value {color:#0F172A;font-size:1.55rem;font-weight:850;margin-bottom:.1rem;}
    .metric-caption {color:#64748B;font-size:.8rem;}
    .good-badge {display:inline-block;background:#DCFCE7;color:#166534;border-radius:999px;padding:.18rem .55rem;font-size:.76rem;font-weight:750;}
    .warn-badge {display:inline-block;background:#FEF3C7;color:#92400E;border-radius:999px;padding:.18rem .55rem;font-size:.76rem;font-weight:750;}
    .bad-badge {display:inline-block;background:#FEE2E2;color:#991B1B;border-radius:999px;padding:.18rem .55rem;font-size:.76rem;font-weight:750;}
    div[data-testid="stMetric"] {background-color:#F8FAFC;border:1px solid #E2E8F0;padding:1rem;border-radius:1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


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
        fuente = ruta_parquet
    elif ruta_csv.exists():
        df = pd.read_csv(ruta_csv)
        fuente = ruta_csv
    else:
        raise FileNotFoundError("No se encontró dataset_financiero_limpio.parquet ni dataset_financiero_limpio.csv.")

    requeridas = {"periodo", "banco_estandarizado", "indicador", "valor", "unidad", "sentido"}
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")

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
    df["fuente_datos"] = str(fuente)
    return df[df["indicador"].isin(KPI_TODOS)].copy()


@st.cache_data(show_spinner=False)
def preparar_datos_anuales(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["anio", "banco_estandarizado", "indicador"], dropna=False)
        .agg(
            valor=("valor", "mean"),
            unidad=("unidad", lambda s: s.dropna().iloc[0] if s.dropna().size else None),
            sentido=("sentido", lambda s: s.dropna().iloc[0] if s.dropna().size else None),
            meses_con_dato=("valor", "count"),
        )
        .reset_index()
    )


def formato_valor(valor, indicador) -> str:
    if pd.isna(valor):
        return "N/D"
    if KPI_CONFIG[indicador]["formato"] == "dinero":
        return f"USD {valor:,.2f} M"
    if KPI_CONFIG[indicador]["formato"] == "porcentaje":
        return f"{valor:,.2f}%"
    return f"{valor:,.2f}"


def ordenar_por_kpi(df_base: pd.DataFrame, indicador: str) -> pd.DataFrame:
    return df_base.sort_values("valor", ascending=KPI_CONFIG[indicador]["orden_ascendente"])


def ranking_mensual(df: pd.DataFrame, periodo: str, indicador: str) -> pd.DataFrame:
    base = df[(df["periodo"] == periodo) & (df["indicador"] == indicador) & (df["valor"].notna())].copy()
    base = ordenar_por_kpi(base, indicador).reset_index(drop=True)
    base["ranking"] = base.index + 1
    return base


def ranking_anual(df_anual: pd.DataFrame, anio: int, indicador: str) -> pd.DataFrame:
    base = df_anual[(df_anual["anio"] == anio) & (df_anual["indicador"] == indicador) & (df_anual["valor"].notna())].copy()
    base = ordenar_por_kpi(base, indicador).reset_index(drop=True)
    base["ranking"] = base.index + 1
    return base


def ranking_anual_todos_los_anios(df_anual: pd.DataFrame, indicador: str) -> pd.DataFrame:
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
    return df_anual.groupby(["anio", "indicador"], dropna=False).agg(promedio_sistema=("valor", "mean")).reset_index()


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


def variacion_anual_banco(df: pd.DataFrame, banco: str, indicador: str, anio: int) -> float:
    serie = df[(df["banco_estandarizado"] == banco) & (df["indicador"] == indicador) & (df["anio"] == anio) & (df["valor"].notna())].sort_values("mes")
    if len(serie) < 2:
        return np.nan
    valor_inicio = serie["valor"].iloc[0]
    valor_fin = serie["valor"].iloc[-1]
    if pd.isna(valor_inicio) or valor_inicio == 0:
        return np.nan
    return ((valor_fin - valor_inicio) / valor_inicio) * 100


def ultimo_periodo_disponible_anio(df: pd.DataFrame, anio: int, indicador: str):
    periodos = df[(df["anio"] == anio) & (df["indicador"] == indicador)]["periodo"].dropna().sort_values().unique()
    return None if len(periodos) == 0 else periodos[-1]


def tarjeta_html(label, value, caption="", badge=None, badge_type="good"):
    badge_html = ""
    if badge:
        clase = {"good": "good-badge", "warn": "warn-badge", "bad": "bad-badge"}.get(badge_type, "good-badge")
        badge_html = f"<span class='{clase}'>{badge}</span>"
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-caption">{caption}</div>
        <div style="margin-top: 0.5rem;">{badge_html}</div>
    </div>
    """


def clasificar_senal_riesgo(morosidad, solvencia, roe, morosidad_prom, solvencia_prom, roe_prom):
    if pd.isna(morosidad) or pd.isna(solvencia) or pd.isna(roe):
        return "Sin datos suficientes"
    if morosidad > morosidad_prom and solvencia < solvencia_prom and roe < roe_prom:
        return "Mayor riesgo relativo"
    if morosidad <= morosidad_prom and solvencia >= solvencia_prom and roe >= roe_prom:
        return "Mejor posición relativa"
    return "Zona intermedia"


def normalizar_heatmap(grupo):
    minimo = grupo.min()
    maximo = grupo.max()
    if pd.isna(minimo) or pd.isna(maximo) or maximo == minimo:
        return pd.Series(0.5, index=grupo.index)
    return (grupo - minimo) / (maximo - minimo)




@st.cache_data(show_spinner=False)
def cargar_resultado_modelo(nombre_base: str) -> pd.DataFrame | None:
    """
    Carga un resultado generado por el notebook 03_modelado_ml.
    Busca primero Parquet y luego CSV dentro de 01_datos_procesados/modelos.
    Si el archivo no existe, devuelve None para que el dashboard no se rompa.
    """
    raiz = encontrar_raiz_proyecto()
    carpeta_modelos = raiz / "01_datos_procesados" / "modelos"
    ruta_parquet = carpeta_modelos / f"{nombre_base}.parquet"
    ruta_csv = carpeta_modelos / f"{nombre_base}.csv"

    if ruta_parquet.exists():
        return pd.read_parquet(ruta_parquet)

    if ruta_csv.exists():
        return pd.read_csv(ruta_csv)

    return None


def preparar_fecha_modelo(df_modelo: pd.DataFrame | None) -> pd.DataFrame | None:
    """
    Normaliza columnas de fecha en datasets de modelos.
    """
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


def mostrar_archivos_modelos_faltantes():
    """
    Mensaje estándar cuando todavía no existen archivos de modelos.
    """
    st.warning(
        "No encuentro los resultados de modelos en `01_datos_procesados/modelos/`. "
        "Ejecuta primero `03_cuadernos/03_modelado_ml.ipynb` y vuelve a abrir el dashboard."
    )

try:
    df = cargar_dataset()
    df_anual = preparar_datos_anuales(df)
except Exception as e:
    st.error(f"No se pudo cargar o preparar el dataset: {e}")
    st.stop()

anios = sorted(df["anio"].dropna().astype(int).unique())
bancos = sorted(df["banco_estandarizado"].dropna().unique())
if not anios or not bancos:
    st.error("El dataset no contiene años o bancos suficientes.")
    st.stop()

anio_default = int(max(anios))
df_prom_mensual = promedio_sistema_mensual(df)
df_prom_anual = promedio_sistema_anual(df_anual)


# ============================================================
# Carga de resultados de modelos ML
# ============================================================
# Estos archivos son generados por 03_cuadernos/03_modelado_ml.ipynb.
df_roe_predicciones = preparar_fecha_modelo(cargar_resultado_modelo("modelo_roe_predicciones"))
df_roe_metricas = cargar_resultado_modelo("modelo_roe_metricas")
df_roe_importancia = cargar_resultado_modelo("modelo_roe_importancia_variables")

df_clusters = preparar_fecha_modelo(cargar_resultado_modelo("clusters_bancos_anual"))
df_clusters_resumen = cargar_resultado_modelo("clusters_resumen")

df_prophet_forecast = preparar_fecha_modelo(cargar_resultado_modelo("prophet_forecast"))
df_prophet_metricas = cargar_resultado_modelo("prophet_metricas_ajuste")

# Resultados del score inteligente de salud financiera.
df_score_salud = cargar_resultado_modelo("score_salud_bancaria")
df_score_componentes = cargar_resultado_modelo("score_componentes_bancos")

st.markdown('<div class="main-title">Sistema de Inteligencia Financiera Bancaria</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Dashboard comparativo: banco vs sistema, rankings históricos y señales de riesgo.</div>', unsafe_allow_html=True)

with st.expander("Pregunta de negocio, hipótesis y lectura del dashboard", expanded=False):
    st.markdown(
        """
        **Pregunta principal:**  
        ¿Cómo se puede comparar y rankear de forma histórica, consistente y automática el desempeño financiero de los bancos privados ecuatorianos usando boletines oficiales?

        **Hipótesis que ayuda a evaluar:**
        - Bancos grandes lideran persistentemente por activos.
        - El liderazgo por activos no necesariamente coincide con liderazgo por ROE.
        - Bancos especializados o de mayor riesgo pueden presentar mayor morosidad.
        - Periodos de estrés pueden reflejar aumentos de morosidad y reducciones de ROE.
        - Bancos pequeños pueden mostrar solvencia proxy relativamente alta.
        """
    )

tab_banco, tab_ranking, tab_riesgo, tab_comparativa, tab_modelo_roe, tab_clusters, tab_prophet, tab_score = st.tabs(
    [
        "Banco vs Sistema",
        "Ranking",
        "Riesgo financiero",
        "Tabla comparativa",
        "Modelo ROE",
        "Clusters KMeans",
        "Proyecciones Prophet",
        "Score inteligente",
    ]
)

with tab_banco:
    st.markdown('<div class="section-title">Banco vs Sistema</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Analiza un banco específico frente al promedio del sistema, con vista mensual y evolución anual histórica.</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns([1.3, 1, 0.7])
    with col_f1:
        banco_sel = st.selectbox("Banco", options=bancos, index=bancos.index("PICHINCHA") if "PICHINCHA" in bancos else 0, key="bvs_banco")
    with col_f2:
        kpi_banco = st.selectbox("KPI", options=KPI_PRINCIPALES, format_func=lambda x: KPI_CONFIG[x]["label"], index=0, key="bvs_kpi")
    with col_f3:
        anio_banco = st.selectbox("Año", options=anios, index=anios.index(anio_default), key="bvs_anio")

    ultimo_periodo_anio = ultimo_periodo_disponible_anio(df, anio_banco, kpi_banco)
    if ultimo_periodo_anio is None:
        st.warning("No existen datos para el año e indicador seleccionados.")
    else:
        valor_banco_mes = df[(df["periodo"] == ultimo_periodo_anio) & (df["banco_estandarizado"] == banco_sel) & (df["indicador"] == kpi_banco)]["valor"]
        valor_banco_mes = valor_banco_mes.iloc[0] if not valor_banco_mes.empty else np.nan
        promedio_mes = df[(df["periodo"] == ultimo_periodo_anio) & (df["indicador"] == kpi_banco)]["valor"].mean()
        ranking_mes = ranking_mensual(df, ultimo_periodo_anio, kpi_banco)
        fila_rank = ranking_mes[ranking_mes["banco_estandarizado"] == banco_sel]
        posicion = int(fila_rank["ranking"].iloc[0]) if not fila_rank.empty else None
        variacion = variacion_anual_banco(df, banco_sel, kpi_banco, anio_banco)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(tarjeta_html(f"{KPI_CONFIG[kpi_banco]['label_largo']} · {ultimo_periodo_anio}", formato_valor(valor_banco_mes, kpi_banco), "Valor del banco seleccionado"), unsafe_allow_html=True)
        with c2:
            st.markdown(tarjeta_html("Promedio sistema", formato_valor(promedio_mes, kpi_banco), f"Promedio del sistema en {ultimo_periodo_anio}"), unsafe_allow_html=True)
        with c3:
            st.markdown(tarjeta_html("Posición ranking", "N/D" if posicion is None else f"#{posicion}", f"de {len(ranking_mes)} bancos"), unsafe_allow_html=True)
        with c4:
            var_txt = "N/D" if pd.isna(variacion) else f"{variacion:,.2f}%"
            st.markdown(tarjeta_html(f"Variación {anio_banco}", var_txt, "Primer vs último mes disponible", badge="anual", badge_type="good" if not pd.isna(variacion) and variacion >= 0 else "warn"), unsafe_allow_html=True)

        st.markdown("#### Historial mensual del año seleccionado")
        mensual_banco = df[(df["anio"] == anio_banco) & (df["banco_estandarizado"] == banco_sel) & (df["indicador"] == kpi_banco)][["periodo", "mes", "mes_nombre", "valor"]].copy()
        mensual_sistema = df_prom_mensual[(df_prom_mensual["anio"] == anio_banco) & (df_prom_mensual["indicador"] == kpi_banco)][["periodo", "mes", "mes_nombre", "promedio_sistema"]].copy()
        mensual = mensual_banco.merge(mensual_sistema, on=["periodo", "mes", "mes_nombre"], how="outer").sort_values("mes")

        fig_mes = go.Figure()
        fig_mes.add_trace(go.Bar(x=mensual["mes_nombre"], y=mensual["valor"], name=banco_sel, marker_color=KPI_CONFIG[kpi_banco]["color"], text=[formato_valor(v, kpi_banco) for v in mensual["valor"]], textposition="outside"))
        fig_mes.add_trace(go.Scatter(x=mensual["mes_nombre"], y=mensual["promedio_sistema"], mode="lines+markers", name="Promedio sistema", line=dict(width=3, color="#94A3B8", dash="dash")))
        fig_mes.update_layout(height=460, title=f"{KPI_CONFIG[kpi_banco]['label_largo']} mensual · {banco_sel} vs sistema · {anio_banco}", xaxis_title="Mes", yaxis_title="Millones USD" if KPI_CONFIG[kpi_banco]["unidad"] == "millones_usd" else "Porcentaje", margin=dict(l=10, r=10, t=60, b=10), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_mes, width="stretch")

        st.markdown("#### Evolución anual histórica")
        anual_banco = df_anual[(df_anual["banco_estandarizado"] == banco_sel) & (df_anual["indicador"] == kpi_banco)][["anio", "valor"]].copy()
        anual_sistema = df_prom_anual[df_prom_anual["indicador"] == kpi_banco][["anio", "promedio_sistema"]].copy()
        fig_anual = go.Figure()
        fig_anual.add_trace(go.Scatter(x=anual_banco["anio"], y=anual_banco["valor"], mode="lines+markers", name=banco_sel, line=dict(width=3, color=KPI_CONFIG[kpi_banco]["color"])))
        fig_anual.add_trace(go.Scatter(x=anual_sistema["anio"], y=anual_sistema["promedio_sistema"], mode="lines+markers", name="Promedio sistema", line=dict(width=3, color="#94A3B8", dash="dash")))
        fig_anual.update_layout(height=460, title=f"Evolución anual promedio · {KPI_CONFIG[kpi_banco]['label_largo']}", xaxis_title="Año", yaxis_title="Millones USD" if KPI_CONFIG[kpi_banco]["unidad"] == "millones_usd" else "Porcentaje", margin=dict(l=10, r=10, t=60, b=10), hovermode="x unified", legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_anual, width="stretch")

with tab_ranking:
    st.markdown('<div class="section-title">Ranking histórico de bancos</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Evalúa liderazgo financiero por KPI, año y evolución histórica del Top N. Esta pestaña no depende de un banco seleccionado.</div>', unsafe_allow_html=True)
    r1, r2, r3 = st.columns([1, .8, .8])
    with r1:
        kpi_ranking = st.selectbox("KPI", options=KPI_PRINCIPALES, format_func=lambda x: KPI_CONFIG[x]["label"], index=0, key="rank_kpi")
    with r2:
        anio_ranking = st.selectbox("Año para ranking", options=anios, index=anios.index(anio_default), key="rank_anio")
    with r3:
        top_n = st.slider("Top N", min_value=3, max_value=10, value=10, step=1, key="rank_top")

    ranking_year = ranking_anual(df_anual, anio_ranking, kpi_ranking)
    ranking_top = ranking_year.head(top_n).copy()
    bancos_top = ranking_top["banco_estandarizado"].tolist()
    ranking_top["valor_texto"] = ranking_top["valor"].apply(lambda x: formato_valor(x, kpi_ranking))

    col_barras, col_tabla = st.columns([1.55, 1])
    with col_barras:
        plot_rank = ranking_top.sort_values("ranking", ascending=False)
        fig_rank = px.bar(plot_rank, x="valor", y="banco_estandarizado", orientation="h", text="valor_texto", color="valor", color_continuous_scale="Blues" if kpi_ranking != "morosidad" else "Reds", title=f"Top {top_n} · {KPI_CONFIG[kpi_ranking]['label_largo']} · {anio_ranking}")
        fig_rank.update_traces(textposition="outside", hovertemplate="<b>%{y}</b><br>Valor: %{x:.2f}<extra></extra>")
        fig_rank.update_layout(height=480, margin=dict(l=10, r=20, t=60, b=10), xaxis_title="Millones USD" if KPI_CONFIG[kpi_ranking]["unidad"] == "millones_usd" else "Porcentaje", yaxis_title="Banco", coloraxis_showscale=False)
        st.plotly_chart(fig_rank, width="stretch")
    with col_tabla:
        st.markdown("#### Ranking anual")
        tabla_ranking = ranking_year[["ranking", "banco_estandarizado", "valor", "unidad", "sentido", "meses_con_dato"]].copy()
        tabla_ranking["valor_formateado"] = tabla_ranking["valor"].apply(lambda x: formato_valor(x, kpi_ranking))
        st.dataframe(tabla_ranking[["ranking", "banco_estandarizado", "valor", "valor_formateado", "unidad", "sentido", "meses_con_dato"]], width="stretch", hide_index=True)

    st.markdown("#### Evolución anual del indicador para el Top N")
    hist_top = df_anual[(df_anual["indicador"] == kpi_ranking) & (df_anual["banco_estandarizado"].isin(bancos_top))]
    fig_hist = px.line(hist_top, x="anio", y="valor", color="banco_estandarizado", markers=True, title=f"Evolución anual promedio del Top {top_n} · {KPI_CONFIG[kpi_ranking]['label_largo']}", labels={"anio": "Año", "valor": "Millones USD" if KPI_CONFIG[kpi_ranking]["unidad"] == "millones_usd" else "Porcentaje", "banco_estandarizado": "Banco"})
    fig_hist.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10), hovermode="x unified")
    st.plotly_chart(fig_hist, width="stretch")

    st.markdown("#### Evolución anual del ranking")
    ranking_hist = ranking_anual_todos_los_anios(df_anual, kpi_ranking)
    ranking_hist_top = ranking_hist[ranking_hist["banco_estandarizado"].isin(bancos_top)]
    fig_rank_hist = px.line(ranking_hist_top, x="anio", y="ranking", color="banco_estandarizado", markers=True, title=f"Posición anual del Top {top_n} actual · 1 es mejor", labels={"anio": "Año", "ranking": "Ranking", "banco_estandarizado": "Banco"})
    fig_rank_hist.update_yaxes(autorange="reversed", dtick=1)
    fig_rank_hist.update_layout(height=500, margin=dict(l=10, r=10, t=60, b=10), hovermode="x unified")
    st.plotly_chart(fig_rank_hist, width="stretch")

with tab_riesgo:
    st.markdown('<div class="section-title">Riesgo financiero y señales relativas</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Cruce anual de morosidad, solvencia proxy, ROE y activos para identificar bancos con señales de mayor riesgo relativo.</div>', unsafe_allow_html=True)
    anio_riesgo = st.selectbox("Año", options=anios, index=anios.index(anio_default), key="riesgo_anio")
    tabla_riesgo = pivot_anual(df_anual, anio_riesgo)
    mor_prom = tabla_riesgo["morosidad"].mean()
    solv_prom = tabla_riesgo["solvencia_proxy"].mean()
    roe_prom = tabla_riesgo["roe"].mean()
    tabla_riesgo["senal_riesgo"] = tabla_riesgo.apply(lambda fila: clasificar_senal_riesgo(fila["morosidad"], fila["solvencia_proxy"], fila["roe"], mor_prom, solv_prom, roe_prom), axis=1)
    fig_riesgo = px.scatter(tabla_riesgo, x="morosidad", y="solvencia_proxy", size="activos_totales", color="roe", hover_name="banco_estandarizado", text="banco_estandarizado", color_continuous_scale="RdYlGn", size_max=55, title=f"Morosidad vs Solvencia proxy · promedio anual {anio_riesgo}", labels={"morosidad": "Morosidad (%)", "solvencia_proxy": "Solvencia proxy (%)", "roe": "ROE (%)", "activos_totales": "Activos (USD M)"})
    fig_riesgo.add_vline(x=mor_prom, line_dash="dash", line_color="#94A3B8", annotation_text="Morosidad promedio", annotation_position="top")
    fig_riesgo.add_hline(y=solv_prom, line_dash="dash", line_color="#94A3B8", annotation_text="Solvencia promedio", annotation_position="right")
    fig_riesgo.update_traces(textposition="top center", textfont=dict(size=9), marker=dict(opacity=.78, line=dict(width=1, color="#0F172A")))
    fig_riesgo.update_layout(height=650, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig_riesgo, width="stretch")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Morosidad promedio", f"{mor_prom:,.2f}%")
    s2.metric("Solvencia proxy promedio", f"{solv_prom:,.2f}%")
    s3.metric("ROE promedio", f"{roe_prom:,.2f}%")
    s4.metric("Bancos mayor riesgo relativo", int((tabla_riesgo["senal_riesgo"] == "Mayor riesgo relativo").sum()))
    st.markdown("#### Tabla de señales de riesgo")
    st.dataframe(tabla_riesgo[["banco_estandarizado", "activos_totales", "roe", "morosidad", "solvencia_proxy", "senal_riesgo"]].sort_values(["senal_riesgo", "morosidad"], ascending=[True, False]), width="stretch", hide_index=True)

with tab_comparativa:
    st.markdown('<div class="section-title">Tabla comparativa y heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Comparación anual simultánea de todos los bancos. La tabla es ordenable y el heatmap resume fortalezas relativas.</div>', unsafe_allow_html=True)
    t1, t2 = st.columns([.7, 1])
    with t1:
        anio_tabla = st.selectbox("Año", options=anios, index=anios.index(anio_default), key="tabla_anio")
    with t2:
        kpi_orden = st.selectbox("Ordenar inicialmente por", options=KPI_PRINCIPALES, format_func=lambda x: KPI_CONFIG[x]["label"], index=0, key="tabla_kpi_orden")
    tabla_comp = pivot_anual(df_anual, anio_tabla)
    ranking_tabla = ranking_anual(df_anual, anio_tabla, kpi_orden)[["banco_estandarizado", "ranking"]]
    tabla_comp = tabla_comp.merge(ranking_tabla, on="banco_estandarizado", how="left").sort_values("ranking", na_position="last")
    for col in KPI_TODOS:
        tabla_comp[col] = pd.to_numeric(tabla_comp[col], errors="coerce").round(2)
    tabla_comp = tabla_comp[["ranking", "banco_estandarizado"] + KPI_TODOS]
    st.dataframe(tabla_comp, width="stretch", hide_index=True)
    st.markdown("#### Heatmap comparativo normalizado")
    heatmap_long = tabla_comp.drop(columns=["ranking"], errors="ignore").melt(id_vars="banco_estandarizado", value_vars=KPI_TODOS, var_name="indicador", value_name="valor")
    heatmap_long["valor_normalizado"] = heatmap_long.groupby("indicador")["valor"].transform(normalizar_heatmap)
    mask_morosidad = heatmap_long["indicador"] == "morosidad"
    heatmap_long.loc[mask_morosidad, "valor_normalizado"] = 1 - heatmap_long.loc[mask_morosidad, "valor_normalizado"]
    heatmap_matrix = heatmap_long.pivot_table(index="banco_estandarizado", columns="indicador", values="valor_normalizado", aggfunc="first")[KPI_TODOS]
    fig_heatmap = px.imshow(heatmap_matrix, aspect="auto", color_continuous_scale="RdYlGn", title="Heatmap normalizado · verde representa mejor posición relativa por KPI")
    fig_heatmap.update_layout(height=max(500, len(heatmap_matrix) * 24), margin=dict(l=10, r=10, t=60, b=10), xaxis_title="KPI", yaxis_title="Banco")
    st.plotly_chart(fig_heatmap, width="stretch")


# ============================================================
# TAB 5: Modelo ROE con RandomForestRegressor
# ============================================================

with tab_modelo_roe:
    st.markdown('<div class="section-title">Modelo ROE · RandomForestRegressor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Modelo supervisado para estimar ROE usando activos, pasivos, patrimonio, morosidad y solvencia proxy.</div>',
        unsafe_allow_html=True,
    )

    if df_roe_predicciones is None or df_roe_metricas is None or df_roe_importancia is None:
        mostrar_archivos_modelos_faltantes()
    else:
        df_roe_pred = df_roe_predicciones.copy()
        df_roe_met = df_roe_metricas.copy()
        df_roe_imp = df_roe_importancia.copy()

        # Filtros principales del modelo ROE.
        bancos_modelo = sorted(df_roe_pred["banco_estandarizado"].dropna().unique())
        anios_modelo = sorted(df_roe_pred["anio"].dropna().astype(int).unique())

        col_m1, col_m2 = st.columns([1.2, 0.8])

        with col_m1:
            banco_roe = st.selectbox(
                "Banco para ver ROE real vs estimado",
                options=bancos_modelo,
                index=bancos_modelo.index("PICHINCHA") if "PICHINCHA" in bancos_modelo else 0,
                key="ml_roe_banco",
            )

        with col_m2:
            anio_roe = st.selectbox(
                "Año",
                options=["Todos"] + anios_modelo,
                index=0,
                key="ml_roe_anio",
            )

        # Métricas del modelo, priorizando test si existe.
        metrica_test = df_roe_met[df_roe_met["conjunto"].astype(str).str.lower() == "test"]
        metrica_ref = metrica_test.iloc[0] if not metrica_test.empty else df_roe_met.iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("MAE", f"{metrica_ref['mae']:,.2f}")
        c2.metric("RMSE", f"{metrica_ref['rmse']:,.2f}")
        c3.metric("R²", f"{metrica_ref['r2']:,.3f}")
        c4.metric("Observaciones", f"{int(metrica_ref['observaciones']):,}")

        st.caption(
            "MAE y RMSE miden error del modelo en puntos porcentuales de ROE. "
            "R² indica qué proporción de variabilidad del ROE es explicada por el modelo."
        )

        df_roe_filtro = df_roe_pred[df_roe_pred["banco_estandarizado"] == banco_roe].copy()

        if anio_roe != "Todos":
            df_roe_filtro = df_roe_filtro[df_roe_filtro["anio"] == int(anio_roe)].copy()

        col_g1, col_g2 = st.columns([1.35, 1])

        with col_g1:
            st.markdown("#### ROE real vs ROE estimado en el tiempo")

            fig_roe_line = go.Figure()
            fig_roe_line.add_trace(
                go.Scatter(
                    x=df_roe_filtro["periodo_dt"],
                    y=df_roe_filtro["roe_real"],
                    mode="lines+markers",
                    name="ROE real",
                    line=dict(width=3, color="#2563EB"),
                )
            )
            fig_roe_line.add_trace(
                go.Scatter(
                    x=df_roe_filtro["periodo_dt"],
                    y=df_roe_filtro["roe_estimado"],
                    mode="lines+markers",
                    name="ROE estimado",
                    line=dict(width=3, color="#EA580C", dash="dash"),
                )
            )
            fig_roe_line.update_layout(
                height=470,
                xaxis_title="Periodo",
                yaxis_title="ROE (%)",
                hovermode="x unified",
                margin=dict(l=10, r=10, t=35, b=10),
                legend=dict(orientation="h", y=1.08),
            )
            st.plotly_chart(fig_roe_line, width="stretch")

        with col_g2:
            st.markdown("#### Importancia de variables")

            df_roe_imp = df_roe_imp.sort_values("importancia", ascending=True)
            fig_imp = px.bar(
                df_roe_imp,
                x="importancia",
                y="variable",
                orientation="h",
                text=df_roe_imp["importancia"].round(3),
                title="Variables que más aportan a la estimación del ROE",
                color="importancia",
                color_continuous_scale="Blues",
            )
            fig_imp.update_layout(
                height=470,
                xaxis_title="Importancia relativa",
                yaxis_title="Variable",
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_imp, width="stretch")

        st.markdown("#### ROE real vs ROE estimado · todos los bancos")

        df_scatter_roe = df_roe_pred.copy()
        if anio_roe != "Todos":
            df_scatter_roe = df_scatter_roe[df_scatter_roe["anio"] == int(anio_roe)].copy()

        fig_roe_scatter = px.scatter(
            df_scatter_roe,
            x="roe_real",
            y="roe_estimado",
            color="banco_estandarizado",
            hover_name="banco_estandarizado",
            hover_data=["periodo", "activos_totales", "morosidad", "solvencia_proxy", "error_abs_roe"],
            title="Dispersión del modelo · ROE real vs estimado",
            labels={"roe_real": "ROE real (%)", "roe_estimado": "ROE estimado (%)"},
        )

        if not df_scatter_roe.empty:
            v_min = np.nanmin([df_scatter_roe["roe_real"].min(), df_scatter_roe["roe_estimado"].min()])
            v_max = np.nanmax([df_scatter_roe["roe_real"].max(), df_scatter_roe["roe_estimado"].max()])
            fig_roe_scatter.add_trace(
                go.Scatter(
                    x=[v_min, v_max],
                    y=[v_min, v_max],
                    mode="lines",
                    name="Estimación perfecta",
                    line=dict(color="#94A3B8", dash="dash"),
                )
            )

        fig_roe_scatter.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig_roe_scatter, width="stretch")

        st.markdown("#### Bancos/periodos con mayor error de estimación")
        columnas_error = [
            "periodo",
            "banco_estandarizado",
            "roe_real",
            "roe_estimado",
            "error_roe",
            "error_abs_roe",
            "activos_totales",
            "morosidad",
            "solvencia_proxy",
        ]
        st.dataframe(
            df_roe_pred[columnas_error].sort_values("error_abs_roe", ascending=False).head(30),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# TAB 6: Segmentación KMeans
# ============================================================

with tab_clusters:
    st.markdown('<div class="section-title">Segmentación bancaria · KMeans</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Modelo no supervisado para agrupar bancos con perfiles financieros similares por año.</div>',
        unsafe_allow_html=True,
    )

    if df_clusters is None or df_clusters_resumen is None:
        mostrar_archivos_modelos_faltantes()
    else:
        df_cl = df_clusters.copy()
        df_cl_res = df_clusters_resumen.copy()

        anios_cluster = sorted(df_cl["anio"].dropna().astype(int).unique())
        clusters_disponibles = sorted(df_cl["cluster"].dropna().unique())

        col_k1, col_k2 = st.columns([0.7, 1])

        with col_k1:
            anio_cluster = st.selectbox(
                "Año",
                options=anios_cluster,
                index=len(anios_cluster) - 1,
                key="ml_cluster_anio",
            )

        with col_k2:
            cluster_sel = st.multiselect(
                "Clusters a mostrar",
                options=clusters_disponibles,
                default=clusters_disponibles,
                key="ml_cluster_filtro",
            )

        df_cl_anio = df_cl[(df_cl["anio"] == anio_cluster) & (df_cl["cluster"].isin(cluster_sel))].copy()

        st.markdown("#### Mapa de segmentos financieros")
        fig_cluster = px.scatter(
            df_cl_anio,
            x="pca_1",
            y="pca_2",
            color="cluster",
            symbol="perfil_cluster" if "perfil_cluster" in df_cl_anio.columns else None,
            hover_name="banco_estandarizado",
            hover_data=["perfil_cluster", "activos_totales", "roe", "morosidad", "solvencia_proxy", "meses_con_dato"],
            text="banco_estandarizado",
            title=f"Clusters de bancos · {anio_cluster}",
            color_continuous_scale="Viridis",
        )
        fig_cluster.update_traces(textposition="top center", textfont=dict(size=9), marker=dict(size=14, opacity=0.82))
        fig_cluster.update_layout(
            height=620,
            xaxis_title="Componente PCA 1",
            yaxis_title="Componente PCA 2",
            margin=dict(l=10, r=10, t=60, b=10),
        )
        st.plotly_chart(fig_cluster, width="stretch")

        st.markdown("#### Resumen de perfiles por cluster")
        st.dataframe(df_cl_res, width="stretch", hide_index=True)

        st.markdown("#### Bancos clasificados por segmento")
        columnas_cluster = [
            "anio",
            "banco_estandarizado",
            "cluster",
            "perfil_cluster",
            "activos_totales",
            "patrimonio",
            "roe",
            "morosidad",
            "solvencia_proxy",
            "meses_con_dato",
        ]
        columnas_cluster = [c for c in columnas_cluster if c in df_cl_anio.columns]
        st.dataframe(
            df_cl_anio[columnas_cluster].sort_values(["cluster", "banco_estandarizado"]),
            width="stretch",
            hide_index=True,
        )

        st.markdown("#### Evolución de segmentos por banco")
        banco_cluster = st.selectbox(
            "Banco para revisar evolución de cluster",
            options=sorted(df_cl["banco_estandarizado"].dropna().unique()),
            index=0,
            key="ml_cluster_banco_evolucion",
        )
        df_cluster_banco = df_cl[df_cl["banco_estandarizado"] == banco_cluster].copy()
        fig_cluster_evol = px.line(
            df_cluster_banco,
            x="anio",
            y="cluster",
            markers=True,
            hover_data=["perfil_cluster", "activos_totales", "roe", "morosidad", "solvencia_proxy"],
            title=f"Evolución del cluster asignado · {banco_cluster}",
        )
        fig_cluster_evol.update_yaxes(dtick=1)
        fig_cluster_evol.update_layout(height=380, xaxis_title="Año", yaxis_title="Cluster")
        st.plotly_chart(fig_cluster_evol, width="stretch")


# ============================================================
# TAB 7: Proyecciones Prophet
# ============================================================

with tab_prophet:
    st.markdown('<div class="section-title">Proyecciones · Prophet</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Proyecciones exploratorias por banco e indicador. No constituyen recomendación financiera ni predicción oficial.</div>',
        unsafe_allow_html=True,
    )

    if df_prophet_forecast is None or df_prophet_metricas is None:
        mostrar_archivos_modelos_faltantes()
    elif df_prophet_forecast.empty:
        st.warning(
            "El archivo de Prophet existe, pero no contiene proyecciones. "
            "Revisa `prophet_metricas_ajuste` para identificar si hubo errores de instalación, CmdStan o series insuficientes."
        )
        st.dataframe(df_prophet_metricas, width="stretch", hide_index=True)
    else:
        df_pf = df_prophet_forecast.copy()
        df_pm = df_prophet_metricas.copy()

        bancos_prophet = sorted(df_pf["banco_estandarizado"].dropna().unique())
        indicadores_prophet = [i for i in KPI_PRINCIPALES if i in df_pf["indicador"].dropna().unique()]

        col_p1, col_p2 = st.columns([1.2, 1])

        with col_p1:
            banco_prophet = st.selectbox(
                "Banco",
                options=bancos_prophet,
                index=bancos_prophet.index("PICHINCHA") if "PICHINCHA" in bancos_prophet else 0,
                key="ml_prophet_banco",
            )

        with col_p2:
            indicador_prophet = st.selectbox(
                "Indicador",
                options=indicadores_prophet,
                format_func=lambda x: KPI_CONFIG[x]["label_largo"],
                index=0,
                key="ml_prophet_indicador",
            )

        serie_pf = df_pf[
            (df_pf["banco_estandarizado"] == banco_prophet)
            & (df_pf["indicador"] == indicador_prophet)
        ].copy().sort_values("ds")

        metrica_serie = df_pm[
            (df_pm["banco_estandarizado"].astype(str).str.upper() == banco_prophet)
            & (df_pm["indicador"].astype(str).str.lower() == indicador_prophet)
        ].copy()

        if serie_pf.empty:
            st.warning("No existe forecast para el banco e indicador seleccionados.")
        else:
            historico_real = serie_pf[serie_pf["valor_real"].notna()].copy()
            proyeccion = serie_pf[serie_pf["tipo"] == "proyeccion"].copy()

            ultimo_real = historico_real["valor_real"].iloc[-1] if not historico_real.empty else np.nan
            valor_final = proyeccion["yhat"].iloc[-1] if not proyeccion.empty else np.nan
            cambio_estimado = np.nan
            if pd.notna(ultimo_real) and pd.notna(valor_final) and ultimo_real != 0:
                cambio_estimado = ((valor_final - ultimo_real) / ultimo_real) * 100

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Último valor real", formato_valor(ultimo_real, indicador_prophet))
            c2.metric("Valor proyectado final", formato_valor(valor_final, indicador_prophet))
            c3.metric("Cambio estimado", "N/D" if pd.isna(cambio_estimado) else f"{cambio_estimado:,.2f}%")
            if not metrica_serie.empty:
                c4.metric("RMSE ajuste", f"{metrica_serie['rmse_ajuste'].iloc[0]:,.2f}")
            else:
                c4.metric("RMSE ajuste", "N/D")

            st.markdown("#### Histórico y proyección")
            fig_prophet = go.Figure()

            fig_prophet.add_trace(
                go.Scatter(
                    x=serie_pf["ds"],
                    y=serie_pf["yhat_upper"],
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                    name="Límite superior",
                )
            )
            fig_prophet.add_trace(
                go.Scatter(
                    x=serie_pf["ds"],
                    y=serie_pf["yhat_lower"],
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(37,99,235,0.16)",
                    line=dict(width=0),
                    name="Intervalo incertidumbre",
                    hoverinfo="skip",
                )
            )
            fig_prophet.add_trace(
                go.Scatter(
                    x=serie_pf["ds"],
                    y=serie_pf["yhat"],
                    mode="lines",
                    name="Estimación / Forecast",
                    line=dict(width=3, color="#2563EB"),
                )
            )
            fig_prophet.add_trace(
                go.Scatter(
                    x=historico_real["ds"],
                    y=historico_real["valor_real"],
                    mode="markers",
                    name="Valor real",
                    marker=dict(size=6, color="#0F172A"),
                )
            )

            if not proyeccion.empty:
                # Corrección: Plotly puede fallar con add_vline + Timestamp + annotation_text.
                # Por eso convierto la fecha a texto y uso add_shape + add_annotation.
                fecha_inicio_proyeccion = pd.to_datetime(proyeccion["ds"].min()).strftime("%Y-%m-%d")

                fig_prophet.add_shape(
                    type="line",
                    x0=fecha_inicio_proyeccion,
                    x1=fecha_inicio_proyeccion,
                    y0=0,
                    y1=1,
                    xref="x",
                    yref="paper",
                    line=dict(color="#EA580C", dash="dash", width=2)
                )

                fig_prophet.add_annotation(
                    x=fecha_inicio_proyeccion,
                    y=1,
                    xref="x",
                    yref="paper",
                    text="Inicio proyección",
                    showarrow=False,
                    yanchor="bottom",
                    xanchor="left",
                    font=dict(color="#64748B")
                )

            fig_prophet.update_layout(
                height=560,
                title=f"{KPI_CONFIG[indicador_prophet]['label_largo']} · {banco_prophet}",
                xaxis_title="Periodo",
                yaxis_title="Millones USD" if KPI_CONFIG[indicador_prophet]["unidad"] == "millones_usd" else "Porcentaje",
                hovermode="x unified",
                margin=dict(l=10, r=10, t=60, b=10),
                legend=dict(orientation="h", y=1.08),
            )
            st.plotly_chart(fig_prophet, width="stretch")

            st.markdown("#### Métricas y datos de la serie")
            col_tab1, col_tab2 = st.columns([1, 1])
            with col_tab1:
                if metrica_serie.empty:
                    st.info("No hay métricas de ajuste para esta serie.")
                else:
                    st.dataframe(metrica_serie, width="stretch", hide_index=True)
            with col_tab2:
                tabla_forecast = serie_pf[
                    ["periodo", "tipo", "valor_real", "yhat", "yhat_lower", "yhat_upper", "trend"]
                ].tail(24)
                st.dataframe(tabla_forecast, width="stretch", hide_index=True)

        st.markdown("#### Estado general de Prophet")
        resumen_prophet = (
            df_pm.groupby(["indicador", "estado"], dropna=False)
            .agg(series=("banco_estandarizado", "count"), observaciones_promedio=("observaciones", "mean"))
            .reset_index()
        )
        st.dataframe(resumen_prophet, width="stretch", hide_index=True)


# ============================================================
# TAB 8: Score inteligente de salud financiera
# ============================================================

with tab_score:
    st.markdown('<div class="section-title">Score inteligente de salud financiera</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Ranking 0-100 que combina ROE real vs estimado, perfil KMeans y, en el último año, tendencias Prophet. Es una lectura exploratoria, no una calificación regulatoria.</div>',
        unsafe_allow_html=True,
    )

    if df_score_salud is None or df_score_salud.empty:
        st.warning(
            "No encuentro `score_salud_bancaria` en `01_datos_procesados/modelos/`. "
            "Ejecuta primero `03_cuadernos/04_score_salud_bancaria_v2.ipynb`."
        )
    else:
        score_df_base = df_score_salud.copy()

        # Normalizo columnas principales para evitar errores por formatos.
        score_df_base["banco_estandarizado"] = score_df_base["banco_estandarizado"].astype(str).str.strip().str.upper()
        score_df_base["score_salud"] = pd.to_numeric(score_df_base["score_salud"], errors="coerce")

        # Si el score viene de la versión V2, debe traer columna anio.
        if "anio" in score_df_base.columns:
            score_df_base["anio"] = pd.to_numeric(score_df_base["anio"], errors="coerce").astype("Int64")
            anios_score = sorted(score_df_base["anio"].dropna().astype(int).unique())
        else:
            anios_score = []

        if not anios_score:
            st.warning(
                "El archivo `score_salud_bancaria` no tiene columna `anio`. "
                "Para visualizar histórico, ejecuta `04_score_salud_bancaria_v2.ipynb`."
            )
            score_df = score_df_base.copy()
            anio_score_sel = None
        else:
            col_anio, col_banco, col_top = st.columns([0.75, 1.25, 0.8])

            with col_anio:
                anio_score_sel = st.selectbox(
                    "Año score",
                    options=anios_score,
                    index=len(anios_score) - 1,
                    key="score_anio"
                )

            # Filtro por el año seleccionado.
            score_df = score_df_base[score_df_base["anio"] == anio_score_sel].copy()

            if score_df.empty:
                st.warning("No existe score para el año seleccionado.")
                st.stop()

            bancos_score = sorted(score_df["banco_estandarizado"].dropna().unique())

            with col_banco:
                banco_score = st.selectbox(
                    "Banco",
                    options=bancos_score,
                    index=bancos_score.index("PICHINCHA") if "PICHINCHA" in bancos_score else 0,
                    key="score_banco"
                )

            with col_top:
                top_score_n = st.slider(
                    "Top N ranking score",
                    min_value=3,
                    max_value=min(15, max(3, len(bancos_score))),
                    value=min(10, max(3, len(bancos_score))),
                    step=1,
                    key="score_top_n"
                )

            tipo_score_val = (
                score_df["tipo_score"].dropna().astype(str).unique()[0]
                if "tipo_score" in score_df.columns and not score_df["tipo_score"].dropna().empty
                else "N/D"
            )

            if tipo_score_val == "actual_con_proyecciones":
                st.info(
                    f"Mostrando score del año {anio_score_sel}. "
                    "Este es el score actual e incorpora componentes Prophet."
                )
            elif tipo_score_val == "historico_sin_proyecciones":
                st.info(
                    f"Mostrando score histórico del año {anio_score_sel}. "
                    "Este score usa RandomForestRegressor + KMeans y no incorpora Prophet para evitar fuga temporal."
                )
            else:
                st.caption(f"Tipo de score: {tipo_score_val}")

        # Si el archivo no tiene anio, creo controles mínimos.
        if not anios_score:
            bancos_score = sorted(score_df["banco_estandarizado"].dropna().unique())

            col_banco, col_top = st.columns([1.25, 0.8])

            with col_banco:
                banco_score = st.selectbox(
                    "Banco",
                    options=bancos_score,
                    index=bancos_score.index("PICHINCHA") if "PICHINCHA" in bancos_score else 0,
                    key="score_banco_sin_anio"
                )

            with col_top:
                top_score_n = st.slider(
                    "Top N ranking score",
                    min_value=3,
                    max_value=min(15, max(3, len(bancos_score))),
                    value=min(10, max(3, len(bancos_score))),
                    step=1,
                    key="score_top_n_sin_anio"
                )

        fila_score = score_df[score_df["banco_estandarizado"] == banco_score].copy()

        if fila_score.empty:
            st.warning("No existe score para el banco seleccionado en el año elegido.")
        else:
            fila_score = fila_score.iloc[0]

            score_valor = fila_score.get("score_salud", np.nan)
            lectura = fila_score.get("lectura_score", "Sin lectura")
            ranking = fila_score.get("ranking_score", np.nan)
            perfil = fila_score.get("perfil_cluster", "Sin perfil")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Score salud", "N/D" if pd.isna(score_valor) else f"{score_valor:,.2f}/100")
            c2.metric("Lectura", lectura)
            c3.metric("Ranking", "N/D" if pd.isna(ranking) else f"#{int(ranking)}")
            c4.metric("Perfil KMeans", perfil)

            st.markdown("#### Lectura ejecutiva automática")
            st.info(fila_score.get("analisis_ejecutivo", "No existe análisis ejecutivo para este banco."))

            col_g1, col_g2 = st.columns([1, 1.25])

            with col_g1:
                fig_gauge = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=0 if pd.isna(score_valor) else score_valor,
                        number={"suffix": "/100"},
                        title={"text": f"Score · {banco_score}"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": "#2563EB"},
                            "steps": [
                                {"range": [0, 45], "color": "#FEE2E2"},
                                {"range": [45, 60], "color": "#FEF3C7"},
                                {"range": [60, 75], "color": "#DBEAFE"},
                                {"range": [75, 100], "color": "#DCFCE7"},
                            ],
                        },
                    )
                )
                fig_gauge.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_gauge, width="stretch")

            with col_g2:
                componentes_cols = [
                    "puntaje_roe_modelo",
                    "puntaje_cluster",
                    "puntaje_tendencia_general",
                    "puntaje_morosidad_proyectada",
                    "puntaje_solvencia_proyectada",
                ]

                nombres_componentes = {
                    "puntaje_roe_modelo": "ROE real vs estimado",
                    "puntaje_cluster": "Perfil KMeans",
                    "puntaje_tendencia_general": "Tendencia futura",
                    "puntaje_morosidad_proyectada": "Morosidad proyectada",
                    "puntaje_solvencia_proyectada": "Solvencia proyectada",
                }

                data_componentes = []

                for col in componentes_cols:
                    if col in score_df.columns:
                        valor_comp = fila_score.get(col, np.nan)

                        if pd.notna(valor_comp):
                            data_componentes.append({
                                "componente": nombres_componentes[col],
                                "puntaje": valor_comp
                            })

                df_comp = pd.DataFrame(data_componentes)

                if df_comp.empty:
                    st.warning("No hay componentes disponibles para graficar.")
                else:
                    fig_comp = px.bar(
                        df_comp.sort_values("puntaje"),
                        x="puntaje",
                        y="componente",
                        orientation="h",
                        text=df_comp.sort_values("puntaje")["puntaje"].map(lambda x: f"{x:.2f}"),
                        range_x=[0, 100],
                        title="Componentes del score"
                    )
                    fig_comp.update_traces(textposition="outside", marker_color="#2563EB")
                    fig_comp.update_layout(
                        height=360,
                        xaxis_title="Puntaje 0-100",
                        yaxis_title="Componente",
                        margin=dict(l=10, r=30, t=50, b=10)
                    )
                    st.plotly_chart(fig_comp, width="stretch")

        st.markdown("#### Ranking general de salud financiera")

        ranking_score_df = score_df.sort_values("score_salud", ascending=False).head(top_score_n).copy()

        fig_score_rank = px.bar(
            ranking_score_df.sort_values("score_salud"),
            x="score_salud",
            y="banco_estandarizado",
            orientation="h",
            text=ranking_score_df.sort_values("score_salud")["score_salud"].map(lambda x: f"{x:.2f}"),
            color="score_salud",
            color_continuous_scale="RdYlGn",
            range_x=[0, 100],
            title=f"Top {top_score_n} bancos por score inteligente"
        )
        fig_score_rank.update_traces(textposition="outside")
        fig_score_rank.update_layout(
            height=480,
            xaxis_title="Score 0-100",
            yaxis_title="Banco",
            coloraxis_showscale=False,
            margin=dict(l=10, r=30, t=60, b=10)
        )
        st.plotly_chart(fig_score_rank, width="stretch")

        # Si existe histórico, muestro evolución del score del banco seleccionado.
        if "anio" in score_df_base.columns:
            st.markdown("#### Evolución histórica del score del banco")

            hist_score_banco = score_df_base[
                score_df_base["banco_estandarizado"] == banco_score
            ].copy()

            hist_score_banco = hist_score_banco.sort_values("anio")

            if not hist_score_banco.empty:
                fig_hist_score = px.line(
                    hist_score_banco,
                    x="anio",
                    y="score_salud",
                    markers=True,
                    title=f"Evolución del score · {banco_score}",
                    labels={
                        "anio": "Año",
                        "score_salud": "Score 0-100"
                    }
                )
                fig_hist_score.update_yaxes(range=[0, 100])
                fig_hist_score.update_layout(
                    height=420,
                    margin=dict(l=10, r=10, t=55, b=10)
                )
                st.plotly_chart(fig_hist_score, width="stretch")

        st.markdown("#### Tabla completa del score")

        columnas_mostrar_score = [
            "anio",
            "tipo_score",
            "ranking_score",
            "banco_estandarizado",
            "score_salud",
            "lectura_score",
            "perfil_cluster",
            "puntaje_roe_modelo",
            "puntaje_cluster",
            "puntaje_tendencia_general",
            "puntaje_morosidad_proyectada",
            "puntaje_solvencia_proyectada",
            "analisis_ejecutivo",
        ]

        columnas_mostrar_score = [c for c in columnas_mostrar_score if c in score_df.columns]

        st.dataframe(
            score_df[columnas_mostrar_score].sort_values("score_salud", ascending=False),
            width="stretch",
            hide_index=True
        )

        with st.expander("Metodología del score"):
            st.markdown(
                """
                El score se calcula como una media ponderada de componentes disponibles.

                | Componente | Fuente | Peso |
                |---|---|---:|
                | ROE real vs ROE estimado | RandomForestRegressor | 25% |
                | Perfil financiero | KMeans | 20% |
                | Tendencia futura general | Prophet | 20% |
                | Morosidad proyectada | Prophet | 20% |
                | Solvencia proyectada | Prophet | 15% |

                **Regla para evitar fuga temporal:**

                - En años históricos se usa `RandomForestRegressor + KMeans`.
                - En el último año disponible se usa `RandomForestRegressor + KMeans + Prophet`.

                Si falta algún componente, el peso se redistribuye entre los componentes disponibles.

                **Interpretación:**

                - 75 a 100: Salud financiera favorable.
                - 60 a 74.99: Perfil financiero sólido.
                - 45 a 59.99: Perfil intermedio con seguimiento.
                - 0 a 44.99: Requiere revisión.

                Este score es exploratorio y no representa una calificación regulatoria oficial.
                """
            )


st.divider()
st.caption("Dashboard V2 + Modelos ML. Valores monetarios en millones de USD; porcentajes en valor directo. Incluye RandomForestRegressor para ROE, KMeans para segmentación bancaria, Prophet para proyecciones exploratorias y un score inteligente histórico/anual de salud financiera. No se utilizan gráficos de pastel.")
