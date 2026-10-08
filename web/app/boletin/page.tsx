import { readData, getCase } from "@/lib/data";
import type { Bulletin } from "@/lib/bulletin-types";
import BulletinView from "@/components/bulletin-view";
export const metadata = {title:"Boletín de entorno · extensión bancaria"};
export default function Page() {
  const bulletins = readData<Bulletin[]>("bulletins.json");
  const eventIds = [...new Set(bulletins.flatMap(b => b.event_ids))];
  const cases = eventIds.map(getCase);
  return <BulletinView bulletins={bulletins} claims={cases.flatMap(e => e.claims)}
    events={cases.map(e => ({event_id:e.event_id, title:e.title, synthetic:e.synthetic}))}/>;
}
