import { events, qa } from "@/lib/data";
import Queries from "@/components/queries";
export const metadata = {title: "Consultas"};
export default function Page() { return <Queries data={qa()} events={events()}/>; }
