export const display = (value: unknown): string => value == null ? "no disponible" : typeof value === "object" ? JSON.stringify(value) : String(value);
export const readable = (value: string) => value.replaceAll("_", " ");
export function panama(value: string | null): string { return value == null ? "no disponible" : new Intl.DateTimeFormat("es-PA", {timeZone: "America/Panama", dateStyle: "medium", timeStyle: "short"}).format(new Date(value)); }
export function safeUrl(value: string | null | undefined): string | null { if (!value) return null; try { const url = new URL(value); return ["http:", "https:"].includes(url.protocol) ? url.href : null; } catch { return null; } }
