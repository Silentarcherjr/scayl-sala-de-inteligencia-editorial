"""Copied to app/space.py in the prepared Space; gate every page before running it.

Self-configuring for hosts that ignore the Dockerfile (Streamlit Community Cloud, DL-032): puts the stage
root on ``sys.path`` and defaults the hosted settings (cache only, stage-relative data). Values already in
the environment (Docker ENV, host secrets) win. The password is never defaulted.

Public access (jury evaluates unattended, DL-033) is an explicit opt-in: ``SCAYL_PUBLIC_ACCESS = "1"`` in the
host secrets skips the password. Without it the gate keeps failing closed when the password is missing.
"""
import hashlib
import hmac
import os
import sys
from pathlib import Path

import streamlit as st

STAGE = Path(__file__).resolve().parents[1]
if str(STAGE) not in sys.path:
    sys.path.insert(0, str(STAGE))
for _key, _value in {"SCAYL_HOSTED": "1", "SCAYL_LLM_MODE": "cache", "SCAYL_SNAPSHOT_DIR": "data/processed/v1",
                     "SCAYL_LLM_CACHE": str(STAGE / "data" / "cache" / "llm"),
                     "SCAYL_STATE_DIR": str(STAGE / "data" / "state")}.items():
    os.environ.setdefault(_key, _value)


def public_access() -> bool:
    return os.environ.get("SCAYL_PUBLIC_ACCESS", "") == "1"


def require_password() -> None:
    if public_access():
        return
    secret = os.environ.get("SCAYL_SPACE_PASSWORD", "")
    if not secret:
        st.error("Acceso deshabilitado: falta configurar la contraseña del Space.")
        st.stop()
    fingerprint = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    if st.session_state.get("_space_authenticated") == fingerprint:
        return
    def attempt_login() -> None:
        entered = st.session_state.pop("_space_password", "")
        valid = hmac.compare_digest(entered.encode("utf-8"), secret.encode("utf-8"))
        st.session_state["_space_login_failed"] = not valid
        if valid:
            st.session_state["_space_authenticated"] = fingerprint

    from app.components.theme import apply_theme

    apply_theme("Demo para el jurado · reto TVN Media", login=True)
    st.title("SCAYL · Acceso al jurado")
    st.caption("Demo snapshot · Acceso con contraseña")
    with st.form("space-login"):
        st.text_input("Contraseña", type="password", key="_space_password")
        st.form_submit_button("Entrar", on_click=attempt_login, type="primary")
    if st.session_state.get("_space_login_failed"):
        st.error("Contraseña incorrecta.")
    st.stop()


def hosted_frame() -> None:
    require_password()
    from deploy.runtime import enforce_cache

    enforce_cache()
    st.caption("Demo snapshot · salidas IA precalculadas · Modo cache; sin salida guardada se usa template.")
    st.caption("Las decisiones de esta demo son temporales y se pierden al reiniciar el Space.")
    if not public_access() and st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="SCAYL · Demo snapshot", layout="wide")
    # Each selected page runs hosted_frame before importing/rendering the original page.
    page = st.navigation([
        st.Page("Home.py", title="Sala de Situación", default=True),
        st.Page("pages/1_Ficha_de_Caso.py", title="Ficha de Caso"),
        st.Page("pages/2_Consultas.py", title="Consultas"),
        st.Page("pages/3_Trust_Lab.py", title="Trust Lab"),
        st.Page("pages/4_Simulador_de_pesos.py", title="Simulador de pesos"),
    ], position="sidebar" if public_access() or st.session_state.get("_space_authenticated") else "hidden")
    page.run()


if __name__ == "__main__":
    main()
