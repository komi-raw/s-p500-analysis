<script setup lang="ts">
import HomeCard from "@/components/HomeCard.vue";
import { routeInfo } from "@/router";
</script>

<template>
    <div class="mainSubject p-8 grid sm:grid-cols-1 md:grid-cols-2 gap-6">
        <HomeCard
            v-for="info in routeInfo"
            :title="info.title"
            :subtext="info.subtext"
            :isActive="info.path !== '/'"
        ></HomeCard>
    </div>
</template>

<style>
.card:hover.restricted {
    transform: scale(1) !important;
}
.card:hover {
    transform: scale(1.05);
    transition: transform 0.2s ease-in-out;
}
</style>
