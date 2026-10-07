"""B-05 baseline: keyword topics and TF-IDF clustering with a time constraint (T02 on real-like titles)."""
from datetime import timedelta

from scayl.contracts import Topic
from scayl.intel.cluster import cluster
from scayl.intel.embed import get_embedder
from scayl.intel.topics import classify, classify_one
from tests.factories import CUTOFF, news


def test_topics_follow_official_taxonomy():
    assert classify_one("El Canal de Panamá aplica nueva reducción del calado")[0] == Topic.LOGISTICA_CANAL
    assert classify_one("Sismo de magnitud 4,6 sacude Chiriquí")[0] == Topic.EVENTOS_NATURALES
    assert classify_one("Inflación en Panamá baja en julio")[0] == Topic.ECONOMIA
    assert classify_one("Llegada de turistas crece en el aeropuerto de Tocumen")[0] == Topic.TURISMO
    assert classify_one("IDAAN suspende el suministro de agua potable")[0] == Topic.SERVICIOS_PUBLICOS
    assert classify_one("Asamblea aprueba proyecto de ley de transparencia")[0] == Topic.REGULACION
    assert classify_one("Concierto de fin de semana")[0] == Topic.OTRO
    assert classify([news("a", "Canal amplía tránsito de buques")])[0][0] == Topic.LOGISTICA_CANAL


def test_same_event_headlines_cluster_and_unrelated_do_not():
    t = CUTOFF - timedelta(days=2)
    items = [news("a", "Canal de Panamá reduce el calado por la sequía", pub=t),
             news("b", "Canal de Panamá reduce calado ante la sequía", medio="b.com", pub=t + timedelta(hours=3)),
             news("c", "El Canal de Panamá reduce el calado por sequía", medio="c.com", pub=t + timedelta(hours=5)),
             news("d", "Festival de jazz llena el casco antiguo", medio="d.com", pub=t)]
    groups = cluster(items, get_embedder("tfidf"))
    assert ["a", "b", "c"] in groups and ["d"] in groups


def test_time_constraint_prevents_merging_identical_headlines_far_apart():
    items = [news("a", "Canal de Panamá reduce el calado por la sequía", pub=CUTOFF - timedelta(days=40)),
             news("b", "Canal de Panamá reduce el calado por la sequía", medio="b.com", pub=CUTOFF - timedelta(days=1))]
    assert cluster(items, get_embedder("tfidf")) == [["a"], ["b"]]
