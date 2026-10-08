import type { Answer } from "@/lib/types";
import { GenerationNote, ValidationNote, TextList } from "./shared";
import Sentences from "./sentences";
export function AnswerView({answer}: {answer: Answer}) { return <><GenerationNote meta={answer.generated_by}/><h3>{answer.question}</h3>{answer.abstained ? <><p className="warning"><strong>No hay evidencia suficiente en el corpus</strong><br/>{answer.abstention_reason ?? "Motivo no disponible."}</p><h3>Información necesaria</h3><TextList items={answer.needed_information}/></> : <Sentences sentences={answer.answer} citations={answer.citations}/>}<ValidationNote report={answer.validation}/></>; }
