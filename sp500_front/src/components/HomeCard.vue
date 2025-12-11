<script setup lang="ts">
import router from "@/router";

const goToDataView = () => router.push("/data/view");

defineProps(["title", "subtext", "isActive"]);
</script>

<template>
    <div v-if="!isActive" class="p-8 card restricted cursor-not-allowed">
        <h3 class="text-xl">Unavailable yet.</h3>
    </div>
    <div @click="goToDataView" v-if="isActive" class="card cursor-pointer">
        <div class="h-full card-content flex flex-col justify-between">
            <h3 class="text-xl">{{ title }}</h3>
            <p class="card-subtext pl-4">{{ subtext }}</p>
            <div class="flex self-end">
                <span class="material-symbols-outlined">
                    arrow_forward_ios
                </span>
                Go to the tool
            </div>
        </div>
    </div>
</template>

<style>
.card {
    transform: scale(1);
    transition: transform 0.2s ease-in-out;
    border: solid 1px rgba(255, 255, 255, 0.2);
    background-image: radial-gradient(rgba(255, 255, 255, 0.2) 8%, black 8%);
    background-position: 0% 0%;
    background-size: 5vmin 5vmin;
}

.card.restricted {
    background: repeating-linear-gradient(
        -45deg,
        rgba(255, 255, 255, 0.2),
        rgba(255, 255, 255, 0.2) 2px,
        black 5px,
        black 25px
    );
}

.card-content {
    padding: 2rem;
    position: relative;
    z-index: 2;
}

.card-subtext {
    opacity: 80%;
}
</style>
