import ClaimChecker from "@/components/claim-checker";
import { Heading } from "@/components/shared";
export const metadata = {title: "Verificar una afirmación"};
export default function Page() { return <><Heading section="Contrastar con evidencia" title="Verificar una afirmación">Escribe una afirmación nueva y SCAYL la contrasta con el snapshot público: evidencia oficial frente a noticias, cifras, fechas, países y unidades. La decisión sigue siendo editorial.</Heading><ClaimChecker/></>; }
