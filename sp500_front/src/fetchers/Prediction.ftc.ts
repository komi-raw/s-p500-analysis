import { xfetch_back, type xFetch_Response } from "./GenericFetcher";

export type PredictionStep = {
    step: number;
    predicted_close: number;
    estimated_date?: string;
};

export type PredictionResult = {
    ticker: string;
    prediction_mode: string;
    context_length: number;
    prediction_length: number;
    last_known_close: number;
    last_known_date: string;
    predictions: PredictionStep[];
};

/**
 * @link /api/prediction/?code=string
 *
 * Fetch ML price predictions for a given ticker.
 */
export function getPrediction(code: string, steps?: number): Promise<xFetch_Response<PredictionResult>> {
    const url = steps ? `/api/prediction/?code=${code}&steps=${steps}` : `/api/prediction/?code=${code}`;
    return xfetch_back<PredictionResult>(url, null);
}
