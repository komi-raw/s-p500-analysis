<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { SECTORS, type Sector } from "@/config/sectors";
import { getAllCompanies, type CompanyID } from "@/fetchers/Company.ftc";
import { getPrediction, type PredictionResult } from "@/fetchers/Prediction.ftc";
import { BACK_DOMAIN, BACK_IA_PORT } from "@/config/public-env";

// ── State ────────────────────────────────────────────────────────────────────
const allCompanies = ref<CompanyID[]>([]);
const activeSector = ref<Sector>(SECTORS[0]);
const selectedTickers = ref<string[]>([]);
const mlResults = ref<Record<string, PredictionResult>>({});
const aiResponse = ref<string>("");
const isAnalyzing = ref(false);
const mlLoading = ref(false);
const mlError = ref("");
const aiError = ref("");
const steps = ref(7);

// ── Derived ──────────────────────────────────────────────────────────────────
const availableTickers = computed(() => {
    const codes = new Set(allCompanies.value.map((c) => c.code));
    return activeSector.value.tickers.filter((t) => codes.has(t));
});

const allSelected = computed(
    () =>
        availableTickers.value.length > 0 &&
        availableTickers.value.every((t) => selectedTickers.value.includes(t))
);

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
    try {
        const res = await getAllCompanies();
        allCompanies.value = res.data;
    } catch {
        // silently ignore
    }
});

// Reset selection when sector changes
watch(activeSector, () => {
    selectedTickers.value = [];
    mlResults.value = {};
    aiResponse.value = "";
});

// ── Methods ───────────────────────────────────────────────────────────────────
function toggleTicker(ticker: string) {
    const idx = selectedTickers.value.indexOf(ticker);
    if (idx === -1) selectedTickers.value.push(ticker);
    else selectedTickers.value.splice(idx, 1);
}

function toggleAll() {
    if (allSelected.value) {
        selectedTickers.value = [];
    } else {
        selectedTickers.value = [...availableTickers.value];
    }
}

function sparkColor(predictions: PredictionResult["predictions"], last: number): string {
    if (!predictions?.length) return "#6b7280";
    const last_pred = predictions[predictions.length - 1].predicted_close;
    return last_pred >= last ? "#10b981" : "#ef4444";
}

function pctChange(predictions: PredictionResult["predictions"], last: number): string {
    if (!predictions?.length) return "—";
    const end = predictions[predictions.length - 1].predicted_close;
    const pct = ((end - last) / last) * 100;
    return (pct >= 0 ? "+" : "") + pct.toFixed(2) + "%";
}

async function runAnalysis() {
    if (!selectedTickers.value.length) return;

    mlLoading.value = true;
    mlError.value = "";
    aiResponse.value = "";
    aiError.value = "";
    isAnalyzing.value = false;
    mlResults.value = {};

    // 1) Fetch ML predictions for all selected tickers in parallel
    const results = await Promise.allSettled(
        selectedTickers.value.map((ticker) =>
            getPrediction(ticker, steps.value, "day")
        )
    );

    const successData: Record<string, PredictionResult> = {};
    results.forEach((r, i) => {
        if (r.status === "fulfilled" && r.value.data) {
            successData[selectedTickers.value[i]] = r.value.data;
        }
    });

    mlResults.value = successData;
    mlLoading.value = false;

    if (!Object.keys(successData).length) {
        mlError.value = "Aucune prédiction disponible pour les tickers sélectionnés.";
        return;
    }

    // 2) Send ML summary to IA for cross-analysis
    isAnalyzing.value = true;

    const mlSummary = Object.entries(successData)
        .map(([ticker, r]) => {
            const last = r.last_known_close;
            const preds = r.predictions.map((p) => p.predicted_close);
            const trend = pct_raw(preds[preds.length - 1], last);
            return `${ticker}: dernier cours ${last.toFixed(2)}, prédiction sur ${r.prediction_length} jours → ${preds[preds.length - 1].toFixed(2)} (${trend >= 0 ? "+" : ""}${trend.toFixed(2)}%)`;
        })
        .join("\n");

    const prompt = `Secteur analysé : ${activeSector.value.name}

Voici les prédictions ML (PatchTST) sur ${steps.value} jours pour ${Object.keys(successData).length} entreprises du secteur :

${mlSummary}

En tant qu'expert financier, analyse ces prédictions :
1. Quelles entreprises montrent la meilleure dynamique haussière ?
2. Y a-t-il des tendances sectorielles communes ?
3. Quelles entreprises semblent sous-performer par rapport au reste du secteur ?
4. Recommandations d'observation à court terme.`;

    try {
        const iaUrl = new URL("/ask/ia/analyst", BACK_DOMAIN);
        iaUrl.port = BACK_IA_PORT;
        const res = await fetch(iaUrl.toString(), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                companies: Object.keys(successData),
                prompt,
            }),
        });
        const json = await res.json();
        if (json.error) aiError.value = json.error;
        else aiResponse.value = json.response ?? "";
    } catch (e: any) {
        aiError.value = e?.message ?? "Erreur inconnue";
    } finally {
        isAnalyzing.value = false;
    }
}

