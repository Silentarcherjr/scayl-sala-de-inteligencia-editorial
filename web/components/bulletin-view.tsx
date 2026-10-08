"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import type { Bulletin } from "@/lib/bulletin-types";
import type { Claim } from "@/lib/types";
import { Heading, Badge, Citation, GenerationNote, ValidationNote, TextList } from "./shared";
import Sentences from "./sentences";
const sectorLabels: Record<string,string> = {logistica_canal:"Logística y Canal", economia:"Economía"};
export default function BulletinView({bulletins, claims, events}: {
  bulletins: Bulletin[]; claims: Claim[]; events: {event_id:string;title:string;synthetic:boolean}[];
}) {
  const [sector, setSector] = useState(bulletins[0].sector);
  const b = bulletins.find(item => item.sector === sector)!;
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
  return <div className="bank-page" ref={root}><Heading section="Extensión bancaria · boletín de entorno" title="Boletín de entorno sectorial">El mismo núcleo de evidencia para un analista de estudios económicos o riesgo sectorial. SCAYL mantiene su modalidad editorial; este boletín es una extensión.</Heading><div className="bank-print-controls filters"><label>Seleccionar boletín<select value={sector} onChange={e => setSector(e.target.value)}>{bulletins.map(item => <option key={item.sector} value={item.sector}>{sectorLabels[item.sector] ?? item.sector}</option>)}</select></label><button className="button" onClick={()=>window.print()}>Imprimir / guardar PDF</button></div><section aria-label="Boletín seleccionado" key={b.bulletin_id}><div className="warning bank-limits"><strong>Alcance del boletín</strong><p>{b.limits_notice}</p></div><p className="eyebrow">{b.bulletin_id} · {sectorLabels[b.sector]}</p><h2>{b.question}</h2><p><strong>Usuario:</strong> Analista de estudios económicos o riesgo sectorial</p><p><strong>Horizonte temporal:</strong> {b.horizon}</p><GenerationNote meta={b.generated_by}/>{b.scope_disclaimer ? <p className="warning">{b.scope_disclaimer}</p> : null}<article className="card"><h2>Resumen</h2><Sentences sentences={b.summary} claims={claims} citations={b.sources}/></article><section className="grid-two bank-columns"><article className="card"><p className="eyebrow">Lo que dicen las fuentes</p><h2>Observación</h2><p className="muted">Las declaraciones conservan atribución. Los indicadores aportan contexto de su período; no confirman por sí solos los titulares.</p><Sentences sentences={b.observations} claims={claims} citations={b.sources}/></article><article className="card bank-hypotheses"><p className="eyebrow">Posibilidades que deben comprobarse</p><h2>Hipótesis de impacto</h2><p className="warning">HIPÓTESIS · requieren verificación. No son hechos observados ni pronósticos.</p><Sentences sentences={b.impact_hypotheses} claims={claims} citations={b.sources}/></article></section><section className="card"><h2>Sectores potencialmente relacionados</h2><div className="badges">{b.related_sectors.map(item => <Badge key={item} value={item}/>)}</div><h2>Tres preguntas para el analista</h2><TextList items={b.analyst_questions}/></section><section className="card"><h2>Eventos usados</h2><p className="muted">Seleccionados en el orden de prioridad oficial; no se calcula un puntaje bancario.</p><ol className="text-list">{b.event_ids.map(id => {const e = events.find(item=>item.event_id===id);return <li key={id}><Link href={`/caso/${id}/`}>{id} · {e?.title ?? "Título no disponible"}</Link>{e?.synthetic ? <Badge value="SINTÉTICO"/> : null}</li>;})}</ol></section><section><h2>Fuentes y períodos</h2>{b.sources.map((ref,i)=><Citation key={`${ref.evidence_id}-${ref.field}-${i}`} refData={ref}/>)}</section><ValidationNote report={b.validation}/></section></div>;
}
