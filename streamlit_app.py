"""
Dashboard COLCAP — Acciones Colombia
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
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# CATÁLOGO ACCIONES
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
# CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── App ── */
.stApp { background: #f1f5f9; }

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] ::-webkit-scrollbar { width: 3px; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: #e2e8f0; border-radius: 4px;
}

.block-container {
    padding: 0 2rem 2rem;
    max-width: 1200px;
}

/* ── Top banner ── */
.top-banner {
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
    margin: 0 -2rem 0;
    padding: 18px 2rem 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}
.top-banner-title {
    font-size: 1.5rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.5px;
    line-height: 1;
}
.top-banner-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: rgba(255,255,255,0.7);
    margin-top: 4px;
    letter-spacing: 0.06em;
}
.top-banner-right {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: rgba(255,255,255,0.75);
    text-align: right;
    line-height: 1.8;
}
.top-banner-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    font-weight: 600;
    padding: 2px 7px;
    letter-spacing: 0.08em;
    color: #fff;
    text-transform: uppercase;
    margin-left: 8px;
    vertical-align: middle;
}

/* ── KPI Cards ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
@media (max-width: 900px) {
    .kpi-row { grid-template-columns: repeat(2, 1fr); }
}
.kpi-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px 18px 14px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04);
    transition: transform .15s, box-shadow .15s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.09);
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 0 0 12px 12px;
}
.kpi-card.up::after   { background: linear-gradient(90deg, #0ea5e9, #34d399); }
.kpi-card.down::after { background: linear-gradient(90deg, #f87171, #fb923c); }
.kpi-card.flat::after { background: linear-gradient(90deg, #94a3b8, #cbd5e1); }
.kpi-card.info::after { background: linear-gradient(90deg, #818cf8, #a78bfa); }

.kpi-icon {
    font-size: 1.3rem;
    margin-bottom: 8px;
    display: block;
}
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 5px;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    letter-spacing: -0.5px;
}
.kpi-sub {
    font-size: 0.72rem;
    font-weight: 500;
    margin-top: 5px;
}
.kpi-sub.up   { color: #10b981; }
.kpi-sub.down { color: #ef4444; }
.kpi-sub.flat { color: #94a3b8; }
.kpi-sub.info { color: #818cf8; }

/* ── Section header ── */
.section-hd {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 24px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
}
.section-hd-bar {
    width: 3px;
    height: 14px;
    border-radius: 2px;
    flex-shrink: 0;
}
.section-hd-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    flex: 1;
}
.section-hd-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    background: #f1f5f9;
    color: #94a3b8;
    border-radius: 4px;
    padding: 2px 6px;
    letter-spacing: 0.05em;
}

/* ── Sector pill ── */
.sector-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* ── Sidebar ── */
.sb-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: #0ea5e9;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 14px 0 5px;
    font-weight: 600;
}
.sb-logo-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
}
.sb-logo-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.52rem;
    color: #94a3b8;
    margin-top: 2px;
    letter-spacing: 0.06em;
}

/* ── Table ── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* ── Download buttons ── */
div[data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    transition: all .12s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: #0ea5e9 !important;
    color: #0ea5e9 !important;
    background: #f0f9ff !important;
    transform: translateY(-1px);
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# FUNCIONES DE DATOS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def load_prices(tickers_tuple: tuple, start: str, end: str) -> pd.DataFrame:
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


def max_drawdown(s: pd.Series) -> float:
    s = s.dropna()
    if len(s) < 2:
        return 0.0
    roll_max = s.cummax()
    dd = (s - roll_max) / roll_max * 100
    return dd.min()


def sharpe_ratio(s: pd.Series) -> float:
    s = s.dropna()
    if len(s) < 10:
        return 0.0
    rd = s.pct_change().dropna()
    if rd.std() == 0:
        return 0.0
    return rd.mean() / rd.std() * np.sqrt(252)


def drawdown_series(s: pd.Series) -> pd.Series:
    s = s.dropna()
    roll_max = s.cummax()
    return (s - roll_max) / roll_max * 100


def base100(df: pd.DataFrame) -> pd.DataFrame:
    first = df.apply(lambda s: s.dropna().iloc[0] if s.dropna().shape[0] else np.nan)
    return df.div(first) * 100


def moving_avg(s: pd.Series, window: int) -> pd.Series:
    return s.rolling(window=window, min_periods=window // 2).mean()


# Shared chart theme
CHART_FONT   = dict(family="Inter", color="#475569", size=11)
CHART_GRID   = "#f1f5f9"
CHART_ZERO   = "#e2e8f0"
CHART_BG     = "white"
CHART_LEGEND = dict(
    bgcolor="rgba(255,255,255,0.96)", bordercolor="#e2e8f0", borderwidth=1,
    font=dict(size=10, color="#475569"), orientation="h",
    yanchor="bottom", y=1.02, xanchor="left", x=0,
)

SECTION_GRADIENTS = {
    "blue":   "linear-gradient(180deg,#0ea5e9,#6366f1)",
    "green":  "linear-gradient(180deg,#10b981,#0ea5e9)",
    "purple": "linear-gradient(180deg,#8b5cf6,#ec4899)",
    "orange": "linear-gradient(180deg,#f59e0b,#ef4444)",
    "teal":   "linear-gradient(180deg,#06b6d4,#10b981)",
}


def section(text: str, color: str = "blue", chip: str = "") -> None:
    chip_html = f'<span class="section-hd-chip">{chip}</span>' if chip else ""
    st.markdown(f"""
    <div class="section-hd">
        <div class="section-hd-bar" style="background:{SECTION_GRADIENTS[color]}"></div>
        <span class="section-hd-text">{text}</span>
        {chip_html}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 4px">
        <div class="sb-logo-title">📈 COLCAP</div>
        <div class="sb-logo-sub">BOLSA DE VALORES DE COLOMBIA</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="sb-section">⏱ Periodo</div>', unsafe_allow_html=True)
    periodo_label = st.selectbox("Periodo", list(PERIODOS.keys()), index=3,
                                 label_visibility="collapsed")
    dias = PERIODOS[periodo_label]
    fecha_fin    = date.today()
    fecha_inicio = fecha_fin - timedelta(days=dias)

    with st.expander("📅 Rango personalizado"):
        fecha_inicio = st.date_input("Desde", value=fecha_inicio,
                                     min_value=date(2010, 1, 1), max_value=fecha_fin)
        fecha_fin    = st.date_input("Hasta", value=fecha_fin,
                                     min_value=fecha_inicio, max_value=date.today())
    st.divider()

    st.markdown('<div class="sb-section">🏭 Sector</div>', unsafe_allow_html=True)
    sectores_disp = sorted({v["sector"] for v in ACCIONES.values()})
    sectores_sel  = st.multiselect("Sectores", sectores_disp, default=sectores_disp,
                                   label_visibility="collapsed")
    acciones_disp = [k for k, v in ACCIONES.items() if v["sector"] in sectores_sel]

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

    st.markdown('<div class="sb-section">⚙️ Gráfico principal</div>', unsafe_allow_html=True)
    modo = st.radio("Modo precio", ["Base 100 (comparativa)", "Precio absoluto (COP)"],
                    index=0, label_visibility="collapsed")
    mostrar_ma = st.checkbox("Medias móviles (MA20 · MA50)", value=False)
    st.divider()

    st.markdown('<div class="sb-section">📊 Secciones</div>', unsafe_allow_html=True)
    mostrar_drawdown = st.checkbox("Drawdown", value=True)
    mostrar_sector   = st.checkbox("Distribución sectorial", value=True)
    mostrar_corr     = st.checkbox("Correlación", value=True)
    st.divider()

    st.caption("Datos: Yahoo Finance · Caché 15 min")
    st.caption(f"Actualizado: {date.today().strftime('%d/%m/%Y')}")


