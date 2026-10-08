import type { Evidence, Generation, Sentence, Validation } from "./types";
export type Bulletin = {
  bulletin_id: string; sector: string; question: string; horizon: string;
  summary: Sentence[]; observations: Sentence[]; impact_hypotheses: Sentence[];
  related_sectors: string[]; analyst_questions: string[]; event_ids: string[];
  sources: Evidence[]; scope_disclaimer: string | null; limits_notice: string;
  validation: Validation; generated_by: Generation;
};
