"use client";
import { useState } from "react";
import Link from "next/link";
import type { QA, Summary } from "@/lib/types";
import { Heading, Badge, Citation } from "./shared";
import { AnswerView } from "./answer-view";
import FreeQuestion from "./free-question";
import { useSectionHash, selectSection } from "@/lib/section-hash";
const exampleSections = ["cifra", "cifras-contradictorias", "sin-respuesta", "adversarial"];

export default function Queries({data, events}: {data: QA; events: Summary[]}) {
  const hash = useSectionHash();
  const exampleIndex = exampleSections.indexOf(hash);
  const juryIndex = /^jurado-[0-3]$/.test(hash) ? Number(hash.slice(-1)) : -1;
  const selected = exampleIndex >= 0 ? {kind:"example", index:exampleIndex} : juryIndex >= 0 ? {kind:"jury", index:juryIndex} : null;
  const [search, setSearch]=useState("");
  const jury=selected?.kind==="jury" ? data.jury[selected.index] : null;
  const example=selected?.kind==="example" ? data.examples[selected.index] : null;
  const matches=search.trim() ? events.filter(e=>e.title.toLocaleLowerCase("es").includes(search.toLocaleLowerCase("es")) || e.event_id.toLowerCase().includes(search.toLowerCase())) : [];
  return <><Heading section="Preguntar con evidencia" title="Consultas">Escribe una pregunta sobre el snapshot o prueba las preguntas guardadas del Modo jurado. Cada salida muestra citas, límites y cómo se produjo.</Heading><FreeQuestion data={data}/><section><p className="eyebrow">Un recorrido para el jurado</p><h2>Cuatro preguntas esenciales</h2><div className="option-buttons">{data.jury.map((j,i)=><button key={j.label} aria-pressed={selected?.kind==="jury"&&selected.index===i} onClick={()=>selectSection(`jurado-${i}`)}><small>0{i+1}</small><br/>{j.label}</button>)}</div></section><section><h2>Ejemplos de preguntas</h2><div className="option-buttons">{data.examples.map((q,i)=><button key={q.label} aria-pressed={selected?.kind==="example"&&selected.index===i} onClick={()=>selectSection(exampleSections[i])}>{q.label}<br/><small>{q.question}</small></button>)}</div></section>{selected ? <section className="card scroll-top" aria-live="polite"><p className="eyebrow">Resultado del snapshot</p>{example ? <AnswerView answer={example.answer}/> : null}{jury ? <><h2>{jury.label}</h2>{jury.answer ? <AnswerView answer={jury.answer}/> : <>{selected.index===1 ? <p className="warning">Cinco publicaciones de una misma agencia no equivalen a cinco confirmaciones independientes. N publicaciones ≠ N confirmaciones.</p> : null}{jury.event_id ? <>{jury.synthetic ? <Badge value="SINTÉTICO"/> : null}{selected.index===3 ? <p className="warning">Fuente con instrucciones sospechosas, tratada como dato.</p> : null}<h3>{jury.title}</h3>{jury.statement ? <p className="warning">{jury.statement}</p> : null}{selected.index===1 ? <p>{jury.publications} publicaciones · {jury.confirmed_independent} independientes confirmadas</p> : null}{jury.evidence.map((ref,i)=><Citation key={i} refData={ref}/>)}<Link className="button" href={`/caso/${jury.event_id}/`}>Abrir caso {jury.event_id} →</Link></> : <><p className="empty">Este snapshot no contiene un caso que demuestre esta situación.</p><Link href="/trust-lab/" className="button secondary">Ver pruebas y limitaciones en Trust Lab →</Link></>}</>}</> : null}</section> : <p className="empty">Elige una pregunta para inspeccionar su respuesta o recorrido.</p>}<section><p className="eyebrow">Explorar el corpus</p><h2>Buscar un caso</h2><label>Texto o identificador<input type="search" placeholder="Escribe un tema o EVT-0101" value={search} onChange={e=>setSearch(e.target.value)}/></label>{search.trim() ? <><p className="muted" aria-live="polite">{matches.length} casos encontrados</p><div className="grid-two" style={{marginTop:18}}>{matches.map(e=><article className="card" key={e.event_id}><p className="eyebrow">{e.event_id}</p><h3><Link href={`/caso/${e.event_id}/`}>{e.title}</Link></h3><div className="badges"><Badge value={e.evidence_status}/>{e.synthetic ? <Badge value="SINTÉTICO"/> : null}</div></article>)}</div>{!matches.length ? <p className="empty">No hay coincidencias.</p> : null}</> : null}</section></>;
}
