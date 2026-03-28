<script setup lang="ts">
import { ref, onBeforeMount, nextTick } from "vue";
import { getAllCompanies, type CompanyID } from "@/fetchers/Company.ftc";
import { BACK_IA_PORT } from "@/config/public-env";

const companies = ref<CompanyID[]>([]);
const selectedCompanies = ref<string[]>([]);
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

        <div class="flex flex-wrap gap-2">
            <label class="text-sm">Entreprises :</label>
            <select multiple v-model="selectedCompanies" class="bg-zinc-800 rounded p-1 text-sm" style="height: 80px;">
                <option v-for="c in companies" :key="c.code" :value="c.code">{{ c.code }}</option>
            </select>
            <span class="text-xs text-zinc-400 self-end">Ctrl+clic pour sélectionner plusieurs</span>
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