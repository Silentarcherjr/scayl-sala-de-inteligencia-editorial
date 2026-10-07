"""A-01/A-02: snapshot navigation and editorial situation room."""
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from app.components.agenda import agenda
from scayl import service
from scayl.contracts import Event, EvidenceStatus, PriorityTier


def panama(value: datetime | None) -> str:
    return (value.astimezone(ZoneInfo("America/Panama")).strftime("%Y-%m-%d %H:%M")
            if value is not None else "no disponible")


def ranked_events(events: list[Event]) -> list[Event]:
    return sorted(events, key=lambda e: (-e.priority.score, -e.priority.components.U, e.event_id))


def main() -> None:
    st.set_page_config(page_title="Sala de Situación · SCAYL", layout="wide")
    st.title("Sala de Situación")
    st.caption("De la señal a la decisión editorial · Priorizar atención, investigar evidencia")
    bundle = service.load_bundle()
    events = ranked_events(bundle.events)
    st.caption(f"Snapshot: {bundle.snapshot_version} · Corte: {panama(bundle.snapshot_cutoff_utc)} Panamá")
    if events and all(event.synthetic for event in events):
        st.warning("SINTÉTICO · Casos de demostración")
    with st.container(horizontal=True):
        st.page_link("pages/2_Consultas.py", label="Consultas")
        st.page_link("pages/3_Trust_Lab.py", label="Trust Lab")
        st.page_link("pages/4_Simulador_de_pesos.py", label="Simulador de pesos")
    for col, label, value in zip(st.columns(4), ("Señales recibidas", "Señales válidas", "Eventos", "Top 5"),
                                  (bundle.signals_total, bundle.signals_valid, len(events), min(5, len(events)))):
        col.metric(label, value)
    st.info("P mide atención, no probabilidad de verdad ni impacto. El estado de evidencia es independiente.")
    st.caption("Prioridad alta NO habilita publicación. Aprobado como borrador NO significa publicado.")
    agenda(bundle, service.official_weights())
    left, right = st.columns(2)
    topic = left.selectbox("Tema", ["Todos"] + sorted({e.topic.value for e in events}))
    status = right.selectbox("Estado de evidencia", ["Todos"] + [s.value for s in EvidenceStatus])
    filtered = [e for e in events if (topic == "Todos" or e.topic.value == topic)
                and (status == "Todos" or e.evidence_status.value == status)]
    st.caption(f"{len(filtered)} eventos visibles de {len(events)} · Orden: P descendente, U descendente, ID ascendente")
    if not filtered:
        st.info("No hay eventos que coincidan con los filtros.")
    else:
        st.dataframe(pd.DataFrame([{
            "Caso": e.event_id, "Titular": e.title, "P": e.priority.score,
            "Rango": e.priority.tier.value, "Evidencia": e.evidence_status.value,
            "Tema": e.topic.value, "Publicación (Panamá)": panama(e.last_published),
            "Detección (Panamá)": panama(e.first_detected),
            "Publicaciones": e.source_dna.publications,
            "Máx. independientes": e.source_dna.max_possible_independent,
            "Independientes confirmadas": e.source_dna.confirmed_independent,
            "Conflicto": "⚠ Sí" if e.conflicts else "No registrado",
            "Acción": e.recommended_action,
        } for e in filtered]), hide_index=True, width="stretch", key="event-table")
    st.subheader("Prioridad × Evidencia")
    st.caption("Conteos de los eventos visibles tras aplicar los filtros.")
    matrix = [{"Rango": tier.value, **{
        state.value: sum(e.priority.tier == tier and e.evidence_status == state for e in filtered)
        for state in EvidenceStatus}} for tier in (PriorityTier.ALTO, PriorityTier.MEDIO, PriorityTier.BAJO)]
    st.dataframe(pd.DataFrame(matrix), hide_index=True, width="stretch", key="evidence-matrix")
    st.subheader("Casos y componentes de atención")
    weights = service.official_weights()
    for event in filtered:
        with st.expander(f"{event.event_id} · P {event.priority.score:g} · {event.title}"):
            st.badge(f"Atención: {event.priority.tier.value}", color="orange")
            st.badge(f"Evidencia: {event.evidence_status.value}", color="blue")
            if event.synthetic:
                st.badge("SINTÉTICO", color="gray")
            st.text(event.evidence_status_reason)
            st.text(event.recommended_action)
            st.text(event.source_dna.statement)
            st.caption(f"Publicaciones: {event.source_dna.publications} · Máximo posible de independientes: "
                       f"{event.source_dna.max_possible_independent} · Confirmadas: {event.source_dna.confirmed_independent}")
            st.caption(f"Reglas: {event.priority.rules_version} · Contribuciones en puntos de P")
            for col, key in zip(st.columns(5), ("R", "I", "U", "N", "E")):
                component = getattr(event.priority.components, key)
                contribution = weights[key] * component
                col.progress(component, text=f"{key}: {contribution:g}/{weights[key]}")
                col.caption(event.priority.components.rationale.get(key, "Justificación no disponible"),
                            help=f"{key}={component:g} × peso {weights[key]} = {contribution:g} puntos")
            if event.is_recirculated:
                st.warning("Noticia recirculada: se conserva la fecha original de publicación.")
            if event.conflicts:
                st.warning("⚠ Conflicto: ver ambas versiones y la verificación pendiente en la ficha.")
            st.page_link("pages/1_Ficha_de_Caso.py", label=f"Abrir ficha {event.event_id}",
                         query_params={"event_id": event.event_id})


main()
