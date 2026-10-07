from scayl.eval.run import build_report, precision_at_5, pytest_results


def real_events(bundle):
    bundle.events = [bundle.events[0].model_copy(deep=True) for _ in range(6)]
    for n, event in enumerate(bundle.events):
        event.event_id = f"E{n}"
        event.member_ids = [f"N{n}"]
        event.synthetic = False
        event.priority.score = 90 - n
    return bundle


def test_precision_maps_news_to_events_and_preserves_denominator(bundle):
    bundle = real_events(bundle)
    bundle.events[0].member_ids.append("copy")
    result = precision_at_5(bundle, {"ids": ["N0", "copy", "N2", "N4", "N5"]})
    assert result["num"] == 3 and result["den"] == 5 and result["value"] == 0.6
    assert result["duplicates_collapsed"] == 1
    assert result["editor_positions"]["E5"] == 6
    assert result["exploratory"] and "1 de 5" in result["limitation"]


def test_missing_id_is_not_silently_scored_as_zero(bundle):
    result = precision_at_5(real_events(bundle), {"ids": ["N0", "N1", "N2", "N3", "missing"]})
    assert result["status"] == "no medido" and result["value"] is None


def test_ties_use_u_then_id_and_do_not_modify_input(bundle):
    bundle = real_events(bundle)
    for event in bundle.events:
        event.priority.score = 70
    bundle.events[5].priority.components.U = 1
    bundle.events.reverse()
    result = precision_at_5(bundle, {"ids": [f"N{n}" for n in range(5)]})
    assert result["system_top5"] == ["E5", "E0", "E1", "E2", "E3"]
    assert bundle.events[0].event_id == "E5"


def test_absent_measurements_remain_null_and_labelled(bundle):
    report = build_report(real_events(bundle), {"ids": [f"N{n}" for n in range(5)]})
    assert report["metrics"]["citation_coverage"]["status"] == "no medido"
    assert report["metrics"]["citation_coverage"]["num"] is None
    assert report["metrics"]["latency_ms"]["qa"]["n"] is None
    assert report["tests"]["T01"]["status"] == "no medido"


def test_saved_pytest_failures_and_skips_are_visible(tmp_path):
    path = tmp_path / "junit.xml"
    path.write_text('<testsuites><testsuite><testcase classname="tests.test_t01_validation" name="a"/>'
                    '<testcase classname="tests.test_t01_validation" name="b"><failure/></testcase>'
                    '<testcase classname="tests.test_t07_injection" name="c"><skipped/></testcase>'
                    '</testsuite></testsuites>')
    result = pytest_results(path)
    assert result["T01"]["num"] == 1 and result["T01"]["den"] == 2
    assert result["T01"]["failures"][0]["test"].endswith(".b")
    assert result["T07"]["status"] == "failed_or_skipped"
    assert result["T10"]["status"] == "no medido"


def test_cli_writes_utf8_artifacts_with_portable_console(bundle, tmp_path, monkeypatch, capsys):
    import json

    from scayl.eval import run

    bundle_dir = tmp_path / "data/processed/v1"
    labels_dir = tmp_path / "data/labels"
    bundle_dir.mkdir(parents=True)
    labels_dir.mkdir(parents=True)
    (bundle_dir / "bundle.json").write_text(real_events(bundle).model_dump_json(), encoding="utf-8")
    (labels_dir / "editor_top5.json").write_text(json.dumps({"ids": [f"N{n}" for n in range(5)]}))
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["eval", "--snapshot", "v1"])
    run.main()
    console = capsys.readouterr().out
    assert console.isascii() and json.loads(console)["value"] == 1
    saved = json.loads((tmp_path / "eval/results/latest.json").read_text(encoding="utf-8"))
    assert "selección" in saved["metrics"]["precision_at_5"]["limitation"]
    assert (tmp_path / saved["saved_run"]).exists()


def test_human_label_metrics_are_imported_with_provenance(tmp_path):
    import json

    from scayl.eval import run
    path = tmp_path / "b07.json"
    path.write_text(json.dumps({"topics": {"status": "medido", "baseline": {"macro_f1": 0.75, "n": 100},
                                           "ai": {"macro_f1": 0.25, "n": 100}},
                                "clustering": {"status": "medido; desarrollo asistido", "baseline": {"f1": 0.4},
                                               "ai": {"f1": 0.9}}}), encoding="utf-8")
    m = run.human_label_metrics(path)
    assert m["topics_macro_f1"]["baseline"] == 0.75 and m["topics_macro_f1"]["n"] == 100
    assert m["clustering"]["ai_f1"] == 0.9 and m["clustering"]["measurement"]["sha256"]
    assert run.human_label_metrics(tmp_path / "missing.json") == {}
