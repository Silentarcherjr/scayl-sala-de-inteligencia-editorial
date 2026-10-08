import json

import pytest
from streamlit.testing.v1 import AppTest

from deploy.prepare import check_public, prepare
from deploy.runtime import CacheOnlyLLM
from scayl.gen.llm import CacheMiss, OllamaBackend


def test_hosted_adapter_forces_cache_even_when_live_requested(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Hosted runtime must not call Ollama")
    monkeypatch.setattr(OllamaBackend, "chat_json", forbidden)
    llm = CacheOnlyLLM(mode="live", cache_dir=tmp_path)
    assert llm.mode == "cache"
    with pytest.raises(CacheMiss):
        llm.generate("test", "system", "user", {})


@pytest.mark.parametrize("payload", [
    {"news": [{"descripcion": "RSS privado"}]},
    {"claims": [{"evidence": [{"field": "descripcion", "value": "extracto"}]}]},
])
def test_public_audit_rejects_nested_rss(payload):
    with pytest.raises(ValueError, match="RSS"):
        check_public(payload)


def test_gate_fails_closed_and_accepts_password_then_invalidates_rotation(monkeypatch):
    code = "from deploy.space import require_password\nrequire_password()\nimport streamlit as st\nst.success('PROTECTED')"
    monkeypatch.delenv("SCAYL_SPACE_PASSWORD", raising=False)
    at = AppTest.from_string(code).run()
    assert not at.success and "deshabilitado" in at.error[0].value
    monkeypatch.setenv("SCAYL_SPACE_PASSWORD", "synthetic-test-password")
    at.run()
    at.text_input[0].input("wrong")
    at.button[0].click().run()
    assert not at.success and at.error[0].value == "Contraseña incorrecta."
    at.text_input[0].input("synthetic-test-password")
    at.button[0].click().run()
    assert at.success[0].value == "PROTECTED"
    assert "_space_password" not in at.session_state
    monkeypatch.setenv("SCAYL_SPACE_PASSWORD", "rotated-synthetic")
    at.run()
    assert not at.success


def test_staging_allowlist_and_all_page_routes_are_gated(bundle, tmp_path, monkeypatch):
    from scayl import service
    bundle.snapshot_version = "v1"
    bundle.reviews = []
    from tests.factories import news
    bundle.news = [news("demo", "[SINTÉTICO] Titular de demostración")]
    for item in bundle.news:
        item.descripcion = None
    source = tmp_path / "bundle.json"
    source.write_text(bundle.model_dump_json(), encoding="utf-8")
    destination = tmp_path / "stage"
    report = prepare(source, tmp_path / "empty-cache", destination)
    assert not report["published"] and report["cache_entries"] == 0
    assert (destination / "data/cache/llm").is_dir()
    assert not (destination / "data/raw").exists()
    assert not (destination / "data/labels").exists()
    assert not (destination / ".env").exists()
    assert json.loads((destination / "data/processed/v1/bundle.json").read_text(encoding="utf-8"))["news"][0]["descripcion"] is None
    monkeypatch.delenv("SCAYL_SPACE_PASSWORD", raising=False)
    at = AppTest.from_file(str(destination / "app/space.py")).run()
    assert not at.exception
    for page in ("pages/1_Ficha_de_Caso.py", "pages/2_Consultas.py", "pages/3_Trust_Lab.py", "pages/4_Simulador_de_pesos.py"):
        at.switch_page(page).run()
        assert not at.exception and "deshabilitado" in at.error[0].value
        assert not at.metric and not at.dataframe
    monkeypatch.setattr(service, "bundle_path", lambda: source)
    original_llm = service.LLM
    monkeypatch.setattr(service, "LLM", original_llm)  # restore hosting adapter after this test
    monkeypatch.setenv("SCAYL_SPACE_PASSWORD", "synthetic-test-password")
    monkeypatch.setenv("SCAYL_HOSTED", "1")
    service.reload()
    try:
        at.switch_page("pages/2_Consultas.py").run()
        at.text_input[0].input("synthetic-test-password")
        at.button[0].click().run()
        assert not at.exception
        assert at.selectbox[0].options == ["cache"]
        assert "Demo snapshot" in at.caption[0].value
        next(b for b in at.button if b.label == "Cerrar sesión").click().run()
        assert not at.selectbox and not at.metric
        monkeypatch.delenv("SCAYL_SPACE_PASSWORD")
        at.run()
        assert not at.selectbox and not at.metric  # closing the deployment revokes existing sessions
    finally:
        service.reload()


@pytest.mark.parametrize("flag", ["", "0", "true", "yes"])
def test_public_access_needs_exact_opt_in(monkeypatch, flag):
    code = "from deploy.space import require_password\nrequire_password()\nimport streamlit as st\nst.success('OPEN')"
    monkeypatch.delenv("SCAYL_SPACE_PASSWORD", raising=False)
    monkeypatch.setenv("SCAYL_PUBLIC_ACCESS", flag)
    at = AppTest.from_string(code).run()
    assert not at.success and "deshabilitado" in at.error[0].value


def test_public_access_opens_without_password_or_logout(monkeypatch):
    code = ("from deploy.space import hosted_frame\nhosted_frame()\nimport streamlit as st\nst.success('OPEN')")
    monkeypatch.delenv("SCAYL_SPACE_PASSWORD", raising=False)
    monkeypatch.setenv("SCAYL_PUBLIC_ACCESS", "1")
    at = AppTest.from_string(code).run()
    assert at.success[0].value == "OPEN" and not at.text_input and not at.error
    assert not [b for b in at.button if b.label == "Cerrar sesión"]


def test_public_access_read_from_streamlit_secrets(monkeypatch):
    """Streamlit Cloud may not re-export secrets edited at runtime; st.secrets is the fallback."""
    import streamlit as st

    from deploy import space

    monkeypatch.delenv("SCAYL_SPACE_PASSWORD", raising=False)
    monkeypatch.delenv("SCAYL_PUBLIC_ACCESS", raising=False)
    monkeypatch.setattr(st, "secrets", {"SCAYL_PUBLIC_ACCESS": "1"})
    assert space.public_access()
    monkeypatch.setattr(st, "secrets", {"SCAYL_PUBLIC_ACCESS": 1})  # TOML integer, not the exact string "1"
    assert not space.public_access()
    monkeypatch.setattr(st, "secrets", {"SCAYL_SPACE_PASSWORD": "from-secrets"})
    assert space._setting("SCAYL_SPACE_PASSWORD") == "from-secrets"