# ─────────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────
with st.spinner("Cargando datos..."):
    df_raw = load_prices(
        tuple(acciones_sel),
        str(fecha_inicio),
        str(fecha_fin + timedelta(days=1)),
    )

if df_raw.empty:
    st.error("⚠️ Sin datos. Intenta con otro período o acción.")
    st.stop()

cols_ok       = [c for c in acciones_sel if c in df_raw.columns]
df            = df_raw[cols_ok].copy()
solo_acciones = [c for c in cols_ok if c != "COLCAP (Índice)"] or cols_ok


# ─────────────────────────────────────────────────────────────────
# TOP BANNER
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-banner">
    <div>
        <div class="top-banner-title">
            Acciones COLCAP
            <span class="top-banner-badge">BVC</span>
        </div>
        <div class="top-banner-sub">Bolsa de Valores de Colombia · Datos en tiempo real</div>
    </div>
    <div class="top-banner-right">
        {fecha_inicio.strftime('%d %b %Y')} → {fecha_fin.strftime('%d %b %Y')}<br>
        {len(cols_ok)} activos &nbsp;·&nbsp; {len(df)} sesiones de bolsa<br>
        Período: {periodo_label}
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────
rets     = {c: retorno(df[c])      for c in solo_acciones}
vols     = {c: volatilidad(df[c])  for c in solo_acciones}
mdd_dict = {c: max_drawdown(df[c]) for c in solo_acciones}
mejor    = max(rets, key=rets.get)
peor     = min(rets, key=rets.get)
ret_prom = np.mean(list(rets.values()))
vol_prom = np.mean(list(vols.values()))
mdd_prom = np.mean(list(mdd_dict.values()))

