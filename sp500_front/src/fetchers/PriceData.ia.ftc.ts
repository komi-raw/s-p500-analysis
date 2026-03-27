import { BACK_IA_PORT } from "@/config/public-env";
import { xfetch_back, type xFetch_Response } from "./GenericFetcher";


export type IAResponse = {
    response: string,
}

export function askIAPrompt(company: string, data: any, prompt: string): Promise<xFetch_Response<IAResponse>> {
    return xfetch_back("/ask/companyinfo/data", {
        method: "POST",
        body: JSON.stringify({ prompt: `En sachant que l'entreprise étudiée est ${company}, que tu dois me donner une réponse brève ${Array.from(data).length === 0 ? "" : `et que tu disposes de ces informations boursières sur l'entreprise : ${JSON.stringify(data)}`}, réponds a ma question : ${prompt}` }),
    }, BACK_IA_PORT);
}