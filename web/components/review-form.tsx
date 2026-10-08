"use client";
import { useEffect, useState } from "react";
import { APIError, postJSON } from "@/lib/api";
import { panama, readable } from "@/lib/format";
type State = "nuevo" | "en_revision" | "requiere_evidencia" | "aprobado_como_borrador" | "descartado";
type Receipt = {rawJSON?:string; review:{review_id:string; event_id:string; from_state:State; to_state:State; reviewer:string; justification:string; decided_at:string}; receipt_sha256:string; note:string};
// UI choices mirror REVIEW_TRANSITIONS; the Python endpoint remains authoritative.
const transitions: Record<State, State[]> = {nuevo:["en_revision"], en_revision:["requiere_evidencia","aprobado_como_borrador","descartado"], requiere_evidencia:["en_revision"], aprobado_como_borrador:["en_revision"], descartado:["en_revision"]};
const storageNotice = "Registro de esta demo en tu navegador; en la redacción iría a su base de datos";
function validHistory(value: unknown, eventId: string): value is Receipt[] {
  return Array.isArray(value) && value.every(row=>row && row.review?.event_id===eventId && typeof row.review.review_id==="string" && Object.hasOwn(transitions,row.review.to_state) && Object.hasOwn(transitions,row.review.from_state) && typeof row.receipt_sha256==="string");
}
export default function ReviewForm({eventId}: {eventId: string}) {
  const storageKey = `scayl:review:v1:${eventId}`;
  const [history, setHistory] = useState<Receipt[]>([]);
  const [ready, setReady] = useState(false);
  const [destination, setDestination] = useState<State | "">("");
  const [reviewer, setReviewer] = useState("");
  const [justification, setJustification] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const state: State = history.at(-1)?.review.to_state ?? "nuevo";
  const allowed = transitions[state];
  const toState = destination && allowed.includes(destination) ? destination : allowed[0];
  useEffect(()=>{
    const load = () => {
      try { const raw=localStorage.getItem(storageKey); const parsed:unknown=raw ? JSON.parse(raw) : []; if (!validHistory(parsed,eventId)) throw Error(); setHistory(parsed); }
      catch { setMessage("No se pudo leer el historial local. Puedes registrar una nueva revisión y descargar el recibo."); }
      setReady(true);
    };
    const frame=requestAnimationFrame(load);
    const onStorage=(event:StorageEvent)=>{if(event.key===storageKey) load();};
    window.addEventListener("storage",onStorage);
    return ()=>{cancelAnimationFrame(frame); window.removeEventListener("storage",onStorage);};
  },[eventId, storageKey]);
  function download(receipt: Receipt) {
    const url=URL.createObjectURL(new Blob([receipt.rawJSON ?? JSON.stringify(receipt,null,2)],{type:"application/json"}));
    const anchor=document.createElement("a"); anchor.href=url; anchor.download=`${receipt.review.review_id}.json`; anchor.click(); URL.revokeObjectURL(url);
  }
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (busy || !ready) return;
    setBusy(true); setMessage("");
    try {
      // Guard against a concurrent review in another tab before sending from_state.
      let raw:string | null=null;
      try { raw=localStorage.getItem(storageKey); } catch { /* A downloadable receipt still works when storage is disabled. */ }
      if (raw) { const stored:unknown=JSON.parse(raw); if (!validHistory(stored,eventId) || stored.at(-1)?.review.review_id !== history.at(-1)?.review.review_id) { if (validHistory(stored,eventId)) setHistory(stored); throw Error("El historial cambió en otra pestaña. Revisa el estado y vuelve a enviar."); } }
      let rawJSON="";
      const receipt=await postJSON<Receipt>("/api/review",{event_id:eventId,from_state:state,to_state:toState,reviewer:reviewer.trim(),justification:justification.trim()}, raw=>{rawJSON=raw;});
      const updated=[...history,{...receipt,rawJSON}]; setHistory(updated); setDestination(""); setJustification("");
      try { localStorage.setItem(storageKey,JSON.stringify(updated)); setMessage("Decisión registrada en este navegador. Puedes descargar su recibo JSON."); }
      catch { setMessage("La API validó la decisión, pero el navegador no pudo guardarla. Descarga el recibo antes de salir."); }
    } catch(error) { setMessage(error instanceof APIError ? error.message : error instanceof TypeError || (error instanceof DOMException && error.name === "TimeoutError") ? "No se pudo conectar con la API. No se registró una nueva decisión; vuelve a intentarlo cuando haya conexión." : error instanceof Error ? error.message : "No se pudo validar la revisión. No se registró una nueva decisión."); }
    finally { setBusy(false); }
  }
  return <article className="card"><h2>Revisión humana</h2><p className="warning">{storageNotice}</p><p className="warning">Aprobado como borrador NO significa publicado.</p><p>La API valida la transición y genera un recibo con hashes de la evidencia y del paquete mostrado. El nombre identifica a quien revisa en esta demo; no es una autenticación.</p><p><strong>Estado en este navegador:</strong> {readable(state)}</p><form onSubmit={submit}><label htmlFor="review-state">Nuevo estado</label><select id="review-state" value={toState} onChange={e=>setDestination(e.target.value as State)}>{allowed.map(value=><option key={value} value={value}>{readable(value)}</option>)}</select><label htmlFor="reviewer">Persona revisora</label><input id="reviewer" value={reviewer} onChange={e=>setReviewer(e.target.value)} maxLength={100} required/><label htmlFor="justification">Justificación obligatoria (hasta 500 caracteres)</label><textarea id="justification" value={justification} onChange={e=>setJustification(e.target.value)} maxLength={500} required rows={4}/><p className="muted">{justification.length}/500 caracteres</p><button className="button" disabled={!ready || busy || !reviewer.trim() || !justification.trim()}>{busy ? "Validando decisión…" : "Registrar revisión"}</button></form><p role="status" aria-live="polite">{message}</p><h3>Historial de esta demo</h3>{history.length ? history.map(receipt=><article className="citation" key={receipt.review.review_id}><p><strong>{readable(receipt.review.from_state)} → {readable(receipt.review.to_state)}</strong></p><p>{receipt.review.reviewer} · {panama(receipt.review.decided_at)} Panamá</p><p>{receipt.review.justification}</p><button className="button secondary" onClick={()=>download(receipt)}>Descargar recibo JSON</button></article>) : <p className="muted">Aún no hay decisiones registradas en este navegador.</p>}</article>;
}
