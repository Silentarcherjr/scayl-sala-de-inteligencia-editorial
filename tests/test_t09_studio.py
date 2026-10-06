"""T09 (generation half): LLM package keeps useful format, valid citations, facts vs statements."""
from datetime import timedelta

from scayl.contracts import ClaimType, Topic
from scayl.evidence.assemble import build_event
from scayl.gen import claims, studio
from scayl.gen.llm import LLM, LLMUnavailable
from scayl.gen.validators import SCOPE_PHRASE
from tests.factories import CUTOFF, news, quake
from tests.fake_llm import fake_llm

T = CUTOFF - timedelta(hours=6)


def seismic_event():
    items = [news("a", "Sismo de magnitud 4.6 sacude Chiriquí, según el Instituto de Geociencias", pub=T),
             news("b", "Fuerte temblor de 4.6 se siente en David", medio="otro.com", pub=T)]
    return build_event("EVT-0010", items, Topic.EVENTOS_NATURALES, 0.9, [], [quake("us9", 4.6, T)], CUTOFF), items


def good_response(e):
    c = {x.status.value: x.claim_id for x in e.claims}
    return {
        "proposed_title": "Sismo de magnitud 4.6 en Chiriquí: lo que se sabe",
        "public_interest_angle": "Informar con precisión y sin alarma sobre daños no confirmados.",
        "brief": [
            {"text": "USGS registró un sismo de magnitud 4.6 en la zona.", "tag": "HECHO", "claim_ids": [c["SUSTENTADA"]]},
            {"text": "Según medios locales, el temblor se sintió en Chiriquí.", "tag": "DECLARACION",
             "claim_ids": [c["SOLO_REPORTADA"]]},
            {"text": "No hay datos verificados de daños.", "tag": "HECHO", "claim_ids": [c["SIN_SUSTENTO"]]},
            {"text": "El sismo dejó 15 heridos.", "tag": "HECHO", "claim_ids": [c["SUSTENTADA"]]},
        ],
        "investigation_questions": ["¿Reporta daños SINAPROC?", "¿Hubo réplicas?", "¿Qué zonas lo sintieron?"],
        "script": [{"text": "Un sismo de magnitud 4.6 fue registrado por el USGS.", "tag": "HECHO",
                    "claim_ids": [c["SUSTENTADA"]]}],
        "social_copy": {"text": "USGS registró un sismo de 4.6. Sin reportes verificados de daños.", "tag": "HECHO",
                        "claim_ids": [c["SUSTENTADA"], c["SIN_SUSTENTO"]]},
        "pending_verifications": ["Daños con SINAPROC"],
    }


def test_llm_package_is_validated_and_hallucination_removed(tmp_path):
    e, _ = seismic_event()
    llm, _ = fake_llm(tmp_path, {"studio": good_response(e)})
    pkg = studio.generate(e, llm)
    texts = [s.text for s in pkg.brief]
    assert "El sismo dejó 15 heridos." not in texts and len(texts) == 3
    assert {s.tag for s in pkg.brief} == {ClaimType.HECHO, ClaimType.DECLARACION}
    assert pkg.generated_by.mode == "live" and pkg.generated_by.cost_usd == 0.0
    assert pkg.scope_disclaimer == SCOPE_PHRASE and len(pkg.investigation_questions) == 3
    assert pkg.validation.passed


def test_title_with_unsupported_figure_is_replaced(tmp_path):
    e, _ = seismic_event()
    resp = good_response(e) | {"proposed_title": "Sismo de 6.1 deja 40 heridos"}
    llm, _ = fake_llm(tmp_path, {"studio": resp})
    pkg = studio.generate(e, llm)
    assert "6.1" not in pkg.proposed_title and any(i.code == "TITLE_REPLACED" for i in pkg.validation.issues)


def test_unavailable_or_broken_model_falls_back_to_template(tmp_path):
    e, _ = seismic_event()
    down, _ = fake_llm(tmp_path, {"studio": LLMUnavailable("Ollama apagado")})
    pkg = studio.generate(e, down)
    assert pkg.generated_by.mode == "template" and pkg.validation.issues[0].code == "LLM_FALLBACK"
    broken, _ = fake_llm(tmp_path / "b", {"studio": {"unexpected": True}})
    assert studio.generate(e, broken).generated_by.mode == "template"
    assert studio.generate(e, LLM(mode="cache", cache_dir=tmp_path / "empty")).generated_by.mode == "template"


def test_claim_extraction_is_attributed_and_drops_altered_figures(tmp_path):
    e, items = seismic_event()
    llm, _ = fake_llm(tmp_path, {"claims": {"claims": [
        {"source_id": "a", "statement": "El temblor fue sentido en Chiriquí", "type": "HECHO",
         "attributed_to": "Instituto de Geociencias"},
        {"source_id": "b", "statement": "El temblor fue de 5.4", "type": "HECHO"},
        {"source_id": "zzz", "statement": "Inventada", "type": "HECHO"},
    ]}})
    new = claims.extract(e, items, llm)
    assert [c.statement for c in new] == ["El temblor fue sentido en Chiriquí"]
    assert new[0].status.value == "SOLO_REPORTADA" and new[0].type == ClaimType.DECLARACION
    assert "Instituto de Geociencias" in new[0].attributed_to and new[0].evidence[0].evidence_id == "news:a"


def test_generation_report_measures_removals_and_attribution(tmp_path):
    from scayl.gen.studio import generate_with_report
    e, _ = seismic_event()
    llm, _ = fake_llm(tmp_path, {"studio": good_response(e)})
    _, report = generate_with_report(e, llm)
    assert report["sentences_generated"] == 6 and report["sentences_kept"] == 5
    assert report["removed_by_code"] == {"NUMBER_NOT_IN_EVIDENCE": 1}
    assert report["attribution"]["candidates"] >= 1 and report["cost_usd"] == 0.0


def test_pipeline_with_llm_enriches_top_events_and_writes_report(tmp_path):
    from scayl.pipeline import GENERATION_REPORTS, build_bundle, write_outputs
    e, items = seismic_event()
    llm, _ = fake_llm(tmp_path, {"studio": good_response(e), "claims": {"claims": []}})
    bundle = build_bundle(items, [], [quake("us9", 4.6, T)], CUTOFF, "t", 2,
                          classify=lambda xs: [(Topic.EVENTOS_NATURALES, 0.9)] * len(xs),
                          cluster=lambda xs: [[x.id_noticia for x in xs]], llm=llm, public=True)
    assert bundle.news and all(n.descripcion is None for n in bundle.news)
    assert len(GENERATION_REPORTS) == 1
    write_outputs(bundle, tmp_path / "out")
    assert (tmp_path / "out" / "generation_report.jsonl").read_text(encoding="utf-8").strip()
