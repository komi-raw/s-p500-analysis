<script setup lang="ts">
import {
    getAllCompanies,
    getCompanyInfo,
    type CompanyID,
} from "@/fetchers/Company.ftc";
import { getAllPrices } from "@/fetchers/Company2Stat.ftc";
import { ChartDefault } from "@/objects/ChartCM";
import { CandlestickSeries } from "lightweight-charts";
import { onBeforeMount, onMounted, ref } from "vue";

const loading = ref(true);
const currentCompany = ref("");
const companies = ref<CompanyID[]>([
    { id: 1, code: "TOT" },
    { id: 2, code: "TET" },
]);
onBeforeMount(() => {
    getAllCompanies()
        .then((xAnswer) => {
            loading.value = false;
            companies.value = Array.from(xAnswer.data);
        })
        .catch((xReject) => {
            loading.value = false;
        });
});
let chart: any = null;
onMounted(() => {
    const data = [
        { open: 10, high: 10.63, low: 9.49, close: 9.55, time: 1642427876 },
        { open: 9.55, high: 10.3, low: 9.42, close: 9.94, time: 1642514276 },
        { open: 9.94, high: 10.17, low: 9.92, close: 9.78, time: 1642600676 },
        { open: 9.78, high: 10.59, low: 9.18, close: 9.51, time: 1642687076 },
        { open: 9.51, high: 10.46, low: 9.1, close: 10.17, time: 1642773476 },
        {
            open: 10.17,
            high: 10.96,
            low: 10.16,
            close: 10.47,
            time: 1642859876,
        },
        { open: 10.47, high: 11.39, low: 10.4, close: 10.81, time: 1642946276 },
        { open: 10.81, high: 11.6, low: 10.3, close: 10.75, time: 1643032676 },
        { open: 10.75, high: 11.6, low: 10.49, close: 10.93, time: 1643119076 },
        {
            open: 10.93,
            high: 11.53,
            low: 10.76,
            close: 10.96,
            time: 1643205476,
        },
    ];

    chart = new ChartDefault("chart", CandlestickSeries);

    chart.registerData(data);
    chart.fitContent();
});

function corpChanged(val: any) {
    loading.value = true;
    currentCompany.value = val.target.value;
    getCompanyInfo(currentCompany.value).then((xAnswer) => {
        console.log(xAnswer);
    });
    getAllPrices(currentCompany.value).then((xAnswer) => {
        let d = Array.from(xAnswer.data);
        let s = Array.from(
            new Map(
                d
                    .map((d) => ({
                        open: d.open,
                        high: d.high,
                        low: d.low,
                        close: d.close,
                        time: Math.floor(new Date(d.date).getTime() / 1000),
                    }))
                    .sort((a, b) => a.time - b.time)
                    .map((item) => [item.time, item]),
            ).values(),
        );
        chart.registerData(s);
        chart.fitContent();
        loading.value = false;
    });
}
</script>

<template>
    <div
        v-if="loading"
        class="loader absolute z-10 mainSubject w-full flex justify-center items-center"
    >
        <span class="spinner"
            ><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
                    opacity=".25"
                />
                <path
                    d="M12,4a8,8,0,0,1,7.89,6.7A1.53,1.53,0,0,0,21.38,12h0a1.5,1.5,0,0,0,1.48-1.75,11,11,0,0,0-21.72,0A1.5,1.5,0,0,0,2.62,12h0a1.53,1.53,0,0,0,1.49-1.3A8,8,0,0,1,12,4Z"
                >
                    <animateTransform
                        attributeName="transform"
                        type="rotate"
                        dur="0.75s"
                        values="0 12 12;360 12 12"
                        repeatCount="indefinite"
                    />
                </path></svg
        ></span>
    </div>
    <section class="mainSubject flex flex-row">
        <div style="width: 60%" id="chart"></div>
        <div style="width: 40%" class="bg-accent">
            <div>
                <span>Company : </span>
                <select @change="corpChanged" name="corp" id="">
                    <option
                        v-for="(company, index) in companies"
                        :value="company.code"
                    >
                        {{ company.code }}
                    </option>
                </select>
            </div>
            <div>
                
            </div>
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
