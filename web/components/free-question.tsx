"use client";
import { useState } from "react";
import type { Answer, QA } from "@/lib/types";
import { APIError, postJSON } from "@/lib/api";
import { AnswerView } from "./answer-view";
export default function FreeQuestion({data}: {data: QA}) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [fallback, setFallback] = useState(false);
  const [mode, setMode] = useState<"evidence" | "online">("evidence");
  // Access code lives only in component memory: never in the URL, storage or telemetry.
  const [code, setCode] = useState("");
  const [elapsed, setElapsed] = useState<number | null>(null);
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !question.trim()) return;
    setBusy(true); setAnswer(null); setNotice(""); setFallback(false); setElapsed(null);
    const online = mode === "online";
    const started = performance.now();
    try {
      setAnswer(await postJSON<Answer>("/api/ask", online ? {question:question.trim(), mode:"online", access_code:code} : {question:question.trim()}));
      setElapsed(Math.round(performance.now() - started));
    }
    catch (error) {
      if (error instanceof APIError && error.status >= 400 && error.status < 500) setNotice(online && error.status === 403 ? `Acceso no autorizado a la IA en vivo: ${error.message}` : error.message);
      else if (online) setNotice("La IA en vivo no respondió. No se muestra ninguna respuesta en su lugar; prueba «Consulta con evidencia».");
      else {
        setFallback(true);
        // evidence mode only (online returned above): saved answers are labelled as such
        const exact = [...data.examples, ...data.jury].find(item=>item.question.toLocaleLowerCase("es") === question.trim().toLocaleLowerCase("es") && item.answer);
        setAnswer(exact?.answer ?? null);
        setNotice(exact ? "La API no está disponible. Mostramos la respuesta guardada para esta misma pregunta." : "La API no está disponible. Esta pregunta no tiene una respuesta guardada; puedes consultar los ejemplos de qa.json que aparecen abajo. No responden a tu pregunta libre.");
      }
    } finally { setBusy(false); }
  }
  return <section className="card" id="pregunta-libre"><p className="eyebrow">Consulta libre del snapshot</p><h2>Escribe tu pregunta</h2><p>Busca en el corpus público con citas o abstención. Por defecto se usan salidas de IA guardadas o una plantilla; cada respuesta indica su modo y modelo.</p><form onSubmit={submit}><fieldset className="mode-choice"><legend>Modo de respuesta</legend><label><input type="radio" name="qa-mode" checked={mode === "evidence"} onChange={()=>setMode("evidence")}/> Consulta con evidencia <span className="muted">(sin IA externa: evidencia citada o abstención)</span></label><label><input type="radio" name="qa-mode" checked={mode === "online"} onChange={()=>setMode("online")}/> IA generativa en vivo (Gemini) <span className="muted">(evaluadores autorizados)</span></label></fieldset>{mode === "online" ? <><p className="warning">Se envían a Google (Gemini) la pregunta y extractos de evidencia pública del snapshot; nada más. La respuesta pasa por los mismos validadores de citas y cifras. Si no hay evidencia suficiente, SCAYL se abstiene sin llamar al proveedor.</p><label htmlFor="access-code">Código de acceso</label><input id="access-code" type="password" autoComplete="off" value={code} onChange={e=>setCode(e.target.value)} maxLength={200} required/></> : null}<label htmlFor="question">Pregunta (hasta 300 caracteres)</label><textarea id="question" value={question} onChange={e=>setQuestion(e.target.value)} maxLength={300} required rows={3}/><p className="muted">{question.length}/300 caracteres</p><button className="button" disabled={busy || !question.trim() || (mode === "online" && !code)}>{busy ? (mode === "online" ? "Generando con Gemini…" : "Buscando evidencia…") : "Consultar"}</button></form><div aria-live="polite" aria-busy={busy}>{notice ? <p className="warning">{notice}</p> : null}{answer && mode === "online" && answer.generated_by.mode !== "online" ? <p className="warning">{answer.validation.issues.some(i=>i.code === "ONLINE_FALLBACK") ? "Gemini no pudo responder: se muestra la respuesta con evidencia (sin IA generativa)." : "Gemini no fue llamado: SCAYL se abstuvo o respondió con evidencia antes de generar."}{elapsed != null ? ` Tiempo total: ${elapsed} ms.` : ""}</p> : null}{answer && answer.generated_by.mode === "online" && elapsed != null ? <p className="muted">Tiempo total de la solicitud: {elapsed} ms.</p> : null}{answer ? <AnswerView answer={answer}/> : null}{fallback && !answer ? <div><h3>Respuestas guardadas disponibles</h3>{data.examples.map(item=><details className="citation" key={item.label}><summary>{item.question}</summary><AnswerView answer={item.answer}/></details>)}</div> : null}</div></section>;
}
