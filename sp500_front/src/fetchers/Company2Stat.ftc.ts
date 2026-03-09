import { xfetch_back, type xFetch_Response } from "./GenericFetcher";


export type PriceInfo = {
    id: number,
    date: string,
    open: number,
    low: number,
    high: number,
    close: number,
    volume: number,
}

/**
 * @link /api/price/list?code=string
 * 
 * Retrieve all prices for a specific company, identified by its code.
 * [{
 *  id: number,
 *  date: string,
 *  open: number,
 *  low: number,
 *  high: number,
 *  close: number,
 *  volume: number,
 * },{
 *  id: number,
 *  date: string,
 *  open: number,
 *  low: number,
 *  high: number,
 *  close: number,
 *  volume: number,
 * },...]
 * @returns {PriceInfo[]}
 */
export function getAllPrices(companyId: string): Promise<xFetch_Response<PriceInfo[]>> {
    return xfetch_back<PriceInfo[]>(`/api/price/list?code=${companyId}`, {});
}