"""A-08: shared citation card; values and periods come from the evidence contract."""
from urllib.parse import urlsplit

import streamlit as st

from scayl.contracts import EvidenceRef


def evidence_card(ref: EvidenceRef) -> None:
    """Click the cited value to inspect its source without converting nulls to zero."""
    value = "no disponible (nulo)" if ref.value is None else str(ref.value)
    with st.expander(f"{value} · {ref.evidence_id} · {ref.field}"):
        st.text(f"ID de evidencia: {ref.evidence_id}")
        st.text(f"Tipo: {ref.kind.value}")
        st.text(f"Campo: {ref.field}")
        st.text(f"Valor: {value}")
        st.text(f"Período: {ref.period if ref.period is not None else 'no disponible'}")
        if ref.evidence_id.startswith("wb:") and ref.period:
            st.warning(f"Dato histórico — {ref.period}. No presentarlo como medición actual.")
        elif ref.period:
            st.caption("La evidencia corresponde al período indicado; no implica condiciones actuales.")
        if ref.url:
            if urlsplit(ref.url).scheme.lower() in {"http", "https"}:
                st.link_button("Abrir fuente", ref.url)
            st.text(f"URL: {ref.url}")
        else:
            st.text("URL: no disponible")
        st.text(f"Extracto: {ref.excerpt if ref.excerpt is not None else 'no disponible'}")
