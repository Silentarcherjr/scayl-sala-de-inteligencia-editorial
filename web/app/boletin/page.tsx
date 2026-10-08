import { readData, getCase } from "@/lib/data";
import type { Bulletin } from "@/lib/bulletin-types";
import BulletinView from "@/components/bulletin-view";
export const metadata = {title:"Boletín de entorno logístico · extensión bancaria"};
export default function Page() {
  const bulletin = readData<Bulletin[]>("bulletins.json").find(b=>b.sector==="logistica_canal");
  if (!bulletin) throw new Error("Falta el boletín CU-05 de logística");
  const cases = bulletin.event_ids.map(getCase);
  return <BulletinView bulletin={bulletin} claims={cases.flatMap(e=>e.claims)}
    headlines={cases.flatMap(e=>e.headlines.map(h=>({evidence_id:`news:${h.id_noticia}`,title:h.titulo,language:h.idioma})))}
    events={cases.map(e=>({event_id:e.event_id,title:e.title,synthetic:e.synthetic,
      language:e.headlines.find(h=>h.titulo===e.title)?.idioma ?? null}))}/>;
}
