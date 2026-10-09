import Link from "next/link";
import { Heading } from "@/components/shared";
export const metadata = {title: "Página no encontrada"};
export default function NotFound() { return <><Heading section="Error 404" title="Página no encontrada">El caso o la página no existe en este snapshot congelado. Los identificadores de caso tienen la forma EVT-0101.</Heading><div className="case-actions"><Link className="button" href="/">Volver a la Sala de Situación →</Link><Link className="button secondary" href="/consultas/">Buscar un caso →</Link></div></>; }