c1 = "up" if ret_prom >= 0 else "down"
s1 = "up" if ret_prom >= 0 else "down"

def kpi(icon, label, value_str, sub_str, card_class, sub_class):
    return f"""
    <div class="kpi-card {card_class}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value_str}</div>
        <div class="kpi-sub {sub_class}">{sub_str}</div>
    </div>"""

html_kpi  = '<div class="kpi-row">'
html_kpi += kpi("📈", "Retorno promedio",   f"{ret_prom:+.1f}%",
                f"{'▲' if ret_prom>=0 else '▼'} {periodo_label}", c1, s1)
html_kpi += kpi("〜", "Volatilidad media",  f"{vol_prom:.1f}%",
                "Anualizada · σ × √252", "info", "info")
html_kpi += kpi("🏆", "Mejor desempeño",    mejor,
                f"▲ {rets[mejor]:+.2f}%", "up", "up")
html_kpi += kpi("📉", "Drawdown promedio",  f"{mdd_prom:.1f}%",
                "Máx. caída desde pico", "down", "down")
html_kpi += '</div>'
st.markdown(html_kpi, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# GRÁFICO PRINCIPAL
# ─────────────────────────────────────────────────────────────────
section("Evolución de precios", "blue",
        chip=f"{len(cols_ok)} activos · {modo.split('(')[0].strip()}")

df_plot = base100(df) if "Base 100" in modo else df
y_label = "Base 100" if "Base 100" in modo else "Precio cierre (COP)"

fig_main = go.Figure()
for col in cols_ok:
    if col not in df_plot.columns:
        continue
    sec   = ACCIONES[col]["sector"]
    color = SECTOR_COLORS.get(sec, "#94a3b8")
    dash  = "dot"   if col == "COLCAP (Índice)" else "solid"
    width = 2.5     if col == "COLCAP (Índice)" else 1.8
    s = df_plot[col].dropna()
    fig_main.add_trace(go.Scatter(
        x=s.index, y=s.values, name=col, mode="lines",
        line=dict(color=color, width=width, dash=dash),
        hovertemplate=f"<b>{col}</b><br>%{{x|%d %b %Y}}<br>{y_label}: %{{y:,.2f}}<extra></extra>",
    ))
    if mostrar_ma and col != "COLCAP (Índice)":
        raw_s = df[col].dropna()
        for win, clr in [(20, "#0ea5e9"), (50, "#8b5cf6")]:
            ma = moving_avg(raw_s, win)
            if "Base 100" in modo:
                first_val = raw_s.dropna().iloc[0]
                ma = ma / first_val * 100
            fig_main.add_trace(go.Scatter(
                x=ma.index, y=ma.values,
                name=f"MA{win} · {col}", mode="lines",
                line=dict(color=clr, width=1.2, dash="dash"),
                opacity=0.55, showlegend=False,
                hovertemplate=f"MA{win} {col}: %{{y:,.2f}}<extra></extra>",
            ))

fig_main.update_layout(
    paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
    font=CHART_FONT, height=400,
    margin=dict(l=0, r=0, t=36, b=0),
    legend=CHART_LEGEND,
    xaxis=dict(gridcolor=CHART_GRID, zeroline=False,
               showspikes=True, spikecolor="#0ea5e9",
               spikethickness=1, spikedash="dot", linecolor=CHART_ZERO),
    yaxis=dict(gridcolor=CHART_GRID, zeroline=False, title=y_label,
               title_font=dict(size=10), linecolor=CHART_ZERO),
    hovermode="x unified",
)
st.plotly_chart(fig_main, use_container_width=True,
                config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# RETORNOS + VOLATILIDAD
# ─────────────────────────────────────────────────────────────────
ca, cb = st.columns(2, gap="medium")

with ca:
    section("Retorno del período", "green")
    df_ret = (pd.DataFrame({"Acción": list(rets.keys()),
                             "Retorno": list(rets.values())})
              .sort_values("Retorno", ascending=True))
    fig_ret = go.Figure(go.Bar(
        x=df_ret["Retorno"], y=df_ret["Acción"], orientation="h",
        marker=dict(
            color=["#10b981" if r >= 0 else "#f87171" for r in df_ret["Retorno"]],
            opacity=0.82,
            line=dict(width=0),
        ),
        text=[f"{v:+.1f}%" for v in df_ret["Retorno"]],
        textposition="outside", textfont=dict(size=10, color="#64748b"),
        hovertemplate="<b>%{y}</b>  %{x:.2f}%<extra></extra>",
    ))
    fig_ret.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=CHART_FONT, margin=dict(l=0, r=52, t=0, b=0),
        height=max(240, len(solo_acciones) * 34),
        xaxis=dict(gridcolor=CHART_GRID, zeroline=True,
                   zerolinecolor=CHART_ZERO, zerolinewidth=1.5),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_ret, use_container_width=True,
                    config={"displayModeBar": False})

with cb:
    section("Volatilidad anualizada", "purple")
    df_vol = (pd.DataFrame({"Acción": list(vols.keys()),
                             "Volatilidad": list(vols.values())})
              .sort_values("Volatilidad", ascending=True))
    fig_vol = go.Figure(go.Bar(
        x=df_vol["Volatilidad"], y=df_vol["Acción"], orientation="h",
        marker=dict(color="#818cf8", opacity=0.72, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in df_vol["Volatilidad"]],
        textposition="outside", textfont=dict(size=10, color="#64748b"),
        hovertemplate="<b>%{y}</b>  σ=%{x:.2f}%<extra></extra>",
    ))
    fig_vol.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=CHART_FONT, margin=dict(l=0, r=52, t=0, b=0),
        height=max(240, len(solo_acciones) * 34),
        xaxis=dict(gridcolor=CHART_GRID, zeroline=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_vol, use_container_width=True,
                    config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# DRAWDOWN
# ─────────────────────────────────────────────────────────────────
if mostrar_drawdown:
    section("Drawdown — caída desde máximo histórico del período",
            "orange", chip="% vs pico")
    fig_dd = go.Figure()
    for col in cols_ok:
        sec   = ACCIONES[col]["sector"]
        color = SECTOR_COLORS.get(sec, "#94a3b8")
        dd    = drawdown_series(df[col])
        fig_dd.add_trace(go.Scatter(
            x=dd.index, y=dd.values, name=col, mode="lines",
            line=dict(color=color, width=1.6),
            fill="tozeroy", fillcolor=color.replace(")", ",0.07)").replace("rgb", "rgba")
                                                                    if color.startswith("rgb")
                                                                    else color + "12",
            hovertemplate=f"<b>{col}</b><br>%{{x|%d %b %Y}}<br>DD: %{{y:.2f}}%<extra></extra>",
        ))
    fig_dd.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=CHART_FONT, height=260,
        margin=dict(l=0, r=0, t=36, b=0),
        legend=CHART_LEGEND,
        xaxis=dict(gridcolor=CHART_GRID, zeroline=False, linecolor=CHART_ZERO),
        yaxis=dict(gridcolor=CHART_GRID, zeroline=True,
                   zerolinecolor=CHART_ZERO, zerolinewidth=1.5,
                   title="Drawdown (%)", title_font=dict(size=10)),
        hovermode="x unified",
    )
    st.plotly_chart(fig_dd, use_container_width=True,
                    config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# SECTOR DISTRIBUTION
# ─────────────────────────────────────────────────────────────────
if mostrar_sector and len(cols_ok) >= 2:
    section("Distribución sectorial", "teal", chip=f"{len(cols_ok)} activos")
    cd, ce = st.columns([1, 1], gap="medium")

    with cd:
        sector_counts = {}
        for c in cols_ok:
            sec = ACCIONES[c]["sector"]
            sector_counts[sec] = sector_counts.get(sec, 0) + 1

        labels = list(sector_counts.keys())
        values = list(sector_counts.values())
        colors = [SECTOR_COLORS.get(l, "#94a3b8") for l in labels]

        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.52,
            marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent",
            textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>%{value} acciones · %{percent}<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=f"<b>{len(cols_ok)}</b><br><span style='font-size:10px'>activos</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#0f172a", family="Inter"),
            align="center",
        )
        fig_pie.update_layout(
            paper_bgcolor=CHART_BG,
            font=CHART_FONT, height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)",
                        orientation="v", x=1.02),
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True,
                        config={"displayModeBar": False})

    with ce:
        # Retorno promedio por sector
        sector_ret = {}
        sector_cnt = {}
        for c in solo_acciones:
            sec = ACCIONES[c]["sector"]
            sector_ret[sec] = sector_ret.get(sec, 0) + rets[c]
            sector_cnt[sec] = sector_cnt.get(sec, 0) + 1
        sector_avg = {k: sector_ret[k] / sector_cnt[k] for k in sector_ret}
        df_sec = (pd.DataFrame({"Sector": list(sector_avg.keys()),
                                 "Retorno": list(sector_avg.values())})
                  .sort_values("Retorno", ascending=True))

        fig_sec = go.Figure(go.Bar(
            x=df_sec["Retorno"], y=df_sec["Sector"], orientation="h",
            marker=dict(
                color=[SECTOR_COLORS.get(s, "#94a3b8") for s in df_sec["Sector"]],
                opacity=0.80, line=dict(width=0),
            ),
            text=[f"{v:+.1f}%" for v in df_sec["Retorno"]],
            textposition="outside", textfont=dict(size=10, color="#64748b"),
            hovertemplate="<b>%{y}</b>  %{x:.2f}%<extra></extra>",
        ))
        fig_sec.update_layout(
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=CHART_FONT, height=280,
            margin=dict(l=0, r=52, t=10, b=0),
            title=dict(text="Retorno por sector", font=dict(size=11, color="#64748b"),
                       x=0, pad=dict(b=4)),
            xaxis=dict(gridcolor=CHART_GRID, zeroline=True,
                       zerolinecolor=CHART_ZERO, zerolinewidth=1.5),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_sec, use_container_width=True,
                        config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# CORRELACIÓN
# ─────────────────────────────────────────────────────────────────
if mostrar_corr and len(cols_ok) >= 2:
    section("Correlación de retornos diarios", "purple",
            chip="ρ de Pearson")
    corr   = df[cols_ok].pct_change().dropna().corr()
    zvals  = np.round(corr.values, 2)
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
        colorbar=dict(tickfont=dict(color="#94a3b8", size=9),
                      outlinecolor="#e2e8f0", outlinewidth=1, thickness=10),
    ))
    fig_corr.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=CHART_FONT, margin=dict(l=0, r=0, t=0, b=0),
        height=max(260, len(cols_ok) * 46),
    )
    st.plotly_chart(fig_corr, use_container_width=True,
                    config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
# TABLA RESUMEN
# ─────────────────────────────────────────────────────────────────
section("Resumen estadístico", "blue", chip=f"{len(cols_ok)} activos")

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
        "Retorno %":         retorno(s),
        "Vol. anual %":      volatilidad(s),
        "Sharpe":            sharpe_ratio(s),
        "Max DD %":          max_drawdown(s),
        "Ret. diario %":     rd.mean() * 100,
        "Máx. período":      f"${s.max():,.1f}",
        "Mín. período":      f"${s.min():,.1f}",
        "Sesiones":          len(s),
    })

