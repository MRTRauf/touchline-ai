"""Original football-game-inspired visual chrome for the public Touchline demo.

Presentation only. This module does not access or change research data.
"""
from html import escape
from math import isfinite
from textwrap import wrap

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


_STYLES = r"""
<style>
:root {
  --tl-bg: #080d13;
  --tl-panel: #121c24;
  --tl-ink: #f3f8f6;
  --tl-muted: #9fb0b5;
  --tl-acid: #c8f743;
  --tl-teal: #35eac4;
  --tl-edge: rgba(199,247,76,.18);
}
.tl-hero, .tl-hero *, .tl-kpis, .tl-kpis *, .tl-player-card, .tl-player-card *,
.tl-kicker, .tl-sidebar-brand, .tl-sidebar-brand * {box-sizing:border-box}
.tl-hero {
  position:relative; overflow:hidden; margin:.35rem 0 1.4rem;
  border:1px solid rgba(200,247,67,.25); border-radius:22px;
  background:
    radial-gradient(circle at 82% 23%,rgba(53,234,196,.14),transparent 38%),
    linear-gradient(120deg,#111b23 0%,#0a1319 55%,#12231b 100%);
  box-shadow:0 18px 60px rgba(0,0,0,.27);
}
.tl-hero::before {content:"";position:absolute;inset:0;opacity:.19;pointer-events:none;
  background:repeating-linear-gradient(140deg,transparent 0 41px,rgba(255,255,255,.08) 42px,transparent 43px)}
.tl-hero-inner {position:relative;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(240px,.75fr);
  align-items:center;gap:clamp(1rem,3vw,3rem);padding:clamp(1.5rem,4vw,3.2rem)}
.tl-eyebrow {font:800 .73rem/1.4 system-ui,sans-serif;letter-spacing:.18em;color:var(--tl-acid);text-transform:uppercase}
.tl-hero h1 {margin:.85rem 0 1rem;color:var(--tl-ink)!important;
  font:900 clamp(2.5rem,5vw,5.3rem)/.99 Impact,"Arial Narrow",system-ui,sans-serif!important;
  letter-spacing:-.045em;text-transform:uppercase;text-wrap:balance}
.tl-hero h1 em {font-style:normal;color:var(--tl-acid)}
.tl-hero p {max-width:610px;color:#c4d1d0;font-size:clamp(.94rem,1.2vw,1.07rem);line-height:1.66;margin:0 0 1.4rem}
.tl-hero-tags {display:flex;flex-wrap:wrap;gap:.45rem}
.tl-hero-tags span {border:1px solid rgba(203,232,214,.23);border-radius:100px;padding:.35rem .72rem;
  color:#e3eeea;font:700 .64rem/1.25 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;
  background:rgba(5,18,24,.38)}
.tl-hero-visual {position:relative;min-height:220px;border:1px solid rgba(201,247,67,.22);
  border-radius:16px;display:grid;place-items:center;background:
  radial-gradient(ellipse at 50% 50%,rgba(200,247,67,.09),transparent 62%),
  linear-gradient(160deg,rgba(15,42,39,.85),rgba(8,18,23,.95));overflow:hidden}
.tl-pitch {position:relative;width:84%;height:150px;border:1px solid #7cce9f;opacity:.85}
.tl-half {position:absolute;left:50%;height:100%;border-left:1px solid #7cce9f}
.tl-centre {position:absolute;left:calc(50% - 28px);top:calc(50% - 28px);width:56px;height:56px;border:1px solid #7cce9f;border-radius:50%}
.tl-area {position:absolute;top:24%;height:52%;width:18%;border:1px solid #7cce9f}
.tl-area-left {left:0;border-left:0}.tl-area-right {right:0;border-right:0}
.tl-node {position:absolute;width:9px;height:9px;border-radius:50%;background:var(--tl-acid);box-shadow:0 0 0 7px rgba(200,247,67,.1)}
.tl-node-one {left:28%;top:25%}.tl-node-two {left:62%;top:40%}.tl-node-three {left:72%;top:72%}
.tl-pitch-caption {position:absolute;top:13px;left:14px;color:var(--tl-acid);
  font:700 .72rem/1.5 system-ui,sans-serif;letter-spacing:.16em}
.tl-pitch-footer {position:absolute;bottom:12px;right:14px;color:#8dafa4;
  font:700 .6rem/1.4 system-ui,sans-serif;letter-spacing:.12em}
.tl-kpis {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;margin:0 0 1.35rem}
.tl-kpi {min-width:0;padding:1rem 1.05rem;border:1px solid rgba(159,176,181,.18);border-radius:15px;
  background:linear-gradient(145deg,rgba(23,36,42,.98),rgba(13,26,30,.98))}
.tl-kpi b {display:block;font:900 clamp(1.45rem,2.7vw,2.15rem)/1.2 "Arial Narrow",system-ui,sans-serif;
  letter-spacing:-.045em;color:#eaf7e9}
.tl-kpi:first-child b {color:var(--tl-acid)}
.tl-kpi span {display:block;margin-top:.22rem;font:700 .66rem/1.4 system-ui,sans-serif;
  letter-spacing:.10em;text-transform:uppercase;color:#a6bbb8}
.tl-kicker {margin:.9rem 0 .55rem;padding-left:.85rem;border-left:3px solid var(--tl-acid);
  font:800 .72rem/1.45 system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--tl-acid)}
.tl-player-card {position:relative;overflow:hidden;margin:.9rem 0 1.25rem;border:1px solid var(--tl-edge);
  border-radius:18px;padding:clamp(1.15rem,2.5vw,1.9rem);
  background:radial-gradient(circle at 97% 5%,rgba(200,247,67,.14),transparent 40%),
  linear-gradient(112deg,#172821,#101c22 70%)}
.tl-player-card::after {content:"";position:absolute;right:-45px;bottom:-95px;width:270px;height:270px;
  border:1px solid rgba(200,247,67,.15);border-radius:50%;pointer-events:none}
.tl-card-inner {position:relative;z-index:1;display:flex;justify-content:space-between;
  align-items:center;gap:1rem;flex-wrap:wrap}
.tl-card-label {color:var(--tl-acid);font:800 .68rem/1.2 system-ui,sans-serif;letter-spacing:.17em;text-transform:uppercase}
.tl-card-name {font:900 clamp(1.55rem,3.5vw,2.75rem)/1.07 Impact,"Arial Narrow",system-ui,sans-serif;
  letter-spacing:-.025em;color:#f5fff6;margin:.55rem 0;text-transform:uppercase;overflow-wrap:anywhere}
.tl-card-meta {font:600 .82rem/1.6 system-ui,sans-serif;color:#c4d9d2}
.tl-card-score {flex:0 0 auto;min-width:110px;text-align:center;padding:.65rem 1.1rem;
  border:1px solid rgba(200,247,67,.46);border-radius:12px;background:rgba(2,19,18,.56)}
.tl-card-score b {display:block;color:var(--tl-acid);font:900 2.7rem/1 Impact,"Arial Narrow",system-ui,sans-serif}
.tl-card-score span {display:block;margin-top:.3rem;font:700 .72rem/1.5 system-ui,sans-serif;
  color:#d3e6d9;letter-spacing:.12em;text-transform:uppercase}
.tl-sidebar-brand {border-bottom:1px solid rgba(199,247,76,.24);padding:.15rem .1rem 1.1rem;margin-bottom:1.1rem}
.tl-sidebar-name {font:900 1.6rem/1 Impact,"Arial Narrow",system-ui,sans-serif;color:#f4fff6;
  letter-spacing:-.025em}
.tl-sidebar-name span {color:var(--tl-acid)}
.tl-sidebar-sub {font:700 .72rem/1.45 system-ui,sans-serif;color:#9caead;letter-spacing:.15em;
  margin-top:.55rem;text-transform:uppercase}
div[data-testid="stMetric"] {padding:1rem 1.15rem;border:1px solid rgba(200,247,67,.15);
  border-radius:14px;background:linear-gradient(160deg,#17252b,#111c23)}
div[data-testid="stMetricValue"] {color:#c8f743}
[data-testid="stMetricLabel"] p {white-space:normal!important;overflow:visible!important;text-overflow:clip!important}
div[data-testid="stDataFrame"] {border-radius:12px;overflow:hidden}
.stButton > button[kind="primary"], .stDownloadButton > button {
  border-radius:10px!important;font-weight:800!important;letter-spacing:.015em}
div[data-testid="stSidebar"] {border-right:1px solid rgba(200,247,67,.14)}
@media(max-width:920px) {.tl-hero-inner {grid-template-columns:minmax(0,1fr)}
  .tl-hero-visual {min-height:150px}.tl-pitch {max-width:280px;height:100px}}
@media(max-width:670px) {.tl-hero-inner {padding:1.4rem}.tl-hero-visual {display:none}
  .tl-kpis {grid-template-columns:repeat(2,minmax(0,1fr))}
  .tl-card-score {min-width:88px}.tl-card-score b {font-size:2.2rem}
  .tl-hero h1 {font-size:clamp(2.3rem,10vw,3.7rem)}}
@media(prefers-reduced-motion:no-preference) {
  .tl-hero {animation:tl-reveal .5s ease-out both}
  @keyframes tl-reveal {from{opacity:.35;transform:translateY(8px)}to{opacity:1;transform:none}}
}
/* Foreground/background pairs: dark surfaces use light ink; lime/teal use dark ink. */
:root {--tl-on-accent:#080d13;--tl-info-bg:#142c3f;--tl-info-ink:#e8f4ff;--tl-warning-bg:#382e10;--tl-warning-ink:#fff0b3}
[data-tag] {background:var(--tl-acid)!important;color:var(--tl-on-accent)!important}
[data-tag] *, [role="option"][aria-selected="true"] * {color:inherit!important}
[role="option"][aria-selected="true"] {background:var(--tl-acid)!important;color:var(--tl-on-accent)!important}
.stButton button {background:var(--tl-panel);color:var(--tl-ink)}
.stButton button[kind="primary"], .stDownloadButton button {background:var(--tl-acid)!important;color:var(--tl-on-accent)!important;border-color:var(--tl-acid)!important}
.stButton button[kind="primary"] *, .stDownloadButton button * {color:inherit!important}
.stDownloadButton button:hover {background:var(--tl-teal)!important;color:var(--tl-on-accent)!important}
button:focus-visible, input:focus-visible, textarea:focus-visible {outline:3px solid var(--tl-teal)!important;outline-offset:3px}
input, textarea {color:var(--tl-ink)!important;caret-color:var(--tl-acid)}
button:disabled, input:disabled, textarea:disabled {color:var(--tl-muted)!important;background:var(--tl-panel)!important;opacity:1}
[data-testid="stAlertContainer"] {color:var(--tl-ink)}
</style>
"""

