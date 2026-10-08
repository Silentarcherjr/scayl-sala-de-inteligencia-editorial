// Same-origin only; static/offline exports deliberately have no API.
export class APIError extends Error { constructor(message: string, public status: number) { super(message); } }
export async function postJSON<T>(path: "/api/ask" | "/api/review", body: object, receiveRaw?: (json: string) => void): Promise<T> {
  const response = await fetch(path, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body), signal:AbortSignal.timeout(30000), cache:"no-store"});
  const raw = await response.text();
  const data = JSON.parse(raw);
  if (!response.ok) throw new APIError(typeof data.error === "string" ? data.error : "La API no pudo completar la solicitud.", response.status);
  receiveRaw?.(raw);
  return data as T;
}
