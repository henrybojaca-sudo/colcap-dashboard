"""
Dashboard COLCAP — Acciones Colombia
Inspirado en el GDP Dashboard template de Streamlit
Datos en tiempo real via yfinance · Bolsa de Valores de Colombia
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import date, timedelta
import numpy as np

# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="COLCAP Dashboard",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# CATÁLOGO ACCIONES COLCAP (ticker Yahoo Finance · sufijo .CL = BVC)
# ─────────────────────────────────────────────────────────────────
ACCIONES = {
    "COLCAP (Índice)":        {"ticker": "^COLCAP",        "sector": "Índice"},
    "Ecopetrol":              {"ticker": "ECOPETL.CL",     "sector": "Energía"},
    "Bancolombia":            {"ticker": "BCOLO.CL",       "sector": "Financiero"},
    "Pref. Bancolombia":      {"ticker": "PFBCOLO.CL",     "sector": "Financiero"},
    "Grupo Sura":             {"ticker": "GRUPOSURA.CL",   "sector": "Financiero"},
    "Pref. Grupo Sura":       {"ticker": "PFGRUPSURA.CL",  "sector": "Financiero"},
    "Grupo Argos":            {"ticker": "GRUPOARGOS.CL",  "sector": "Industrial"},
    "Cementos Argos":         {"ticker": "CEMARGOS.CL",    "sector": "Industrial"},
    "Nutresa":                {"ticker": "NUTRESA.CL",     "sector": "Consumo"},
    "ISA":                    {"ticker": "ISA.CL",         "sector": "Energía"},
    "GEB":                    {"ticker": "GEB.CL",         "sector": "Energía"},
    "Celsia":                 {"ticker": "CELSIA.CL",      "sector": "Energía"},
    "Mineros":                {"ticker": "MINEROS.CL",     "sector": "Materiales"},
    "Canacol Energy":         {"ticker": "CNE.TO",         "sector": "Energía"},
    "Corficolombiana":        {"ticker": "CORFICOLCF.CL",  "sector": "Financiero"},
    "Promigas":               {"ticker": "PROMIGAS.CL",    "sector": "Energía"},
    "ETB":                    {"ticker": "ETB.CL",         "sector": "Telecom"},
    "Almacenes Éxito":        {"ticker": "EXITO.CL",       "sector": "Consumo"},
    "Pref. Corficolombiana":  {"ticker": "PFCORFICOL.CL",  "sector": "Financiero"},
}

SECTOR_COLORS = {
    "Energía":    "#f59e0b",
    "Financiero": "#3b82f6",
    "Industrial": "#8b5cf6",
    "Consumo":    "#10b981",
    "Materiales": "#ef4444",
    "Telecom":    "#06b6d4",
    "Índice":     "#64748b",
}

PERIODOS = {
    "1 Mes":   30,
    "3 Meses": 90,
    "6 Meses": 180,
    "1 Año":   365,
    "2 Años":  730,
    "5 Años":  1825,
}

DEFAULTS = ["COLCAP (Índice)", "Ecopetrol", "Bancolombia",
            "Grupo Sura", "Grupo Argos", "Nutresa"]

# ─────────────────────────────────────────────────────────────────
# CSS — clean light theme
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background: #f8fafc;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* ── Reduce main content width ── */
.block-container {
    padding: 1.4rem 1.6rem 1.8rem;
    max-width: 960px;
}

/* ── Header ── */
.dash-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 2px 0 14px;
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 18px;
}
.dash-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1;
    margin: 0;
    letter-spacing: -0.5px;
}
.dash-title .accent {
    color: #0ea5e9;
}
.dash-badge {
    display: inline-block;
    background: #f0f9ff;
    color: #0ea5e9;
    border: 1px solid #bae6fd;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 600;
    padding: 2px 7px;
    letter-spacing: 0.08em;
    margin-left: 8px;
    vertical-align: middle;
    text-transform: uppercase;
}
.dash-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #94a3b8;
    text-align: right;
    line-height: 1.8;
}

/* ── KPI Cards ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 22px;
}
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 13px 15px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow .15s;
}
.kpi-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 10px 10px 0 0;
}
.kpi-card.up::before   { background: linear-gradient(90deg, #0ea5e9, #34d399); }
.kpi-card.down::before { background: linear-gradient(90deg, #f87171, #fb923c); }
.kpi-card.flat::before { background: linear-gradient(90deg, #94a3b8, #cbd5e1); }
.kpi-card.info::before { background: linear-gradient(90deg, #818cf8, #a78bfa); }

.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 7px;
}
.kpi-value {
    font-family: 'Inter', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-sub {
    font-size: 0.72rem;
    font-weight: 500;
    margin-top: 4px;
}
.kpi-sub.up   { color: #10b981; }
.kpi-sub.down { color: #ef4444; }
.kpi-sub.flat { color: #94a3b8; }

/* ── Section title ── */
.section-hd {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin: 22px 0 10px;
    padding-bottom: 7px;
    border-bottom: 1px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 6px;
}
.section-hd::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: linear-gradient(180deg, #0ea5e9, #818cf8);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── Sidebar typography ── */
.sb-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: #0ea5e9;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 16px 0 6px;
    font-weight: 600;
}
.sb-logo-title {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
}
.sb-logo-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: #94a3b8;
    margin-top: 2px;
    letter-spacing: 0.06em;
}

/* ── Table ── */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Download buttons ── */
div[data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: #0ea5e9 !important;
    color: #0ea5e9 !important;
    background: #f0f9ff !important;
}

/* ── Streamlit overrides ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar scrollbar ── */
section[data-testid="stSidebar"] ::-webkit-scrollbar { width: 4px; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# FUNCIONES DE DATOS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def load_prices(tickers_tuple: tuple, start: str, end: str) -> pd.DataFrame:
    """Descarga precios de cierre ajustados via yfinance."""
    frames = {}
    for name in tickers_tuple:
        ticker = ACCIONES[name]["ticker"]
        try:
            raw = yf.download(ticker, start=start, end=end,
                              progress=False, auto_adjust=True)
            if raw.empty:
                continue
            close = raw["Close"] if "Close" in raw.columns else raw.iloc[:, 0]
            s = close.squeeze()
            if not s.empty:
                frames[name] = s
        except Exception:
            pass
    if not frames:
        return pd.DataFrame()
    df = pd.DataFrame(frames)
    df.index = pd.to_datetime(df.index)
    df.index.name = "Fecha"
    return df.dropna(how="all")


def retorno(s: pd.Series) -> float:
    s = s.dropna()
    return (s.iloc[-1] / s.iloc[0] - 1) * 100 if len(s) >= 2 else 0.0


def volatilidad(s: pd.Series) -> float:
    s = s.dropna()
    if len(s) < 5:
        return 0.0
    return s.pct_change().dropna().std() * np.sqrt(252) * 100


def base100(df: pd.DataFrame) -> pd.DataFrame:
    first = df.apply(lambda s: s.dropna().iloc[0] if s.dropna().shape[0] else np.nan)
    return df.div(first) * 100


# Colores comunes para gráficos en tema claro
CHART_FONT   = dict(family="Inter", color="#475569", size=11)
CHART_GRID   = "#f1f5f9"
CHART_ZERO   = "#e2e8f0"
CHART_BG     = "white"
CHART_LEGEND = dict(
    bgcolor="rgba(255,255,255,0.95)", bordercolor="#e2e8f0", borderwidth=1,
    font=dict(size=10, color="#475569"), orientation="h",
    yanchor="bottom", y=1.02, xanchor="left", x=0,
)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 2px">
        <div class="sb-logo-title">📈 COLCAP</div>
        <div class="sb-logo-sub">BOLSA DE VALORES DE COLOMBIA</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Periodo ──────────────────────────────────────────────────
    st.markdown('<div class="sb-section">⏱ Periodo</div>', unsafe_allow_html=True)
    periodo_label = st.selectbox(
        "Periodo", list(PERIODOS.keys()), index=3,
        label_visibility="collapsed"
    )
    dias = PERIODOS[periodo_label]
    fecha_fin    = date.today()
    fecha_inicio = fecha_fin - timedelta(days=dias)

    with st.expander("📅 Rango personalizado"):
        fecha_inicio = st.date_input("Desde", value=fecha_inicio,
                                     min_value=date(2010, 1, 1), max_value=fecha_fin)
        fecha_fin    = st.date_input("Hasta", value=fecha_fin,
                                     min_value=fecha_inicio, max_value=date.today())

    st.divider()

    # ── Sector filter ─────────────────────────────────────────────
    st.markdown('<div class="sb-section">🏭 Sector</div>', unsafe_allow_html=True)
    sectores_disp = sorted({v["sector"] for v in ACCIONES.values()})
    sectores_sel  = st.multiselect("Sectores", sectores_disp,
                                   default=sectores_disp,
                                   label_visibility="collapsed")

    acciones_disp = [k for k, v in ACCIONES.items() if v["sector"] in sectores_sel]

    # ── Acciones ──────────────────────────────────────────────────
    st.markdown('<div class="sb-section">🏢 Acciones</div>', unsafe_allow_html=True)
    acciones_sel = st.multiselect(
        "Acciones", acciones_disp,
        default=[a for a in DEFAULTS if a in acciones_disp],
        label_visibility="collapsed",
    )

    if not acciones_sel:
        st.warning("Selecciona al menos una acción.")
        st.stop()

    st.divider()

    # ── Opciones ──────────────────────────────────────────────────
    st.markdown('<div class="sb-section">⚙️ Opciones</div>', unsafe_allow_html=True)
    modo = st.radio("Modo precio", ["Base 100 (comparativa)", "Precio absoluto (COP)"],
                    index=0, label_visibility="collapsed")
    mostrar_corr = st.checkbox("Matriz de correlación", value=True)

    st.divider()
    st.caption("Datos: Yahoo Finance")
    st.caption(f"Caché: 15 min · {date.today().strftime('%d/%m/%Y')}")


# ─────────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────
with st.spinner("Conectando con Yahoo Finance..."):
    df_raw = load_prices(
        tuple(acciones_sel),
        str(fecha_inicio),
        str(fecha_fin + timedelta(days=1))
    )

if df_raw.empty:
    st.error("⚠️ No se pudieron obtener datos. Intenta con otro período o acción.")
    st.stop()

cols_ok = [c for c in acciones_sel if c in df_raw.columns]
df = df_raw[cols_ok].copy()

# Separar índice de acciones para métricas
solo_acciones = [c for c in cols_ok if c != "COLCAP (Índice)"] or cols_ok


# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
    <div>
        <div class="dash-title">
            Acciones <span class="accent">COLCAP</span>
            <span class="dash-badge">BVC</span>
        </div>
    </div>
    <div class="dash-meta">
        {fecha_inicio.strftime('%d %b %Y')} → {fecha_fin.strftime('%d %b %Y')}<br>
        {len(cols_ok)} activos &nbsp;·&nbsp; {len(df)} sesiones<br>
        {periodo_label}
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────
rets  = {c: retorno(df[c])     for c in solo_acciones}
vols  = {c: volatilidad(df[c]) for c in solo_acciones}
mejor = max(rets, key=rets.get)
peor  = min(rets, key=rets.get)
ret_prom = np.mean(list(rets.values()))
vol_prom = np.mean(list(vols.values()))


def kpi(label, value_str, sub_str, card_class, sub_class):
    return f"""
    <div class="kpi-card {card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value_str}</div>
        <div class="kpi-sub {sub_class}">{sub_str}</div>
    </div>"""


c1 = "up" if ret_prom >= 0 else "down"
s1 = "up" if ret_prom >= 0 else "down"
mejor_r = rets[mejor]
peor_r  = rets[peor]

html_kpi = '<div class="kpi-row">'
html_kpi += kpi("Retorno promedio", f"{ret_prom:+.1f}%",
                f"{'▲' if ret_prom>=0 else '▼'} {periodo_label}", c1, s1)
html_kpi += kpi("Volatilidad media", f"{vol_prom:.1f}%",
                "Anualizada · σ × √252", "info", "flat")
html_kpi += kpi("Mejor desempeño", mejor,
                f"{'▲' if mejor_r>=0 else '▼'} {mejor_r:+.2f}%", "up", "up")
html_kpi += kpi("Menor desempeño", peor,
                f"{'▼' if peor_r<0 else '▲'} {peor_r:+.2f}%", "down", "down")
html_kpi += '</div>'
st.markdown(html_kpi, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# GRÁFICO PRINCIPAL — Evolución
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hd">Evolución de precios</div>', unsafe_allow_html=True)

df_plot = base100(df) if "Base 100" in modo else df
y_label = "Base 100" if "Base 100" in modo else "Precio cierre (COP)"

fig_main = go.Figure()
for col in cols_ok:
    if col not in df_plot.columns:
        continue
    sec   = ACCIONES[col]["sector"]
    color = SECTOR_COLORS.get(sec, "#94a3b8")
    dash  = "dot"  if col == "COLCAP (Índice)" else "solid"
    width = 2.5    if col == "COLCAP (Índice)" else 1.8
    s = df_plot[col].dropna()
    fig_main.add_trace(go.Scatter(
        x=s.index, y=s.values, name=col, mode="lines",
        line=dict(color=color, width=width, dash=dash),
        hovertemplate=f"<b>{col}</b><br>%{{x|%d %b %Y}}<br>{y_label}: %{{y:,.2f}}<extra></extra>",
    ))

fig_main.update_layout(
    paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
    font=CHART_FONT,
    margin=dict(l=0, r=0, t=8, b=0), height=360,
    legend=CHART_LEGEND,
    xaxis=dict(
        gridcolor=CHART_GRID, zeroline=False,
        showspikes=True, spikecolor="#0ea5e9",
        spikethickness=1, spikedash="dot",
        linecolor=CHART_ZERO,
    ),
    yaxis=dict(
        gridcolor=CHART_GRID, zeroline=False, title=y_label,
        title_font=dict(size=10), linecolor=CHART_ZERO,
    ),
    hovermode="x unified",
)
st.plotly_chart(fig_main, use_container_width=True,
                config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# FILA 2 — Retornos + Volatilidad
# ─────────────────────────────────────────────────────────────────
ca, cb = st.columns(2, gap="medium")

with ca:
    st.markdown('<div class="section-hd">Retorno del período</div>', unsafe_allow_html=True)
    df_ret = (pd.DataFrame({"Acción": list(rets.keys()),
                             "Retorno": list(rets.values())})
              .sort_values("Retorno", ascending=True))

    fig_ret = go.Figure(go.Bar(
        x=df_ret["Retorno"], y=df_ret["Acción"], orientation="h",
        marker_color=["#10b981" if r >= 0 else "#f87171" for r in df_ret["Retorno"]],
        marker_opacity=0.80,
        text=[f"{v:+.1f}%" for v in df_ret["Retorno"]],
        textposition="outside", textfont=dict(size=10, color="#64748b"),
        hovertemplate="<b>%{y}</b>  %{x:.2f}%<extra></extra>",
    ))
    fig_ret.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=CHART_FONT,
        margin=dict(l=0, r=50, t=0, b=0),
        height=max(240, len(solo_acciones) * 34),
        xaxis=dict(gridcolor=CHART_GRID, zeroline=True,
                   zerolinecolor=CHART_ZERO, zerolinewidth=1),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_ret, use_container_width=True,
                    config={"displayModeBar": False})

with cb:
    st.markdown('<div class="section-hd">Volatilidad anualizada</div>', unsafe_allow_html=True)
    df_vol = (pd.DataFrame({"Acción": list(vols.keys()),
                             "Volatilidad": list(vols.values())})
              .sort_values("Volatilidad", ascending=True))

    fig_vol = go.Figure(go.Bar(
        x=df_vol["Volatilidad"], y=df_vol["Acción"], orientation="h",
        marker_color="#818cf8", marker_opacity=0.70,
        text=[f"{v:.1f}%" for v in df_vol["Volatilidad"]],
        textposition="outside", textfont=dict(size=10, color="#64748b"),
        hovertemplate="<b>%{y}</b>  σ=%{x:.2f}%<extra></extra>",
    ))
    fig_vol.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=CHART_FONT,
        margin=dict(l=0, r=50, t=0, b=0),
        height=max(240, len(solo_acciones) * 34),
        xaxis=dict(gridcolor=CHART_GRID, zeroline=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_vol, use_container_width=True,
                    config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# CORRELACIÓN
# ─────────────────────────────────────────────────────────────────
if mostrar_corr and len(cols_ok) >= 2:
    st.markdown('<div class="section-hd">Correlación de retornos diarios</div>',
                unsafe_allow_html=True)
    corr = df[cols_ok].pct_change().dropna().corr()
    zvals = np.round(corr.values, 2)

    fig_corr = go.Figure(go.Heatmap(
        z=zvals,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[[0.0, "#fca5a5"], [0.5, "#f8fafc"], [1.0, "#6ee7b7"]],
        zmin=-1, zmax=1,
        text=zvals, texttemplate="%{text:.2f}",
        textfont=dict(size=9, color="#334155"),
        hovertemplate="<b>%{y} × %{x}</b><br>ρ = %{z:.3f}<extra></extra>",
        showscale=True,
        colorbar=dict(
            tickfont=dict(color="#94a3b8", size=9),
            outlinecolor="#e2e8f0", outlinewidth=1, thickness=10,
        ),
    ))
    fig_corr.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=CHART_FONT,
        margin=dict(l=0, r=0, t=0, b=0),
        height=max(280, len(cols_ok) * 48),
    )
    st.plotly_chart(fig_corr, use_container_width=True,
                    config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# TABLA RESUMEN
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hd">Resumen estadístico</div>', unsafe_allow_html=True)

rows = []
for col in cols_ok:
    s = df[col].dropna()
    if len(s) < 2:
        continue
    rd = s.pct_change().dropna()
    rows.append({
        "Acción":            col,
        "Sector":            ACCIONES[col]["sector"],
        "Precio actual":     f"${s.iloc[-1]:,.1f}",
        "Retorno período":   f"{retorno(s):+.2f}%",
        "Vol. anual":        f"{volatilidad(s):.1f}%",
        "Ret. diario medio": f"{rd.mean()*100:+.3f}%",
        "Máx. período":      f"${s.max():,.1f}",
        "Mín. período":      f"${s.min():,.1f}",
        "Sesiones":          len(s),
    })

st.dataframe(
    pd.DataFrame(rows),
    hide_index=True,
    use_container_width=True,
    height=min(380, 40 + len(rows) * 36),
)


# ─────────────────────────────────────────────────────────────────
# DESCARGA
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hd">Exportar datos</div>', unsafe_allow_html=True)
dl1, dl2, _ = st.columns([1, 1, 2], gap="small")

with dl1:
    csv_p = df.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Precios (CSV)", data=csv_p,
                       file_name=f"colcap_precios_{fecha_inicio}_{fecha_fin}.csv",
                       mime="text/csv", use_container_width=True)
with dl2:
    csv_r = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Resumen (CSV)", data=csv_r,
                       file_name=f"colcap_resumen_{fecha_inicio}_{fecha_fin}.csv",
                       mime="text/csv", use_container_width=True)
