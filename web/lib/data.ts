import fs from "node:fs";
import path from "node:path";
import type { Case, Summary, QA } from "./types";
export function readData<T>(file: string): T { return JSON.parse(fs.readFileSync(path.join(process.cwd(), "public/data", file), "utf8")) as T; }
export const events = () => readData<Summary[]>("events.json");
export const getCase = (id: string) => readData<Case>(`cases/${id}.json`);
export const qa = () => readData<QA>("qa.json");