_PAGES = {
    "Scout Board": ("RANK THE", "RECORDED EVIDENCE", "Discover role-specific recorded performance. Turn a transparent ranking into a question for human review."),
    "Player Intelligence": ("READ THE", "PLAYER PROFILE", "Inspect exposure, role-relative statistics and source limitations before your next video review."),
    "Compare Players": ("COMPARE THE", "STATISTICS", "Read two or three player records side by side. Higher event output does not establish superior ability."),
    "Similar Profiles": ("FIND SIMILAR", "PROFILES", "Discover players with a similar statistical shape, then challenge the comparison with football context."),
    "Forecast Lab": ("READ THE", "FORECAST", "Explore previously saved next-season attacking output estimates and their limitations."),
    "My Shortlist": ("BUILD YOUR", "REVIEW QUEUE", "Keep temporary scouting questions and analyst-defined priorities for this session. No automated recruitment decisions."),
    "Methodology & Limitations": ("KNOW THE", "LIMITS", "See what this research supports, what it cannot establish, and how to use it responsibly."),
    "Player Stories": ("BEHIND THE", "NUMBERS", "Two grounded player stories show how descriptive data can guide sharper scouting questions."),
    "Explore players": ("FIND YOUR", "NEXT QUESTION", "Filter genuine season evidence, scout role strengths, and build a better video-review shortlist."),
    "Compare statistical profiles": ("COMPARE THE", "PLAYER DNA", "Discover players with a similar statistical shape, then challenge the comparison with football context."),
    "Understand next-season estimates": ("READ THE", "FORECAST", "Explore previously saved next-season attacking output estimates and their limitations."),
    "Two player stories": ("BEHIND THE", "NUMBERS", "Two grounded player stories show how descriptive data can guide sharper scouting questions."),
    "How to read the evidence": ("KNOW THE", "LIMITS", "See what this research supports, what it cannot establish, and how to use it responsibly."),
}


