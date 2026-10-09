"""Source DNA: conservative provenance grouping (ARCHITECTURE §4.3).

Never infers that outlet B copied outlet A. It only collapses publications when there is explicit
evidence of common provenance (same outlet, identical headline, agency signature). Everything else
is "independence unknown". Independent provenance between media is never confirmed from metadata.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import urlparse

from scayl.contracts import NewsItem, ProvenanceGroup, ProvenanceLabel, SourceDNA

NO_INDEPENDENCE = "La procedencia independiente no puede determinarse con la evidencia disponible."
IDENTICAL_TITLE_RATIO = 0.97
AGENCIES = {
    "EFE": r"\bEFE\b", "AFP": r"\bAFP\b", "Reuters": r"\bReuters\b", "AP": r"\(AP\)|\bAP\b\s*[-—–]|Associated Press",
    "Europa Press": r"Europa Press", "Xinhua": r"\bXinhua\b", "ANSA": r"\bANSA\b", "DPA": r"\bDPA\b",
    "Prensa Latina": r"Prensa Latina", "Bloomberg": r"\bBloomberg\b",
}
_AGENCY_RE = {name: re.compile(rx) for name, rx in AGENCIES.items()}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", text.lower()).split())


_EDITION_PREFIXES = ("www.", "m.", "amp.", "mobile.")
_OUTLET_SUFFIX = re.compile(r"\s+[-|–—]\s+[^-|–—]{1,40}$")


def outlet_key(item: NewsItem) -> str:
    """Host without edition prefixes: www./m./amp. editions of one outlet are the same outlet (C2)."""
    if item.url:
        host = urlparse(item.url).netloc.lower()
        for prefix in _EDITION_PREFIXES:
            host = host.removeprefix(prefix)
        if host:
            return host
    return (item.medio or "desconocido").strip().lower()


def core_title(title: str) -> str:
    """Headline without a trailing " - Outlet" / " | Outlet" tag, so syndicated copies compare equal."""
    return _OUTLET_SUFFIX.sub("", title.strip())


def agency_of(item: NewsItem) -> str | None:
    text = " ".join(filter(None, [item.titulo, item.descripcion]))
    for name, rx in _AGENCY_RE.items():
        if rx.search(text):
            return name
    return None


class _UnionFind:
    def __init__(self, ids: list[str]):
        self.parent = {i: i for i in ids}

    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        self.parent[self.find(a)] = self.find(b)


def source_dna(items: list[NewsItem], group_prefix: str = "PG") -> SourceDNA:
    ids = [i.id_noticia for i in items]
    by_id = {i.id_noticia: i for i in items}
    uf = _UnionFind(ids)
    reasons: dict[tuple[str, str], list[str]] = {}

    for idx, a in enumerate(items):
        for b in items[idx + 1:]:
            pair_reasons = []
            if outlet_key(a) == outlet_key(b):
                pair_reasons.append("mismo_medio")
            else:
                if SequenceMatcher(None, normalize_text(core_title(a.titulo)), normalize_text(core_title(b.titulo))).ratio() >= \
                        IDENTICAL_TITLE_RATIO:
                    pair_reasons.append("titular idéntico en medios distintos")
                if agency_of(a) and agency_of(a) == agency_of(b):
                    pair_reasons.append(f"firma de agencia {agency_of(a)}")
            if pair_reasons:
                uf.union(a.id_noticia, b.id_noticia)
                reasons[(a.id_noticia, b.id_noticia)] = pair_reasons

    clusters: dict[str, list[str]] = {}
    for i in ids:
        clusters.setdefault(uf.find(i), []).append(i)

    groups = []
    for n, members in enumerate(sorted(clusters.values(), key=lambda m: (-len(m), m[0])), start=1):
        member_reasons = {r for (a, b), rs in reasons.items() if a in members and b in members for r in rs}
        outlets = {outlet_key(by_id[m]) for m in members}
        if len(members) > 1 and len(outlets) == 1:
            label, basis = ProvenanceLabel.MISMO_MEDIO, f"{len(members)} publicaciones del mismo medio ({outlets.pop()})"
        elif len(members) > 1:
            label = ProvenanceLabel.PROCEDENCIA_COMUN_IDENTIFICADA
            basis = "; ".join(sorted(member_reasons - {"mismo_medio"})) or "procedencia común"
        else:
            label = ProvenanceLabel.INDEPENDENCIA_DESCONOCIDA
            agency = agency_of(by_id[members[0]])
            basis = f"Sin información de procedencia{f' (firma {agency})' if agency else ''}."
        groups.append(ProvenanceGroup(group_id=f"{group_prefix}-{n}", label=label, member_ids=sorted(members),
                                      basis=basis))

    confirmed = sum(g.label == ProvenanceLabel.PROCEDENCIA_INDEPENDIENTE_CONFIRMADA for g in groups)
    statement = NO_INDEPENDENCE if confirmed == 0 else (
        f"{confirmed} procedencia(s) independiente(s) confirmada(s) con evidencia explícita."
    )
    return SourceDNA(
        publications=len(items),
        outlets=len({outlet_key(i) for i in items}),
        groups=groups,
        confirmed_independent=confirmed,
        max_possible_independent=len(groups),
        statement=statement,
    )
