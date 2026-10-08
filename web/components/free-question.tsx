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
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !question.trim()) return;
    setBusy(true); setAnswer(null); setNotice(""); setFallback(false);
    try { setAnswer(await postJSON<Answer>("/api/ask", {question:question.trim()})); }
    catch (error) {
      if (error instanceof APIError && error.status >= 400 && error.status < 500) setNotice(error.message);
      else {
        setFallback(true);
        const exact = [...data.examples, ...data.jury].find(item=>item.question.toLocaleLowerCase("es") === question.trim().toLocaleLowerCase("es") && item.answer);
        setAnswer(exact?.answer ?? null);
        setNotice(exact ? "La API no está disponible. Mostramos la respuesta guardada para esta misma pregunta." : "La API no está disponible. Esta pregunta no tiene una respuesta guardada; puedes consultar los ejemplos de qa.json que aparecen abajo. No responden a tu pregunta libre.");
      }
    } finally { setBusy(false); }
  }
  return <section className="card" id="pregunta-libre"><p className="eyebrow">Consulta libre del snapshot</p><h2>Escribe tu pregunta</h2><p>Busca en el corpus público con citas o abstención. Solo se utilizan salidas de IA guardadas o una plantilla; cada respuesta indica su modo y modelo.</p><form onSubmit={submit}><label htmlFor="question">Pregunta (hasta 300 caracteres)</label><textarea id="question" value={question} onChange={e=>setQuestion(e.target.value)} maxLength={300} required rows={3}/><p className="muted">{question.length}/300 caracteres</p><button className="button" disabled={busy || !question.trim()}>{busy ? "Buscando evidencia…" : "Consultar"}</button></form><div aria-live="polite" aria-busy={busy}>{notice ? <p className="warning">{notice}</p> : null}{answer ? <AnswerView answer={answer}/> : null}{fallback && !answer ? <div><h3>Respuestas guardadas disponibles</h3>{data.examples.map(item=><details className="citation" key={item.label}><summary>{item.question}</summary><AnswerView answer={item.answer}/></details>)}</div> : null}</div></section>;
}
