<script setup lang="ts">
import { getAllCompanies, type CompanyID } from "@/fetchers/Company.ftc";
import { getAllPrices } from "@/fetchers/Company2Stat.ftc";
import { getPrediction, type PredictionResult } from "@/fetchers/Prediction.ftc";
import { ChartDefault } from "@/objects/ChartCM";
import { CandlestickSeries, LineSeries } from "lightweight-charts";
import { onBeforeMount, onMounted, ref } from "vue";

const loading = ref(true);
const predicting = ref(false);
const currentCompany = ref("");
const companies = ref<CompanyID[]>([]);
const predictionResult = ref<PredictionResult | null>(null);
const errorMsg = ref("");
const stepsInput = ref<number>(10);

let chart: any = null;
let predictionSeries: any = null;

onBeforeMount(() => {
    getAllCompanies()
        .then((res) => {
            companies.value = Array.from(res.data);
            loading.value = false;
        })
        .catch(() => {
            loading.value = false;
        });
});

onMounted(() => {
    chart = new ChartDefault("prediction-chart", CandlestickSeries);

    predictionSeries = chart.chart.addSeries(LineSeries);
    predictionSeries.applyOptions({ color: "rgb(74, 222, 128)", lineWidth: 2, lineStyle: 1 });
});

async function corpChanged(val: any) {
    currentCompany.value = val.target.value;
    predictionResult.value = null;
    errorMsg.value = "";
    chart.registerData([]);
    predictionSeries.setData([]);
}

async function runPrediction() {
    if (!currentCompany.value) return;
    predicting.value = true;
    errorMsg.value = "";

    try {
        const [pricesRes, predRes] = await Promise.all([
            getAllPrices(currentCompany.value),
            getPrediction(currentCompany.value, stepsInput.value),
        ]);

        predictionResult.value = predRes.data;

        // Historique en bougies (64 derniers points)
        const raw = Array.from(pricesRes.data)
            .map((d) => ({
                time: Math.floor(new Date(d.date).getTime() / 1000),
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close,
            }))
            .sort((a, b) => a.time - b.time);

        const deduped = Array.from(new Map(raw.map((p) => [p.time, p])).values());
        const historical = deduped.slice(-predRes.data.context_length);
        chart.registerData(historical);

        // Prédictions en ligne verte
        const lastTime = historical[historical.length - 1]?.time ?? 0;
        const interval =
            historical.length > 1
                ? historical[historical.length - 1].time - historical[historical.length - 2].time
                : 86400;

        const predPoints = predRes.data.predictions.map((p, i) => ({
            time: lastTime + interval * (i + 1),
            value: p.predicted_close,
        }));

        predictionSeries.setData(predPoints);
        chart.fitContent();
    } catch (e: any) {
        errorMsg.value = e?.reason?.message ?? "Erreur lors de la prédiction.";
    } finally {
        predicting.value = false;
    }
}
</script>

