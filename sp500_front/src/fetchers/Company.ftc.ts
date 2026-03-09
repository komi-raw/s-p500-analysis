import { xfetch_back, type xFetch_Response } from "./GenericFetcher";


export type CompanyID = {
    id: number,
    code: string
}

/**
 * @link /api/company/list
 * 
 * Retrieve all the company codes with their id in the following format.
 * [{
 *  id: 1,
 *  code: AFB
 * },{
 *  id: 2,
 *  code: ACD
 * },...]
 * @returns {CompanyID[]}
 */
export function getAllCompanies(): Promise<xFetch_Response<CompanyID[]>> {
    return xfetch_back("/api/company/list", {});
}

/**
 * @link /api/company/info
 * 
 * Retrieve all the company codes with their id in the following format.
 * [{
 *  id: 1,
 *  code: AFB
 * },{
 *  id: 2,
 *  code: ACD
 * },...]
 * @returns {CompanyID[]}
 */
export function getCompanyInfo(code: string): Promise<xFetch_Response<any>> {
    return xfetch_back(`/api/company/info?code=${code}`, {});
}
