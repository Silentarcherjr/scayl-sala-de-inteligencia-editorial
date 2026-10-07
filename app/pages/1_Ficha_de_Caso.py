"""A-03: case detail. Shared evidence-card integration awaits A-08 (AP-011)."""
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from scayl import service
from scayl.contracts import REVIEW_TRANSITIONS, Claim, Event, EvidenceRef, StoryPackage

PANAMA = ZoneInfo("America/Panama")


def local_time(value: datetime | None) -> str:
    return "no disponible" if value is None else value.astimezone(PANAMA).strftime("%Y-%m-%d %H:%M Panamá")


def show_refs(refs: list[EvidenceRef]) -> None:
    # Temporary local adapter: preserve the full contract without implementing A-08.
    for ref in refs:
        with st.expander(f"{ref.evidence_id} · {ref.field}"):
            st.json(ref.model_dump(mode="json"))


def show_claim(claim: Claim) -> None:
    st.caption(f"{claim.claim_id} · [{claim.type.value}] · {claim.status.value}")
    st.text(claim.statement)
    if claim.attributed_to:
        st.text(f"Según: {claim.attributed_to}")
    st.text(claim.reason)
    if claim.temporal_note:
        st.warning(claim.temporal_note)
    show_refs(claim.evidence)


def show_package(package: StoryPackage, event: Event) -> None:
    st.subheader(package.proposed_title)
    st.text(package.public_interest_angle)
    meta = package.generated_by
    st.caption(f"Modo: {meta.mode} · Modelo: {meta.model or 'no aplica'} · {local_time(meta.created_at)}")
    st.caption(f"Prompt: {meta.prompt_version or 'no aplica'}")
    st.caption(f"Latencia: {str(meta.latency_ms) + ' ms' if meta.latency_ms is not None else 'no medido'}")
    st.caption(f"Tokens entrada: {meta.tokens_in if meta.tokens_in is not None else 'no medido'} · "
               f"salida: {meta.tokens_out if meta.tokens_out is not None else 'no medido'}")
    if package.scope_disclaimer:
        st.info(package.scope_disclaimer)
    if package.validation.passed:
        st.success("Validación del paquete: aprobada. No autoriza publicación.")
    else:
        st.error("Validación del paquete: no aprobada.")
    for issue in package.validation.issues:
        st.warning(f"{issue.code} · {issue.severity} · {issue.detail}")
    claims = {claim.claim_id: claim for claim in event.claims}
    for title, sentences in (("Brief", package.brief), ("Guion", package.script),
                             ("Copy", [package.social_copy])):
        st.subheader(title)
        for sentence in sentences:
            st.caption(f"[{sentence.tag.value}]")
            st.text(sentence.text)
            for claim_id in sentence.claim_ids:
                with st.expander(f"Afirmación {claim_id}"):
                    if claim_id in claims:
                        show_claim(claims[claim_id])
                    else:
                        st.warning("Afirmación citada no disponible en este caso.")
    for title, entries in (("Preguntas de investigación", package.investigation_questions),
                           ("Verificaciones pendientes", package.pending_verifications)):
        st.subheader(title)
        for entry in entries:
            st.text(entry)
    st.subheader("Fuentes del paquete")
    show_refs(package.sources)


def show_review(event: Event, visible_package: StoryPackage | None) -> None:
    state = service.current_state(event.event_id)
    st.subheader(f"Estado actual: {state.value}")
    st.info("Aprobado como borrador NO significa publicado.")
    saved_package = service.get_package(event.event_id)
    package_matches = visible_package == saved_package
    st.caption(f"Paquete registrado para revisión: {saved_package.package_id if saved_package else 'ninguno'}")
    if not package_matches:
        st.warning("El paquete visible fue generado en esta sesión y no está guardado en el snapshot. "
                   "Vuelve al paquete del snapshot en Producir antes de registrar una revisión.")
    allowed = sorted(REVIEW_TRANSITIONS[state], key=lambda item: item.value)
    with st.form(f"review-{event.event_id}"):
        target = st.selectbox("Nuevo estado", allowed, format_func=lambda item: item.value)
        reviewer = st.text_input("Revisor")
        justification = st.text_area("Justificación obligatoria")
        submitted = st.form_submit_button("Guardar revisión", disabled=not package_matches)
    if submitted:
        if not package_matches:
            st.error("El paquete visible no coincide con el paquete guardado para revisión.")
        elif not reviewer.strip():
            st.error("El revisor es obligatorio.")
        elif not justification.strip():
            st.error("La justificación es obligatoria.")
        elif target not in REVIEW_TRANSITIONS[service.current_state(event.event_id)]:
            st.error("Transición no permitida: el estado cambió. Recarga la ficha.")
        else:
            try:
                service.review(event.event_id, target, reviewer.strip(), justification.strip())
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.rerun()
    st.subheader("Historial")
    history = service.review_history(event.event_id)
    if not history:
        st.info("Sin revisiones registradas.")
    for record in history:
        st.text(f"{local_time(record.decided_at)} · {record.reviewer} · "
                f"{record.from_state.value} → {record.to_state.value}")
        st.text(record.justification)
        st.caption(f"Revisión {record.review_id} · Hash de evidencia: {record.evidence_snapshot_sha256}")
        st.caption(f"Paquete: {record.package_id if record.package_id is not None else 'ninguno'}")


