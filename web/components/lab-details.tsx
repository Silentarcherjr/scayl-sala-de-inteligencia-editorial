import { display, readable } from "@/lib/format";
export function DataDetails({value}: {value: unknown}) {
  if (value === null || value === undefined) return <span className="muted">no medido</span>;
  if (Array.isArray(value)) return value.length ? <ul className="text-list">{value.map((item,i)=><li key={i}><DataDetails value={item}/></li>)}</ul> : <span className="muted">Ninguno registrado</span>;
  if (typeof value === "object") return <dl style={{overflowWrap:"anywhere"}}>{Object.entries(value).map(([key,v])=><div key={key} style={{margin:"10px 0"}}><dt>{readable(key)}</dt><dd><DataDetails value={v}/></dd></div>)}</dl>;
  return <span>{display(value)}</span>;
}
