import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import Nav from "@/components/nav";
import { External } from "@/components/shared";
import meta from "@/public/data/meta.json";
import "./globals.css";
const inter = Inter({ subsets: ["latin"], display: "swap" });
export const metadata: Metadata = {title: {default: "SCAYL · Sala de Inteligencia Editorial", template: "%s · SCAYL"}, description: "De la señal a la decisión editorial. Evidencia trazable, prioridad explicable y revisión humana."};
export default function Layout({children}: Readonly<{children: React.ReactNode}>) { return <html lang="es"><body className={inter.className}><a className="skip" href="#contenido">Saltar al contenido</a><header className="header"><div className="header-inner"><Link href="/" className="brand">SCAYL<span>Sala de Inteligencia Editorial</span></Link><Nav/><span className="snapshot-pill">SNAPSHOT {meta.snapshot_version}</span></div></header><main id="contenido">{children}</main><footer><div><strong>SCAYL</strong><p>Snapshot {meta.snapshot_version} · Demo con salidas IA precalculadas (Qwen3 8B local) · modo cache</p></div><div className="footer-links"><External url="https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial">Repositorio</External><External url="https://scayl-demo.streamlit.app/">Versión Streamlit</External></div></footer></body></html>; }
