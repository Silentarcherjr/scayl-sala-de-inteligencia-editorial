"""LLM claim extraction from headlines (L-10). Conservative by construction.

Every extracted claim is something a MEDIA OUTLET asserted: status SOLO_REPORTADA, type DECLARACION,
attributed, with the headline as evidence. Claims whose numbers are not in the source headline, that
cite an unknown source, or that echo injected instructions are dropped.
"""

from __future__ import annotations

import re
import unicodedata

from scayl.contracts import Claim, ClaimStatus, ClaimType, Event, NewsItem
from scayl.evidence.linking import news_ref
from scayl.gen.guard import SYSTEM_DATA_RULE, data_block, scan
from scayl.gen.llm import LLM, LLMError, load_prompt
from scayl.gen.validators import numbers_in

PROMPT_VERSION = "claims-v1"
MAX_PER_EVENT = 6
SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "statement": {"type": "string"},
                    "type": {"type": "string", "enum": ["HECHO", "DECLARACION"]},
                    "attributed_to": {"type": ["string", "null"]},
                },
                "required": ["source_id", "statement", "type"],
            },
        }
    },
    "required": ["claims"],
}


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", text).split())


def extract(event: Event, items: list[NewsItem], llm: LLM) -> list[Claim]:
    """Return NEW claims to append to the event (may be empty). Never raises on model problems."""
    members = {i.id_noticia: i for i in items if i.id_noticia in set(event.member_ids)}
    if llm.mode == "template" or not members:
        return []
    payload = {"noticias": [{"id": i.id_noticia, "titulo": i.titulo, "medio": i.medio,
                             "descripcion": i.descripcion} for i in members.values()]}
    system = load_prompt("claims", "v1").replace("REGLA_DE_SEGURIDAD", SYSTEM_DATA_RULE)
    try:
        data, meta = llm.generate(PROMPT_VERSION, system, "Extrae las afirmaciones.\n" + data_block(payload), SCHEMA)
    except LLMError:
        return []

    seen = {_norm(c.statement) for c in event.claims}
    out: list[Claim] = []
    n = len(event.claims)
    for raw in data.get("claims", []):
        item = members.get(str(raw.get("source_id", "")))
        statement = str(raw.get("statement", "")).strip().rstrip(".")
        if not item or not statement or scan(statement) or _norm(statement) in seen:
            continue
        source_nums = numbers_in(" ".join(filter(None, [item.titulo, item.descripcion])))
        if any(not (n_ & source_nums) for n_ in (numbers_in(tok) for tok in statement.split()) if n_):
            continue  # invented or altered figure
        who = (raw.get("attributed_to") or "").strip() or item.medio or "el medio"
        if who != (item.medio or "") and item.medio:
            who = f"{who} (según {item.medio})"
        n += 1
        seen.add(_norm(statement))
        out.append(Claim(
            claim_id=f"CLM-{event.event_id.removeprefix('EVT-')}-{n:03d}", event_id=event.event_id,
            statement=statement, type=ClaimType.DECLARACION, status=ClaimStatus.SOLO_REPORTADA, attributed_to=who,
            evidence=[news_ref(item)], reason="Extraída del titular; afirmada por el medio, sin verificación oficial.",
            extracted_by=f"llm:{meta.model}@{PROMPT_VERSION}"))
        if len(out) >= MAX_PER_EVENT:
            break
    return out