def install_theme():
    """Layer original branded components over Streamlit's configured dark theme."""
    st.html(_STYLES)


def sidebar_brand():
    st.sidebar.html(
        '<div class="tl-sidebar-brand"><div class="tl-sidebar-name">TOUCH<span>LINE</span> / AI</div>'
        '<div class="tl-sidebar-sub">Independent football intelligence</div></div>'
    )


def hero(page, record_count, league_count, candidate_count, observed_count):
    lead, accent, subtitle = _PAGES.get(page, _PAGES["Explore players"])
    pitch = """
    <div class="tl-pitch" role="img" aria-label="Abstract football-pitch tactics diagram">
      <div class="tl-half"></div><div class="tl-centre"></div>
      <div class="tl-area tl-area-left"></div><div class="tl-area tl-area-right"></div>
      <span class="tl-node tl-node-one"></span><span class="tl-node tl-node-two"></span>
      <span class="tl-node tl-node-three"></span>
    </div>
    """
    st.html(
        '<section class="tl-hero"><div class="tl-hero-inner">'
        '<div><div class="tl-eyebrow">TOUCHLINE // PERFORMANCE INTELLIGENCE</div>'
        f'<h1>{escape(lead)}<br><em>{escape(accent)}</em></h1>'
        f'<p>{escape(subtitle)}</p>'
        '<div class="tl-hero-tags"><span>Independent research</span>'
        '<span>2024/25 profiles</span><span>Retrospective estimates</span></div></div>'
        '<div class="tl-hero-visual"><span class="tl-pitch-caption">TACTICAL SCAN / 01</span>'
        f'{pitch}<span class="tl-pitch-footer">DATA → VIDEO → CONTEXT</span></div>'
        '</div></section>'
        '<div class="tl-kpis">'
        f'<div class="tl-kpi"><b>{int(record_count):,}</b><span>Season profiles</span></div>'
        f'<div class="tl-kpi"><b>{int(league_count)}</b><span>European leagues</span></div>'
        f'<div class="tl-kpi"><b>{int(candidate_count):,}</b><span>Forecast candidates</span></div>'
        f'<div class="tl-kpi"><b>{int(observed_count):,}</b><span>Observed outcomes</span></div>'
        '</div>'
    )


