<script setup lang="ts">
import { ref, onBeforeMount, nextTick, computed } from "vue";
import { getAllCompanies, type CompanyID } from "@/fetchers/Company.ftc";
import { BACK_IA_PORT } from "@/config/public-env";

const companies = ref<CompanyID[]>([]);
const selectedCompanies = ref<string[]>([]);
const companySearch = ref("");

const filteredCompanies = computed(() =>
    companies.value.filter((c) =>
        c.code.toLowerCase().includes(companySearch.value.toLowerCase())
    )
);

function toggleAll() {
    if (selectedCompanies.value.length === filteredCompanies.value.length && filteredCompanies.value.length > 0) {
        selectedCompanies.value = selectedCompanies.value.filter(
            (s) => !filteredCompanies.value.find((c) => c.code === s)
        );
    } else {
        const toAdd = filteredCompanies.value.map((c) => c.code).filter((code) => !selectedCompanies.value.includes(code));
        selectedCompanies.value = [...selectedCompanies.value, ...toAdd];
    }
}
const messages = ref<{ role: string; content: string; chart?: any }[]>([]);
const inputMessage = ref("");
const loading = ref(false);
const mode = ref<"chat" | "sql">("chat");

onBeforeMount(() => {
    getAllCompanies().then((res) => {
        companies.value = Array.from(res.data);
    });
});