function pct_raw(end: number, start: number): number {
    return ((end - start) / start) * 100;
}

// Mini sparkline: returns SVG polyline points string from predictions array
function sparklinePoints(predictions: PredictionResult["predictions"], last: number): string {
    const values = [last, ...predictions.map((p) => p.predicted_close)];
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const w = 80;
    const h = 28;
    return values
        .map((v, i) => {
            const x = (i / (values.length - 1)) * w;
            const y = h - ((v - min) / range) * h;
            return `${x.toFixed(1)},${y.toFixed(1)}`;
        })
        .join(" ");
}
</script>

<template>
    <div class="p-6 space-y-6">
        <!-- Header -->
        <div>
            <h1 class="text-2xl font-bold text-white">Sector Explorer</h1>
            <p class="text-gray-400 text-sm mt-1">
                Explorez les prédictions ML par secteur GICS et obtenez une analyse IA croisée.
            </p>
        </div>

        <!-- Sector tabs -->
        <div class="flex flex-wrap gap-2">
            <button
                v-for="sector in SECTORS"
                :key="sector.name"
                @click="activeSector = sector"
                class="px-3 py-1.5 rounded-full text-sm font-medium transition-all border"
                :style="{
                    borderColor: sector.color,
                    backgroundColor: activeSector.name === sector.name ? sector.color : 'transparent',
                    color: activeSector.name === sector.name ? '#fff' : sector.color,
                }"
            >
                {{ sector.name }}
            </button>
        </div>

        <!-- Main layout -->
        <div class="grid grid-cols-1 xl:grid-cols-4 gap-6">
            <!-- Left: ticker selector -->
            <div class="xl:col-span-1 bg-gray-800 rounded-xl p-4 space-y-3">
                <div class="flex items-center justify-between">
                    <h2 class="text-white font-semibold text-sm">
                        Entreprises
                        <span class="text-gray-400 font-normal">({{ availableTickers.length }} disponibles)</span>
                    </h2>
                    <button @click="toggleAll" class="text-xs text-blue-400 hover:text-blue-300 underline">
                        {{ allSelected ? "Désélectionner" : "Tout" }}
                    </button>
                </div>

                <div class="overflow-y-auto max-h-80 space-y-1 pr-1">
                    <label
                        v-for="ticker in availableTickers"
                        :key="ticker"
                        class="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-700 cursor-pointer"
                    >
                        <input
                            type="checkbox"
                            :checked="selectedTickers.includes(ticker)"
                            @change="toggleTicker(ticker)"
                            class="accent-blue-500"
                        />
                        <span class="text-gray-200 text-sm">{{ ticker }}</span>
                    </label>
                </div>

                <div class="border-t border-gray-700 pt-3 space-y-2">
                    <label class="text-gray-400 text-xs">Jours à prédire : {{ steps }}</label>
                    <input
                        type="range"
                        v-model.number="steps"
                        min="3"
                        max="30"
                        class="w-full accent-blue-500"
                    />
                </div>

                <button
                    @click="runAnalysis"
                    :disabled="!selectedTickers.length || mlLoading || isAnalyzing"
                    class="w-full py-2 rounded-lg text-sm font-semibold transition-colors"
                    :class="
                        selectedTickers.length && !mlLoading && !isAnalyzing
                            ? 'bg-blue-600 hover:bg-blue-500 text-white'
                            : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                    "
                >
                    <span v-if="mlLoading">Prédictions ML...</span>
                    <span v-else-if="isAnalyzing">Analyse IA...</span>
                    <span v-else>Analyser ({{ selectedTickers.length }} ticker{{ selectedTickers.length > 1 ? "s" : "" }})</span>
                </button>

                <p v-if="mlError" class="text-red-400 text-xs">{{ mlError }}</p>
            </div>

            <!-- Right: results -->
            <div class="xl:col-span-3 space-y-4">
                <!-- ML prediction cards -->
                <div v-if="Object.keys(mlResults).length">
                    <h2 class="text-white font-semibold mb-3">
                        Prédictions ML — {{ activeSector.name }}
                    </h2>
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                        <div
                            v-for="(result, ticker) in mlResults"
                            :key="ticker"
                            class="bg-gray-800 rounded-xl p-3 space-y-2"
                        >
                            <div class="flex items-center justify-between">
                                <span class="text-white font-bold text-sm">{{ ticker }}</span>
                                <span
                                    class="text-xs font-semibold"
                                    :style="{ color: sparkColor(result.predictions, result.last_known_close) }"
                                >
                                    {{ pctChange(result.predictions, result.last_known_close) }}
                                </span>
                            </div>

                            <!-- Sparkline -->
                            <svg width="80" height="28" class="w-full">
                                <polyline
                                    :points="sparklinePoints(result.predictions, result.last_known_close)"
                                    fill="none"
                                    stroke-width="1.5"
                                    :stroke="sparkColor(result.predictions, result.last_known_close)"
                                />
                            </svg>

                            <div class="text-gray-400 text-xs space-y-0.5">
                                <div>Actuel : <span class="text-gray-200">{{ result.last_known_close.toFixed(2) }}</span></div>
                                <div v-if="result.predictions.length">
                                    J+{{ result.prediction_length }} :
                                    <span class="text-gray-200">
                                        {{ result.predictions[result.predictions.length - 1].predicted_close.toFixed(2) }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Loading states -->
                <div v-else-if="mlLoading" class="flex items-center gap-3 text-gray-400 p-6">
                    <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                    </svg>
                    Calcul des prédictions ML en cours...
                </div>

                <div v-else-if="!selectedTickers.length" class="text-gray-500 text-sm p-6">
                    Sélectionnez des entreprises et cliquez sur <strong class="text-gray-300">Analyser</strong>.
                </div>

                <!-- AI Analysis panel -->
                <div
                    v-if="aiResponse || isAnalyzing || aiError"
                    class="bg-gray-800 rounded-xl p-5 space-y-3"
                >
                    <div class="flex items-center gap-2">
                        <div
                            class="w-2 h-2 rounded-full"
                            :style="{ backgroundColor: activeSector.color }"
                        ></div>
                        <h2 class="text-white font-semibold text-sm">
                            Analyse IA — {{ activeSector.name }}
                        </h2>
                        <span v-if="isAnalyzing" class="text-xs text-gray-400 animate-pulse">
                            Analyse en cours...
                        </span>
                    </div>

                    <div v-if="aiError" class="text-red-400 text-sm">{{ aiError }}</div>

                    <div
                        v-else-if="aiResponse"
                        class="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap"
                    >
                        {{ aiResponse }}
                    </div>

                    <div v-else-if="isAnalyzing" class="flex items-center gap-3 text-gray-400 text-sm">
                        <svg class="animate-spin h-4 w-4 flex-shrink-0" viewBox="0 0 24 24" fill="none">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                        </svg>
                        Le modèle IA interprète les prédictions ML...
                    </div>
                </div>

                <!-- Prediction detail table -->
                <div v-if="Object.keys(mlResults).length" class="bg-gray-800 rounded-xl overflow-hidden">
                    <table class="w-full text-sm text-left">
                        <thead>
                            <tr class="border-b border-gray-700 text-gray-400">
                                <th class="px-4 py-2">Ticker</th>
                                <th class="px-4 py-2">Dernier cours</th>
                                <th class="px-4 py-2">Prédiction finale</th>
                                <th class="px-4 py-2">Variation</th>
                                <th class="px-4 py-2">Tendance</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="(result, ticker) in mlResults"
                                :key="ticker"
                                class="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
                            >
                                <td class="px-4 py-2 font-bold text-white">{{ ticker }}</td>
                                <td class="px-4 py-2 text-gray-300">{{ result.last_known_close.toFixed(2) }}</td>
                                <td class="px-4 py-2 text-gray-300">
                                    {{
                                        result.predictions.length
                                            ? result.predictions[result.predictions.length - 1].predicted_close.toFixed(2)
                                            : "—"
                                    }}
                                </td>
                                <td
                                    class="px-4 py-2 font-semibold"
                                    :style="{ color: sparkColor(result.predictions, result.last_known_close) }"
                                >
                                    {{ pctChange(result.predictions, result.last_known_close) }}
                                </td>
                                <td class="px-4 py-2">
                                    <svg width="60" height="20">
                                        <polyline
                                            :points="sparklinePoints(result.predictions, result.last_known_close)"
                                            fill="none"
                                            stroke-width="1.5"
                                            :stroke="sparkColor(result.predictions, result.last_known_close)"
                                        />
                                    </svg>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>
