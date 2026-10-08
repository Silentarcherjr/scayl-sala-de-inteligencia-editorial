"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
const links = [["/", "Sala de Situación"], ["/consultas/", "Consultas"], ["/trust-lab/", "Trust Lab"], ["/simulador/", "Simulador"]];
export default function Nav() { const current = usePathname(); return <nav aria-label="Navegación principal">{links.map(([href, label]) => <Link key={href} href={href} aria-current={current === href ? "page" : undefined}>{label}</Link>)}</nav>; }