function drawChart(canvasId: string, data: any[]) {
    nextTick(() => {
        const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!canvas || !data.length) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const labels = data.map((d: any) => d.date ? new Date(d.date).toLocaleDateString() : "");
        const closes = data.map((d: any) => d.close ?? d[Object.keys(d)[0]]);

        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        const max = Math.max(...closes);
        const min = Math.min(...closes);
        const range = max - min || 1;

        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "#1a1a1a";
        ctx.fillRect(0, 0, width, height);

        // Axes
        ctx.strokeStyle = "#444";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();

        // Courbe
        ctx.strokeStyle = "#4ade80";
        ctx.lineWidth = 2;
        ctx.beginPath();
        closes.forEach((val: number, i: number) => {
            const x = padding + (i / (closes.length - 1)) * (width - 2 * padding);
            const y = height - padding - ((val - min) / range) * (height - 2 * padding);
            i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Labels min/max
        ctx.fillStyle = "#aaa";
        ctx.font = "11px sans-serif";
        ctx.fillText(`${max.toFixed(2)}`, padding + 4, padding + 12);
        ctx.fillText(`${min.toFixed(2)}`, padding + 4, height - padding - 4);
    });
}

function exportConversation() {
    if (!messages.value.length) return;
    const header = `AI Analyst — Export
Entreprises : ${selectedCompanies.value.join(", ") || "aucune"}
Mode : ${mode.value}
Date : ${new Date().toLocaleString()}
${"=".repeat(60)}\n\n`;
    const body = messages.value
        .map((m) => `[${m.role === "user" ? "Vous" : "AI"}]\n${m.content}`)
        .join("\n\n" + "-".repeat(40) + "\n\n");
    const blob = new Blob([header + body], { type: "text/plain;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analyse_ia_${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

async function sendMessage() {
    if (!inputMessage.value.trim()) return;

    const userMsg = inputMessage.value;
    inputMessage.value = "";
    messages.value.push({ role: "user", content: userMsg });
    loading.value = true;

    try {
        const endpoint = mode.value === "sql" ? "/ask/ia/sqlproxy" : "/ask/ia/analyst";
        const res = await fetch(`http://localhost:${BACK_IA_PORT}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt: userMsg,
                companies: selectedCompanies.value,
            }),
        });
        const data = await res.json();
        const msgIndex = messages.value.length;
        messages.value.push({
            role: "assistant",
            content: data.response || data.error || "Erreur inconnue",
            chart: data.raw_data && data.raw_data.length > 1 ? data.raw_data : null,
        });

        if (data.raw_data && data.raw_data.length > 1) {
            drawChart(`chart-${msgIndex}`, data.raw_data);
        }
    } catch (e) {
        messages.value.push({ role: "assistant", content: "Erreur de connexion au backend IA." });
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <div class="mainSubject flex flex-col p-6 gap-4">
        <h2 class="text-xl font-bold">AI Analyst</h2>

        <!-- Sélection des entreprises -->
        <div class="flex gap-3" style="height: 220px;">
            <div class="flex flex-col gap-1 flex-1 min-w-0">
                <!-- Header -->
                <div class="flex items-center justify-between">
                    <span class="text-sm font-semibold">Entreprises</span>
                    <span class="text-xs text-zinc-400">
                        {{ selectedCompanies.length }} sélectionnée{{ selectedCompanies.length > 1 ? 's' : '' }}
                    </span>
                </div>
                <!-- Recherche -->
                <input
                    v-model="companySearch"
                    type="text"
                    placeholder="Rechercher..."
                    class="bg-zinc-800 rounded px-2 py-1 text-sm outline-none border border-zinc-700 focus:border-zinc-500"
                />
                <!-- Tout sélectionner -->
                <button
                    @click="toggleAll"
                    class="text-xs text-left px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 transition-colors text-zinc-400 hover:text-zinc-200"
                >
                    {{ selectedCompanies.length === filteredCompanies.length && filteredCompanies.length > 0 ? 'Tout désélectionner' : 'Tout sélectionner' }}
                    <span class="text-zinc-600">({{ filteredCompanies.length }})</span>
                </button>
                <!-- Liste checkboxes -->
                <div class="overflow-y-auto flex-1 rounded border border-zinc-700 bg-zinc-900">
                    <label
                        v-for="c in filteredCompanies"
                        :key="c.code"
                        class="flex items-center gap-2 px-3 py-1 cursor-pointer hover:bg-zinc-800 transition-colors"
                        :class="{ 'bg-zinc-800': selectedCompanies.includes(c.code) }"
                    >
                        <input
                            type="checkbox"
                            :value="c.code"
                            v-model="selectedCompanies"
                            class="accent-green-400 cursor-pointer"
                        />
                        <span class="text-sm font-mono" :class="selectedCompanies.includes(c.code) ? 'text-green-400' : 'text-zinc-300'">
                            {{ c.code }}
                        </span>
                    </label>
                    <div v-if="filteredCompanies.length === 0" class="px-3 py-2 text-xs text-zinc-500">
                        Aucun résultat
                    </div>
                </div>
            </div>

            <!-- Chips des sélections actives -->
            <div v-if="selectedCompanies.length > 0" class="flex flex-col gap-1" style="width: 140px;">
                <span class="text-xs text-zinc-400 font-semibold">Sélectionnées</span>
                <div class="overflow-y-auto flex-1 flex flex-col gap-1">
                    <div
                        v-for="code in selectedCompanies"
                        :key="code"
                        class="flex items-center justify-between bg-zinc-800 rounded px-2 py-0.5"
                    >
                        <span class="text-xs font-mono text-green-400">{{ code }}</span>
                        <button
                            @click="selectedCompanies = selectedCompanies.filter(s => s !== code)"
                            class="text-zinc-500 hover:text-red-400 transition-colors text-xs ml-1"
                        >✕</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" v-model="mode" value="chat" /> Chat financier
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" v-model="mode" value="sql" /> Requête SQL naturelle
            </label>
        </div>

        <div class="flex flex-col gap-4 bg-zinc-900 rounded p-4 overflow-y-auto" style="height: 500px;">
            <div v-if="messages.length === 0" class="text-zinc-500 text-sm">
                Pose une question sur les entreprises sélectionnées...
            </div>
            <div v-for="(msg, i) in messages" :key="i"
                :class="msg.role === 'user' ? 'self-end bg-zinc-700' : 'self-start bg-zinc-800 w-full'"
                class="rounded p-3 text-sm whitespace-pre-wrap">
                <span class="font-bold mr-2">{{ msg.role === 'user' ? 'Vous' : 'AI' }} :</span>
                {{ msg.content }}
                <canvas v-if="msg.chart" :id="`chart-${i}`" width="600" height="200"
                    class="mt-3 rounded w-full"></canvas>
            </div>
            <div v-if="loading" class="self-start text-zinc-400 text-sm animate-pulse">
                L'IA réfléchit...
            </div>
        </div>

        <div v-if="messages.length" class="flex justify-end">
            <button
                @click="exportConversation"
                class="text-xs px-3 py-1.5 rounded border border-green-700 text-green-400 hover:bg-green-900/30 transition-colors"
            >
                ↓ Exporter la conversation
            </button>
        </div>

        <div class="flex gap-2">
            <textarea v-model="inputMessage" @keydown.enter.prevent="sendMessage"
                placeholder="Ex: Donne moi les 20 derniers prix de clôture de TSLA"
                class="flex-1 bg-zinc-800 rounded p-2 text-sm resize-none" rows="2"></textarea>
            <button @click="sendMessage" :disabled="loading"
                class="bg-zinc-700 hover:bg-zinc-600 rounded px-4 py-2 text-sm transition-all">
                Envoyer
            </button>
        </div>
    </div>
</template>