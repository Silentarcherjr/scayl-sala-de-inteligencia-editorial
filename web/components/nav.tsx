"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
const links = [["/recorrido/", "Empieza aquí"], ["/", "Sala de Situación"], ["/consultas/", "Consultas"], ["/trust-lab/", "Pruebas y métricas"], ["/simulador/", "Simulador"], ["/boletin/", "Boletín (banca)"]];
export default function Nav() { const current = usePathname(); return <nav aria-label="Navegación principal">{links.map(([href, label]) => <Link key={href} href={href} aria-current={current === href ? "page" : undefined}>{label}</Link>)}</nav>; }
