"""A-10: weight simulator. Shows how the ranking changes; official scoring-v1 stays until a recorded decision."""
import streamlit as st

from scayl import service

COMPONENTS = {"R": "Relevancia", "I": "Impacto potencial", "U": "Urgencia", "N": "Novedad", "E": "Evidencia disponible"}


def main() -> None:
    st.set_page_config(page_title="Simulador de pesos · SCAYL", layout="wide")
    st.title("Simulador de pesos")
    st.caption("P = wR·R + wI·I + wU·U + wN·N + wE·E. Es un puntaje de atención, no de verdad ni de impacto. "
               "Simular no cambia el ranking oficial (scoring-v1).")
    official = service.official_weights()
    cols = st.columns(len(COMPONENTS))
    weights = {}
    for col, (key, label) in zip(cols, COMPONENTS.items()):
        with col:
            weights[key] = int(st.number_input(f"{label} ({key})", min_value=0, max_value=100,
                                               value=official[key], step=5, key=f"w-{key}"))
    total = sum(weights.values())
    if total != 100:
        st.error(f"Los pesos deben sumar 100 (ahora suman {total}).")
        return
    is_official = weights == official
    st.success("Pesos oficiales del reto (scoring-v1)." if is_official else "Pesos simulados.")

    baseline = service.simulate_weights(official)
    simulated = service.simulate_weights(weights)
    pos_before = {e.event_id: i for i, e in enumerate(baseline, start=1)}
    st.caption(f"Versión de reglas: {simulated[0].priority.rules_version if simulated else 'sin eventos'}")
    rows = []
    for i, e in enumerate(simulated, start=1):
        delta = pos_before[e.event_id] - i
        arrow = "=" if delta == 0 else (f"▲{delta}" if delta > 0 else f"▼{-delta}")
        rows.append({"Posición": i, "Cambio": arrow, "Evento": e.event_id, "Título": e.title[:80],
                     "P oficial": f"{next(b.priority.score for b in baseline if b.event_id == e.event_id):.1f}",
                     "P simulado": f"{e.priority.score:.1f}", "Rango": e.priority.tier.value,
                     "Evidencia": e.evidence_status.value})
    st.table(rows)
    st.caption("El estado de evidencia no cambia con los pesos: prioridad y evidencia son conceptos separados.")

    if not is_official:
        st.subheader("Registrar la justificación del cambio")
        with st.form("weight-change"):
            author = st.text_input("Autor")
            justification = st.text_area("Justificación obligatoria")
            submitted = st.form_submit_button("Registrar simulación")
        if submitted:
            try:
                entry = service.record_weight_change(weights, author, justification)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success(f"Registrado ({entry['rules_version']}). Queda pendiente de decisión del equipo.")


main()