df_table = pd.DataFrame(rows)

def _color_num(val):
    if isinstance(val, float):
        if val > 0:
            return "color: #059669; font-weight:600"
        elif val < 0:
            return "color: #dc2626; font-weight:600"
    return ""

styled = (
    df_table.style
    .applymap(_color_num, subset=["Retorno %", "Ret. diario %", "Max DD %", "Sharpe"])
    .format({
        "Retorno %":    "{:+.2f}%",
        "Vol. anual %": "{:.1f}%",
        "Sharpe":       "{:.2f}",
        "Max DD %":     "{:.1f}%",
        "Ret. diario %":"{:+.3f}%",
    })
)

st.dataframe(styled, hide_index=True, use_container_width=True,
             height=min(400, 44 + len(rows) * 36))


# ─────────────────────────────────────────────────────────────────
# DESCARGA
# ─────────────────────────────────────────────────────────────────
section("Exportar datos", "teal")
dl1, dl2, _ = st.columns([1, 1, 2], gap="small")

with dl1:
    csv_p = df.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Precios (CSV)", data=csv_p,
                       file_name=f"colcap_precios_{fecha_inicio}_{fecha_fin}.csv",
                       mime="text/csv", use_container_width=True)
with dl2:
    csv_r = df_table.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Resumen (CSV)", data=csv_r,
                       file_name=f"colcap_resumen_{fecha_inicio}_{fecha_fin}.csv",
                       mime="text/csv", use_container_width=True)