def main() -> None:
    st.set_page_config(page_title="Ficha de Caso · SCAYL", layout="wide")
    st.title("Ficha de Caso")
    bundle = service.load_bundle()
    if not bundle.events:
        st.info("No hay casos disponibles en este snapshot.")
        return
    events = {event.event_id: event for event in bundle.events}
    requested = st.query_params.get("event_id")
    ids = list(events)
    selected = st.selectbox("Caso", ids, index=ids.index(requested) if requested in events else 0)
    event = events[selected]
    st.header(event.title)
    if event.synthetic:
        st.warning("SINTÉTICO")
    if event.security_flags:
        st.warning("fuente con instrucciones sospechosas, tratada como dato")
        for flag in event.security_flags:
            st.text(flag)
    st.metric("Puntaje de atención P", event.priority.score)
    st.caption(f"Rango: {event.priority.tier.value} · Reglas: {event.priority.rules_version}")
    st.caption("P no es una probabilidad de verdad ni una medida de impacto.")
    st.info(f"Estado de evidencia: {event.evidence_status.value}")
    st.text(event.evidence_status_reason)
    st.warning("Prioridad alta NO habilita publicación.")
    st.text(event.recommended_action)
    tabs = st.tabs(["Evento", "Fuentes", "Evidencia", "Vacíos", "Producir", "Revisión"])
    with tabs[0]:
        st.text(f"Tema: {event.topic.value}")
        st.text("Entidades: " + (", ".join(event.entities) or "no disponibles"))
        if event.text_scope_note:
            st.info(event.text_scope_note)
        if event.is_recirculated:
            st.warning("Noticia recirculada: se conserva la fecha original de publicación.")
        st.subheader("Línea de tiempo")
        for label, timestamp in (("Primera publicación", event.first_published),
                                 ("Última publicación", event.last_published),
                                 ("Primera detección", event.first_detected)):
            st.text(f"{label}: {local_time(timestamp)}")
        st.subheader("Titulares del evento")
        news = [item for item in bundle.news if item.id_noticia in event.member_ids]
        news.sort(key=lambda item: (item.fecha_publicacion is None,
                                   item.fecha_publicacion.isoformat() if item.fecha_publicacion else "",
                                   item.id_noticia))
        if not news:
            st.info("Titulares individuales no disponibles en este snapshot.")
        for item in news:
            st.text(item.titulo)
            if item.sintetico or item.origen.value == "sintetico":
                st.caption("SINTÉTICO")
            st.caption(f"Medio: {item.medio or 'no disponible'} · "
                       f"Publicación: {local_time(item.fecha_publicacion)} · "
                       f"Detección: {local_time(item.fecha_deteccion)}")
            if item.url:
                st.text(item.url)
        st.subheader("Componentes de P")
        for key in ("R", "I", "U", "N", "E"):
            st.text(f"{key}: {getattr(event.priority.components, key)}")
            st.caption(event.priority.components.rationale.get(key, "Justificación no disponible"))
    with tabs[1]:
        dna = event.source_dna
        st.text(f"Publicaciones: {dna.publications} · Medios: {dna.outlets}")
        st.text(f"Máximo posible de fuentes independientes: {dna.max_possible_independent}")
        st.text(f"Independientes confirmadas: {dna.confirmed_independent}")
        st.info(dna.statement)
        for group in dna.groups:
            st.subheader(group.group_id)
            st.text(group.label.value)
            st.text(group.basis)
            st.text(", ".join(group.member_ids))
    with tabs[2]:
        for warning in event.temporal_warnings:
            st.warning(warning.message)
            st.caption(f"{warning.evidence_id} · Período: {warning.period}")
        st.subheader("Afirmaciones")
        if not event.claims:
            st.info("Sin afirmaciones disponibles.")
        for claim in event.claims:
            show_claim(claim)
        st.subheader("Evidencia oficial")
        show_refs(event.official_evidence)
        st.subheader("Conflictos")
        if not event.conflicts:
            st.info("No hay conflictos registrados.")
        for conflict in event.conflicts:
            st.text(f"{conflict.field} · {conflict.kind.value}")
            for col, label, version in zip(st.columns(2), ("Versión A", "Versión B"),
                                            (conflict.version_a, conflict.version_b)):
                with col:
                    st.subheader(label)
                    st.text(version.value)
                    show_refs(version.evidence)
            st.warning(f"Verificación pendiente: {conflict.verification_needed}")
    with tabs[3]:
        claims = {claim.claim_id: claim.statement for claim in event.claims}
        for field, title in (("we_know", "Qué sabemos"), ("it_is_claimed", "Qué se afirma"),
                             ("we_infer", "Qué inferimos"), ("we_dont_know", "Qué no sabemos"),
                             ("investigate_next", "Qué verificar después")):
            st.subheader(title)
            entries = getattr(event.gap, field) if event.gap else []
            if not entries:
                st.info("No disponible.")
            for entry in entries:
                st.text(claims.get(entry, entry))
    with tabs[4]:
        # Keep the package tied to its snapshot and event across Streamlit reruns.
        key = f"case-package:{bundle.snapshot_version}:{event.event_id}"
        if st.button("Generar", key=f"generate-{event.event_id}"):
            st.session_state[key] = service.generate_package(event.event_id)
        if key in st.session_state and st.button("Volver al paquete del snapshot"):
            del st.session_state[key]
        package = st.session_state.get(key) or service.get_package(event.event_id)
        if package is None:
            st.info("No hay un paquete generado para este caso.")
        else:
            show_package(package, event)
    with tabs[5]:
        show_review(event, package)


main()
