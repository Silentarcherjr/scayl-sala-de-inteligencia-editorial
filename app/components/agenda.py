"""A-07: morning agenda, using deterministic score contributions."""
from zoneinfo import ZoneInfo

import streamlit as st

from scayl.contracts import Event, UIBundle


def top_reasons(event: Event, weights: dict[str, int]) -> list[tuple[str, str]]:
    keys = sorted(("R", "I", "U", "N", "E"),
                  key=lambda key: -weights[key] * getattr(event.priority.components, key))[:2]
    return [(key, event.priority.components.rationale.get(key, "Justificación no disponible")) for key in keys]


def agenda(bundle: UIBundle, weights: dict[str, int]) -> None:
    st.subheader("Agenda de la mañana")
    cutoff = bundle.snapshot_cutoff_utc.astimezone(ZoneInfo("America/Panama"))
    st.caption(f"Top 5 del snapshot · Corte {cutoff:%Y-%m-%d %H:%M} Panamá · No cambia con los filtros de abajo")
    events = sorted(bundle.events, key=lambda e: (-e.priority.score, -e.priority.components.U, e.event_id))[:5]
    if not events:
        st.info("No hay eventos disponibles para la agenda.")
        return
    st.caption("Las fuentes sugeridas son contactos para verificar, no evidencia ni confirmación.")
    for start in range(0, len(events), 2):
        for col, event in zip(st.columns(2), events[start:start + 2]):
            with col.container(border=True):
                st.text(event.title)
                st.badge(f"P {event.priority.score:g} · {event.priority.tier.value}", color="orange")
                st.badge(f"Evidencia: {event.evidence_status.value}", color="blue")
                if event.synthetic:
                    st.badge("SINTÉTICO", color="gray")
                st.caption("Por qué merece atención")
                for key, reason in top_reasons(event, weights):
                    st.text(f"{key}: {reason}")
                st.caption("Acción y fuente sugerida para verificar")
                st.text(event.recommended_action)
                st.page_link("pages/1_Ficha_de_Caso.py", label=f"Investigar {event.event_id}",
                             query_params={"event_id": event.event_id})
