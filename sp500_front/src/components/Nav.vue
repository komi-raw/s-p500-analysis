<script setup lang="ts">
import { RouterLink } from "vue-router";
import { homeRoute, routeInfo } from "@/router";

const routerForNav = routeInfo.filter((r) => {
    return r.path !== "/";
});
</script>

<template>
    <header class="h-20 outline outline-accent">
        <nav
            class="pl-10 pr-10 h-full flex items-center flex-row justify-between"
        >
            <div>
                <RouterLink :to="homeRoute.path"
                    ><span class="brand-tx">SP5-CRW</span></RouterLink
                >
            </div>
            <div class="space-x-4">
                <RouterLink v-for="info in routerForNav" :to="info.path">{{
                    info.navHeader !== "" ? info.navHeader : info.title
                }}</RouterLink>
            </div>
        </nav>
    </header>
</template>
