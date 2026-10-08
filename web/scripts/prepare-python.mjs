// Copy only runtime code and approved public artifacts; never expose them in out/.
import { cpSync, mkdirSync, rmSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
const web = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repo = path.resolve(web, "..");
const dest = path.join(web, ".python-runtime");
const bundle = JSON.parse(readFileSync(path.join(repo, "deploy/artifacts/v1/bundle.public.json"), "utf8"));
function check(value) {
  if (Array.isArray(value)) value.forEach(check);
  else if (value && typeof value === "object") {
    if (value.descripcion != null) throw Error("Public bundle contains descripcion");
    Object.values(value).forEach(check);
  }
}
check(bundle);
rmSync(dest, {recursive:true, force:true});
mkdirSync(path.join(dest,"data/processed/v1"), {recursive:true});
cpSync(path.join(repo,"scayl"),path.join(dest,"scayl"), {recursive:true, filter: src => !src.includes("__pycache__") && !src.endsWith(".pyc")});
cpSync(path.join(repo,"deploy/artifacts/v1/bundle.public.json"),path.join(dest,"data/processed/v1/bundle.json"));
cpSync(path.join(repo,"deploy/artifacts/v1/llm"),path.join(dest,"llm"), {recursive:true, filter: src => !src.includes("__pycache__")});
console.log("Python runtime: scayl + public bundle + public cache only");
