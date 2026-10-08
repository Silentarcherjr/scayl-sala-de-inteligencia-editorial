import {keys, type Key, type Summary} from "./types";
// Round the exact IEEE-754 input to one decimal, ties to even, like Python round(x, 1).
// Avoid Math.round's different tie behavior; all scores are finite and nonnegative.
export function pythonRound1(value: number): number {
  if(value===0)return 0;
  const view=new DataView(new ArrayBuffer(8));view.setFloat64(0,value);
  const bits=view.getBigUint64(0);const exponent=Number((bits>>52n)&2047n)-1023-52;
  const mantissa=(bits&((1n<<52n)-1n))+(1n<<52n);
  const numerator=mantissa*10n*(exponent>0 ? 1n<<BigInt(exponent) : 1n);
  const denominator=exponent<0 ? 1n<<BigInt(-exponent) : 1n;
  const integer=numerator/denominator;const remainder=numerator%denominator;
  const up=remainder*2n>denominator || (remainder*2n===denominator && integer%2n!==0n);
  return Number(integer+(up ? 1n : 0n))/10;
}
export function simulate(events: Summary[], weights: Record<Key,number>) {
  return events.map(event=>({event,score:pythonRound1(keys.reduce((sum,k)=>sum+weights[k]*event.priority.components[k],0))})).sort((a,b)=>b.score-a.score || b.event.priority.components.U-a.event.priority.components.U || (a.event.event_id<b.event.event_id ? -1 : a.event.event_id>b.event.event_id ? 1 : 0));
}
export function adjust(weights: Record<Key,number>,key:Key,value:number):Record<Key,number> {
  const next={...weights,[key]:value};let delta=value-weights[key];
  for(const other of keys.filter(k=>k!==key)) { if(delta>0){const take=Math.min(delta,next[other]);next[other]-=take;delta-=take;}else if(delta<0){const add=Math.min(-delta,100-next[other]);next[other]+=add;delta+=add;} }
  return next;
}
