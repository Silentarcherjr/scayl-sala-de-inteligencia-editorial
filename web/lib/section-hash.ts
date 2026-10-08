"use client";
import { useSyncExternalStore } from "react";
function subscribe(listener: () => void) {
  window.addEventListener("hashchange", listener);
  return () => window.removeEventListener("hashchange", listener);
}
function snapshot() { return window.location.hash.slice(1); }
function serverSnapshot() { return ""; }
export function useSectionHash() { return useSyncExternalStore(subscribe, snapshot, serverSnapshot); }
export function selectSection(section: string) {
  window.history.replaceState(null, "", `#${section}`);
  window.dispatchEvent(new Event("hashchange"));
}
