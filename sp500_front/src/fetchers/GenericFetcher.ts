import { BACK_DOMAIN, BACK_PORT } from "@/config/public-env";
export type NOK = 1;
export const NOK = 1;
export type OK = 0;
export const OK = 0;

export type xFetch_Response<T> = {
    status: NOK | OK,
    reason? : any,
    data : T
}


export function xfetch_back<T>(url: string, args: RequestInit | null = null, port : string = BACK_PORT): Promise<xFetch_Response<T>> {
    const xUrl = new URL(url, BACK_DOMAIN);
    xUrl.port = port;
    return new Promise<xFetch_Response<T>>(async (resolve, reject) => {
        try {
            const response = args ? await fetch(xUrl, args) : await fetch(xUrl);
            if(!response.ok){
                throw new Error("Response is not ok.")
            }
            const json = await response.json();
            const statusResponse: xFetch_Response<T> = {status: OK, data: json}
            resolve(statusResponse);
        } catch(exception){
            const statusResponse: xFetch_Response<T> = {status: NOK, reason: exception, data: null as T}
            reject(statusResponse)
        }
    });
}
