"use client";
import { useState } from "react";
import { APIError, postJSON } from "@/lib/api";
import { External } from "./shared";

type Cite = {evidence_id: string; fuente: string; tipo: "oficial" | "noticia"; url: string | null; campo: string; periodo: string | null; valor: unknown; extracto: string};
type Finding = {relacion: "coincide" | "difiere" | "contexto"; nota: string; evidencia: Cite};
type Result = {afirmacion: string; estado: string; estado_etiqueta: string; explicacion: string; hallazgos: Finding[]; por_comprobar: string[]; detectado: {cifras?: number[]; periodos?: string[]; paises?: string[]; unidad?: string | null; pide_dato_actual?: boolean}; alcance: string; metodo: string; modo: string};

const examples = ["El nivel del lago Gatún era de 90 pies el 29 de septiembre de 2026", "La inflación interanual de Panamá fue de 2,2% en agosto de 2026", "Hubo un sismo de magnitud 4.7 en Chiriquí el 16 de julio de 2026", "El Canal de Panamá aumentará a 33 los cupos diarios de tránsito"];
const relationLabel = {coincide: "Coincide", difiere: "Difiere", contexto: "Contexto (no se compara)"};
const tone: Record<string, string> = {compatible_oficial: "suficiente", discrepancia_oficial: "insuficiente", discrepancia_reportada: "insuficiente", solo_reportado: "parcial", no_comparable: "parcial", evidencia_insuficiente: "insuficiente", abstencion_inyeccion: "insuficiente"};

function show(value: unknown) { return value === null || value === undefined || value === "" ? "no disponible" : typeof value === "number" ? String(Math.round(value * 100) / 100) : String(value); }

export default function ClaimChecker() {
  const [claim, setClaim] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !claim.trim()) return;
    setBusy(true); setResult(null); setNotice("");
    try { setResult(await postJSON<Result>("/api/check", {claim: claim.trim()})); }
    catch (error) { setNotice(error instanceof APIError && error.status < 500 ? error.message : "El verificador no está disponible (requiere la API del sitio publicado o la app local). No se muestra ningún resultado inventado."); }
    finally { setBusy(false); }
  }
  const d = result?.detectado;
  return <section className="card">
    <p className="eyebrow">Verificador editorial de afirmaciones</p>
    <h2>Escribe una afirmación con una cifra</h2>
    <p>SCAYL busca evidencia en el snapshot público y compara cifra, período, país y unidad. <strong>No declara verdadero ni falso</strong>: muestra lo compatible, lo que difiere y lo que falta comprobar. Sin IA generativa: recuperación y reglas deterministas.</p>
    <form onSubmit={submit}>
      <label htmlFor="claim">Afirmación (12 a 300 caracteres)</label>
      <textarea id="claim" value={claim} onChange={e=>setClaim(e.target.value)} maxLength={300} required rows={3}/>
      <p className="muted">{claim.length}/300 caracteres · Ejemplos: {examples.map((x, i) => <button type="button" key={x} className="link-button" onClick={()=>setClaim(x)}>{i ? " · " : ""}«{x}»</button>)}</p>
      <button className="button" disabled={busy || claim.trim().length < 12}>{busy ? "Buscando evidencia…" : "Verificar"}</button>
    </form>
    <div aria-live="polite" aria-busy={busy}>
      {notice ? <p className="warning">{notice}</p> : null}
      {result ? <article className="citation" style={{marginTop: 16}}>
        <p><span className={`badge evidence ${tone[result.estado] ?? "parcial"}`}>{result.estado_etiqueta}</span> <span className="muted">{result.modo}</span></p>
        <p style={{marginTop: 8}}>{result.explicacion}</p>
        {d && Object.keys(d).length ? <p className="muted">Detectado en la afirmación — cifras: {d.cifras?.length ? d.cifras.join(", ") : "ninguna"} · períodos: {d.periodos?.length ? d.periodos.join(", ") : "ninguno"} · países: {d.paises?.length ? d.paises.join(", ") : "ninguno"} · unidad: {d.unidad ?? "no identificada"}{d.pide_dato_actual ? " · pide un dato actual" : ""}</p> : null}
        {result.hallazgos.length ? <><h3>Evidencia</h3>{result.hallazgos.map((f, i) => <details className="citation" key={i} open={f.relacion !== "contexto"}>
          <summary><strong>{relationLabel[f.relacion]}</strong> · {f.evidencia.tipo === "oficial" ? "Evidencia primaria oficial" : "Noticia (declaración periodística)"} · {f.evidencia.fuente} · {f.nota}</summary>
          <dl><dt>Identificador</dt><dd>{f.evidencia.evidence_id}</dd><dt>Fuente</dt><dd>{f.evidencia.fuente}</dd><dt>Campo</dt><dd>{f.evidencia.campo}</dd><dt>Valor</dt><dd>{show(f.evidencia.valor)}</dd><dt>Período</dt><dd>{show(f.evidencia.periodo)}</dd><dt>Extracto</dt><dd>{f.evidencia.extracto}</dd><dt>URL</dt><dd>{f.evidencia.url ? <External url={f.evidencia.url}>{f.evidencia.url}</External> : "no disponible"}</dd></dl>
        </details>)}</> : null}
        <h3>Qué falta comprobar</h3><ul className="text-list">{result.por_comprobar.map(x=><li key={x}>{x}</li>)}</ul>
        <p className="warning">{result.alcance}</p>
        <p className="muted">Método: {result.metodo}</p>
      </article> : null}
    </div>
  </section>;
}
