<script setup>
import { RouterView } from "vue-router";
import Nav from "./components/Nav.vue";
import Footer from "./components/Footer.vue";
</script>

<template>
    <Nav></Nav>
    <RouterView />
    <Footer></Footer>
</template>
