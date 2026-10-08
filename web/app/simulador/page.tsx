import {events} from "@/lib/data";
import meta from "@/public/data/meta.json";
import Simulator from "@/components/simulator";
export const metadata={title:"Simulador de pesos"};
export default function Page(){return <Simulator events={events()} official={meta.weights}/>;}
