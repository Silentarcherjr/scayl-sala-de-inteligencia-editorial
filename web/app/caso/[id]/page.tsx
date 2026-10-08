import { events, getCase } from "@/lib/data";
import meta from "@/public/data/meta.json";
import CaseView from "@/components/case-view";
export function generateStaticParams() { return events().map(e => ({id:e.event_id})); }
export const dynamicParams = false;
export async function generateMetadata({params}: {params: Promise<{id: string}>}) { const {id}=await params;return {title:getCase(id).title}; }
export default async function CasePage({params}: {params: Promise<{id: string}>}) { const {id}=await params;return <CaseView event={getCase(id)} weights={meta.weights}/>; }
