"use client";
import { useEffect, useRef } from "react";
import Link from "next/link";
import type { Bulletin } from "@/lib/bulletin-types";
import type { Claim, Sentence } from "@/lib/types";
import { Heading, Badge, Citation, GenerationNote, ValidationNote, TextList } from "./shared";
import Sentences from "./sentences";
type Headline = {evidence_id:string;title:string;language:string|null};
type UsedEvent = {event_id:string;title:string;synthetic:boolean;language:string|null};
const languageNames: Record<string,string> = {mar:"maratí",hi:"hindi",en:"inglés",pt:"portugués",fr:"francés"};
function OriginalLanguage({language}: {language:string|null}) {
  return language && !["es","spa"].includes(language)
    ? <p className="muted bank-original-language">titular en idioma original ({languageNames[language] ?? language})</p>
    : null;
}
export default function BulletinView({bulletin:b, claims, events, headlines}: {
  bulletin: Bulletin; claims: Claim[]; events: UsedEvent[]; headlines: Headline[];
}) {
  const root = useRef<HTMLDivElement | null>(null);
  const printState = useRef<{node:HTMLDetailsElement;open:boolean}[] | null>(null);
  useEffect(() => {
    const before = () => {
      if (printState.current !== null) return;
      printState.current = Array.from(root.current?.querySelectorAll("details") ?? []).map(node => ({node,open:node.open}));
      printState.current.forEach(({node}) => { node.open = true; });
    };
    const after = () => {
      printState.current?.forEach(({node,open}) => { node.open = open; });
      printState.current = null;
    };
    window.addEventListener("beforeprint", before);
    window.addEventListener("afterprint", after);
    return () => { after(); window.removeEventListener("beforeprint", before); window.removeEventListener("afterprint", after); };
  }, []);
  const renderSentences = (sentences: Sentence[]) => sentences.map((s,i) => {
    const evidenceIds = s.claim_ids.flatMap(id => claims.find(c=>c.claim_id===id)?.evidence.map(r=>r.evidence_id) ?? [id]);
    const languages = [...new Set(headlines.filter(h=>evidenceIds.includes(h.evidence_id)).map(h=>h.language))];
    return <div className="bank-cited-sentence" key={i}>{languages.map(language=><OriginalLanguage key={language ?? "unknown"} language={language}/>)}<Sentences sentences={[s]} claims={claims} citations={b.sources}/></div>;
  });
  return <div className="bank-page" ref={root}>
    <Heading section="Extensión bancaria · boletín de entorno" title="Boletín de entorno logístico">El mismo núcleo de evidencia para un analista de estudios económicos o riesgo sectorial. SCAYL mantiene su modalidad editorial; este boletín es una extensión.</Heading>
    <div className="bank-print-controls"><button className="button" onClick={()=>window.print()}>Imprimir / guardar PDF</button></div>
    <section aria-label="Boletín de logística">
      <div className="warning bank-limits"><strong>Alcance del boletín</strong><p>{b.limits_notice}</p></div>
      <p className="eyebrow">{b.bulletin_id} · Logística y Canal</p><h2>{b.question}</h2>
      <p><strong>Usuario:</strong> Analista de estudios económicos o riesgo sectorial</p>
      <p><strong>Horizonte temporal:</strong> {b.horizon}</p><GenerationNote meta={b.generated_by}/>
      {b.scope_disclaimer ? <p className="warning">{b.scope_disclaimer}</p> : null}
      <article className="card"><h2>Resumen</h2>{renderSentences(b.summary)}</article>
      <section className="grid-two bank-columns">
        <article className="card"><p className="eyebrow">Lo que dicen las fuentes</p><h2>Observación</h2><p className="muted">Las declaraciones conservan atribución. Los indicadores aportan contexto de su período; no confirman por sí solos los titulares.</p>{renderSentences(b.observations)}</article>
        <article className="card bank-hypotheses"><p className="eyebrow">Posibilidades que deben comprobarse</p><h2>Hipótesis de impacto</h2><p className="warning">HIPÓTESIS · requieren verificación. No son hechos observados ni pronósticos.</p>{renderSentences(b.impact_hypotheses)}</article>
      </section>
      <section className="card"><h2>Sectores potencialmente relacionados</h2><div className="badges">{b.related_sectors.map(item=><Badge key={item} value={item}/>)}</div><h2>Tres preguntas para el analista</h2><TextList items={b.analyst_questions}/></section>
      <section className="card"><h2>Eventos usados</h2><p className="muted">Seleccionados en el orden de prioridad oficial; no se calcula un puntaje bancario.</p><ol className="text-list">{b.event_ids.map(id => {
        const e = events.find(item=>item.event_id===id);
        return <li key={id}><OriginalLanguage language={e?.language ?? null}/><Link href={`/caso/${id}/`}>{id} · {e?.title ?? "Título no disponible"}</Link>{e?.synthetic ? <Badge value="SINTÉTICO"/> : null}</li>;
      })}</ol></section>
      <section><h2>Fuentes y períodos</h2>{b.sources.map((ref,i)=><div className={ref.evidence_id.startsWith("bulletin:") ? "bank-derived-count" : undefined} key={`${ref.evidence_id}-${ref.field}-${i}`}>
        <OriginalLanguage language={headlines.find(h=>h.evidence_id===ref.evidence_id)?.language ?? null}/>
        {ref.evidence_id.startsWith("bulletin:") ? <p className="muted">Conteo calculado por código sobre el snapshot; la tarjeta detalla entradas y método. No es un indicador externo ni mide independencia.</p> : null}
        <Citation refData={ref}/>
      </div>)}</section>
      <ValidationNote report={b.validation}/>
    </section>
  </div>;
}
