"""Shared visual layer: CSS on top of .streamlit/config.toml (TVN-inspired palette) and a section kicker.

Only st.html is used, so no widget is added and the element order the UI tests rely on is unchanged.
"""
import streamlit as st

KICKER = "SCAYL · Sala de Inteligencia Editorial"

_CSS = """
<style>
[data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background: #FFFFFF; border-top: 4px solid #005588; }
.block-container { padding-top: 4.5rem; max-width: 1360px; }

.scayl-kicker { display: flex; align-items: center; gap: .6rem; margin: 0 0 -.4rem 0;
  font-size: .78rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #0077C8; }
.scayl-kicker::before { content: ""; width: 28px; height: 4px; border-radius: 2px; background: #FEC526; }

h1 { font-weight: 800 !important; letter-spacing: -.02em; color: #0B1220; }
h2, h3 { font-weight: 700 !important; color: #0B1220; }
h2 { font-size: 1.65rem !important; }
h3 { border-bottom: 2px solid #EAF1F7; padding-bottom: .35rem; }

[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #DCE1E7; border-left: 5px solid #005588;
  border-radius: 10px; padding: .85rem 1.1rem; box-shadow: 0 1px 2px rgba(11, 18, 32, .05); }
[data-testid="stMetricValue"] { color: #005588; font-weight: 700; }
[data-testid="stMetricLabel"] p { font-weight: 600; font-size: .85rem; color: #5A6673; }

/* Bordered containers inside columns: the morning agenda cards. */
[data-testid="stColumn"] [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
  background: #FFFFFF; border-top: 4px solid #005588; box-shadow: 0 2px 6px rgba(11, 18, 32, .08); }
[data-testid="stColumn"] [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] [data-testid="stText"] {
  font-size: .93rem; line-height: 1.45; }
[data-testid="stColumn"] [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]
  > [data-testid="stElementContainer"]:first-child [data-testid="stText"] {
  font-weight: 700; font-size: 1.08rem; line-height: 1.35; color: #0B1220; }
[data-testid="stExpander"] details { background: #FFFFFF; border-radius: 10px; }
[data-testid="stExpander"] summary:hover { color: #005588; }

.stMain [data-testid="stPageLink"] a { font-weight: 600; border: 1px solid #DCE1E7; border-radius: 999px;
  padding: .2rem .9rem; background: #FFFFFF; }
.stMain [data-testid="stPageLink"] a:hover { border-color: #005588; background: #EAF1F7; }
[data-testid="stAlert"] { border-radius: 10px; }
[data-baseweb="tab"] p { font-weight: 600; font-size: .95rem; }

[data-testid="stSidebarHeader"]::after {
  content: "SCAYL"; display: block; padding: 0 1rem .5rem 1rem; font-weight: 800; font-size: 1.35rem;
  letter-spacing: .06em; color: #FFFFFF; }
[data-testid="stSidebarNavLink"] span { font-weight: 600; }
</style>
"""


_LOGIN_CSS = """
<style>
.block-container { max-width: 520px; padding-top: 7rem; }
[data-testid="stForm"] { background: #FFFFFF; border-top: 4px solid #005588; box-shadow: 0 2px 10px rgba(11, 18, 32, .08); }
</style>
"""


def apply_theme(kicker: str = KICKER, login: bool = False) -> None:
    """Inject the shared CSS and the section kicker shown above each page title."""
    st.html(_CSS + (_LOGIN_CSS if login else ""))
    st.html(f'<div class="scayl-kicker">{kicker}</div>')
