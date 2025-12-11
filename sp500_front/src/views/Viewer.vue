<script setup lang="ts">
import { ChartDefault } from "@/objects/ChartCM";
import { CandlestickSeries } from "lightweight-charts";
import { onBeforeMount, onMounted } from "vue";
onBeforeMount(() => {
    fetch("");
});
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

    const chart = new ChartDefault("chart", CandlestickSeries);

    chart.registerData(data);
    chart.fitContent();
});

function corpChanged(val: any) {
    console.log(val.target.value);
}
</script>

<template>
    <section class="mainSubject flex flex-row">
        <div style="width: 60%" id="chart"></div>
        <div style="width: 40%" class="bg-accent">
            <select @change="corpChanged" name="corp" id="">
                <option value="request1">Corp 1</option>
                <option value="request2">Corp 2</option>
            </select>
        </div>
    </section>
</template>