<template>
    <div v-if="loading" class="loader absolute z-10 mainSubject w-full flex justify-center items-center">
        <span class="spinner">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z" opacity=".25" />
                <path d="M12,4a8,8,0,0,1,7.89,6.7A1.53,1.53,0,0,0,21.38,12h0a1.5,1.5,0,0,0,1.48-1.75,11,11,0,0,0-21.72,0A1.5,1.5,0,0,0,2.62,12h0a1.53,1.53,0,0,0,1.49-1.3A8,8,0,0,1,12,4Z">
                    <animateTransform attributeName="transform" type="rotate" dur="0.75s" values="0 12 12;360 12 12" repeatCount="indefinite" />
                </path>
            </svg>
        </span>
    </div>

    <section class="mainSubject flex flex-row">
        <div style="width: 60%" id="prediction-chart"></div>

        <div style="width: 40%" class="overflow-scroll bg-accent pl-5 pr-5 pt-2 pb-6 flex flex-col gap-2.5">
            <div class="row self-center">
                <h3>ML Prediction</h3>
            </div>

            <!-- Sélecteur entreprise -->
            <div class="row self-start">
                <div class="pl-1 pb-1 pr-1" style="background-color: #202020; border-radius: 5px;">
                    <span>Company : </span>
                    <select @change="corpChanged" name="corp">
                        <option value="">-- Choisir --</option>
                        <option v-for="company in companies" :key="company.code" :value="company.code">
                            {{ company.code }}
                        </option>
                    </select>
                </div>
            </div>

            <!-- Nombre de jours -->
            <div class="row self-start">
                <div class="pl-1 pb-1 pr-1" style="background-color: #202020; border-radius: 5px;">
                    <span class="mr-2">Jours à prédire : </span>
                    <input
                        v-model.number="stepsInput"
                        type="number"
                        min="1"
                        max="200"
                        style="width: 60px; background: #333; border: 1px solid #555; border-radius: 3px; padding: 2px 6px; color: #DDD;"
                    />
                </div>
            </div>

            <!-- Bouton prédire -->
            <div class="row self-start">
                <button
                    @click="runPrediction"
                    :disabled="!currentCompany || predicting"
                    style="background-color: #202020; border-radius: 5px; padding: 4px 12px; cursor: pointer;"
                    :style="{ opacity: !currentCompany || predicting ? '0.5' : '1' }"
                >
                    {{ predicting ? "Prédiction en cours..." : "Lancer la prédiction" }}
                </button>
            </div>

            <!-- Légende -->
            <div class="row self-start flex flex-col gap-1">
                <div class="flex items-center gap-2">
                    <span style="display:inline-block; width:20px; height:12px; background: rgb(54,116,217); border-radius:2px;"></span>
                    <span style="font-size: 0.8em;">Historique bougies (64 derniers)</span>
                </div>
                <div class="flex items-center gap-2">
                    <span style="display:inline-block; width:20px; height:3px; background: rgb(74,222,128);"></span>
                    <span style="font-size: 0.8em;">Prédiction ML</span>
                </div>
            </div>

            <!-- Erreur -->
            <div v-if="errorMsg" class="row self-start" style="color: rgb(225,50,85); font-size: 0.85em;">
                {{ errorMsg }}
            </div>

            <!-- Résultats -->
            <template v-if="predictionResult">
                <div class="row self-start">
                    <div class="pl-1 pb-1 pr-1" style="background-color: #202020; border-radius: 5px;">
                        <span class="mr-3">Ticker : </span>
                        <span>{{ predictionResult.ticker }}</span>
                    </div>
                </div>
                <div class="row self-start">
                    <div class="pl-1 pb-1 pr-1" style="background-color: #202020; border-radius: 5px;">
                        <span class="mr-3">Mode : </span>
                        <span :style="{ color: predictionResult.prediction_mode === 'dedicated_scaler' ? 'rgb(74,222,128)' : 'rgb(250,204,21)' }">
                            {{ predictionResult.prediction_mode }}
                        </span>
                    </div>
                </div>
                <div class="row self-start">
                    <div class="pl-1 pb-1 pr-1" style="background-color: #202020; border-radius: 5px;">
                        <span class="mr-3">Dernier close : </span>
                        <span>{{ predictionResult.last_known_close }} $</span>
                    </div>
                </div>
                <div class="row self-start">
                    <div class="pl-1 pb-1 pr-1" style="background-color: #202020; border-radius: 5px;">
                        <span class="mr-3">Dernière date : </span>
                        <span>{{ predictionResult.last_known_date }}</span>
                    </div>
                </div>

                <!-- Tableau des prédictions -->
                <div class="row self-start w-full mt-2">
                    <table style="width:100%; font-size:0.82em; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 1px solid #444;">
                                <th style="text-align:left; padding: 4px 8px;">Step</th>
                                <th style="text-align:left; padding: 4px 8px;">Close estimé</th>
                                <th style="text-align:left; padding: 4px 8px;">Date estimée</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="p in predictionResult.predictions" :key="p.step" style="border-bottom: 1px solid #333;">
                                <td style="padding: 4px 8px;">{{ p.step }}</td>
                                <td style="padding: 4px 8px; color: rgb(74,222,128);">{{ p.predicted_close }} $</td>
                                <td style="padding: 4px 8px; font-size:0.9em; color:#aaa;">
                                    {{ p.estimated_date ?? "—" }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </template>
        </div>
    </section>
</template>

<style>
.loader {
    background-color: rgba(00, 00, 00, 0.5);
}
.spinner > svg {
    width: 5em;
    height: 5em;
    fill: hsl(231, 22%, 88%);
}
</style>
