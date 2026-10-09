"""Regression: two different quakes, one day apart, different magnitudes, must not be one event (real EVT-0114).

Synthetic headlines modelled on the real case: a M4.7 Panamá–Costa Rica quake and a M7.4 México–Guatemala quake
"sin riesgo de tsunami para Panamá", both from the same outlet, which the embedder clustered together."""
from datetime import UTC, datetime

from scayl.intel.cluster import split_distinct_quakes
from scayl.pipeline import build_bundle, stable_ids
from tests.factories import CUTOFF, news, quake

D1 = datetime(2026, 7, 16, 18, tzinfo=UTC)
D2 = datetime(2026, 7, 17, 18, tzinfo=UTC)
LOCAL = news("n-local", "Sismo de magnitud 4.7 sacude la frontera entre Panamá y Costa Rica; no se reportan daños",
             medio="telemetro.com", pub=D1)
REMOTE = news("n-remote", "Sismo de magnitud 7.4 entre México y Guatemala no genera riesgo de tsunami para Panamá",
              medio="telemetro.com", pub=D2)


def test_quakes_in_disjoint_countries_are_split():
    assert split_distinct_quakes([LOCAL, REMOTE], [["n-local", "n-remote"]]) == [["n-local"], ["n-remote"]]


def test_same_quake_named_by_province_and_country_stays_together():
    other = news("n-chiriqui", "Temblor de magnitud 4.5 se sintió en Chiriquí", medio="otro.com", pub=D1)
    assert split_distinct_quakes([LOCAL, other], [["n-chiriqui", "n-local"]]) == [["n-chiriqui", "n-local"]]


def test_headline_without_place_is_not_split_off():
    vague = news("n-vague", "Fuerte sismo de magnitud 4.7 sacude la región", medio="otro.com", pub=D1)
    assert split_distinct_quakes([LOCAL, vague], [["n-local", "n-vague"]]) == [["n-local", "n-vague"]]


def test_non_seismic_clusters_are_untouched():
    a = news("a", "Canal de Panamá aumenta cupos en México y Guatemala", pub=D1)
    b = news("b", "Exportaciones de Costa Rica crecen", pub=D1)
    assert split_distinct_quakes([a, b], [["a", "b"]]) == [["a", "b"]]


def test_stable_ids_keep_existing_ids_and_append_new_ones():
    by = {"n-local": D1, "n-remote": D2, "x": datetime(2026, 7, 20, tzinfo=UTC)}

    def first_date(ids):
        return min(by[i] for i in ids), min(ids)

    reference = {"EVT-0001": ["n-local", "n-remote"], "EVT-0002": ["x"]}
    numbered = stable_ids([["n-local"], ["n-remote"], ["x"]], reference, first_date)
    assert numbered == [("EVT-0001", ["n-local"]), ("EVT-0002", ["x"]), ("EVT-0003", ["n-remote"])]


def test_frozen_rebuild_splits_event_and_drops_false_magnitude_conflict():
    usgs = quake("us-1", 4.5, datetime(2026, 7, 16, 10, 33, tzinfo=UTC), place="3 km ENE of Santa Cruz, Panama")
    reference = {"EVT-0114": ["n-local", "n-remote"]}
    bundle = build_bundle([LOCAL, REMOTE], [], [usgs], CUTOFF, "test", 2,
                          cluster=lambda items: [list(ids) for ids in reference.values()], reference=reference)
    events = {e.event_id: e for e in bundle.events}
    assert sorted(events) == ["EVT-0114", "EVT-0115"]
    assert events["EVT-0114"].member_ids == ["n-local"]
    assert events["EVT-0115"].member_ids == ["n-remote"]
    values = {(c.version_a.value, c.version_b.value) for e in bundle.events for c in e.conflicts}
    assert not any("7.4" in pair for pair in values)
    # the remaining conflict is the legitimate one: headline 4.7 vs USGS 4.5, same day, same area
    assert ("4.7", "4.5") in values
