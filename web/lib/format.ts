export const display = (value: unknown): string => value == null ? "no disponible" : typeof value === "object" ? JSON.stringify(value) : String(value);
export const readable = (value: string) => value.replaceAll("_", " ");
export function panama(value: string | null): string {
  if (value == null) return "no disponible";
  const date = new Date(value);
  const parts = new Intl.DateTimeFormat("es-PA", {timeZone:"America/Panama", day:"numeric", month:"short", year:"numeric"}).formatToParts(date);
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find(p => p.type === type)?.value;
  const time = new Intl.DateTimeFormat("es-PA", {timeZone:"America/Panama", hour:"numeric", minute:"2-digit"}).format(date);
  return `${part("day")} ${part("month")} ${part("year")} · ${time}`;
}
export function safeUrl(value: string | null | undefined): string | null { if (!value) return null; try { const url = new URL(value); return ["http:", "https:"].includes(url.protocol) ? url.href : null; } catch { return null; } }