def kicker(text):
    st.html(f'<div class="tl-kicker">{escape(str(text))}</div>')


def player_card(row):
    player = escape(str(row.get("player", "Unknown player")))
    club = escape(str(row.get("team", "")))
    role = escape(str(row.get("role", "Unknown role")))
    league = escape(str(row.get("comp", "")).upper())
    try:
        screening = float(row.get("screening_score", float("nan")))
        score = f"{screening:.1f}" if isfinite(screening) else "—"
    except (TypeError, ValueError):
        score = "—"
    st.html(
        '<article class="tl-player-card"><div class="tl-card-inner"><div>'
        '<div class="tl-card-label">PLAYER INTELLIGENCE / SEASON PROFILE</div>'
        f'<div class="tl-card-name">{player}</div>'
        f'<div class="tl-card-meta">{club} &nbsp;·&nbsp; {role} &nbsp;·&nbsp; {league} &nbsp;·&nbsp; 2024/25</div>'
        '</div><div class="tl-card-score">'
        f'<b>{score}</b><span>Descriptive screen / 100</span>'
        '</div></div></article>'
    )


def role_radar(profile):
    """Show only saved descriptive percentiles, never simulated player ratings."""
    if not {"metric", "percentile"}.issubset(profile.columns):
        return
    values = profile[["metric", "percentile"]].copy()
    values["percentile"] = pd.to_numeric(values["percentile"], errors="coerce")
    values = values.dropna().head(8)
    if len(values) < 3:
        return
    labels = ["<br>".join(escape(line) for line in wrap(label, width=16))
              for label in values["metric"].astype(str)]
    nums = values["percentile"].clip(0, 100).astype(float).tolist()
    fig = go.Figure(go.Scatterpolar(
        r=nums + nums[:1], theta=labels + labels[:1], fill="toself",
        fillcolor="rgba(200,247,67,.15)",
        line=dict(color="#c8f743", width=2.5),
        marker=dict(size=6, color="#35eac4"),
        hovertemplate="%{theta}: %{r:.0f}th percentile<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9dad4", size=11),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100],
                            gridcolor="rgba(172,204,180,.14)", tickfont=dict(size=9, color="#849b96")),
            angularaxis=dict(gridcolor="rgba(172,204,180,.12)", linecolor="rgba(172,204,180,.22)")
        ),
        margin=dict(l=94, r=94, t=40, b=40), showlegend=False,
        height=390
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
