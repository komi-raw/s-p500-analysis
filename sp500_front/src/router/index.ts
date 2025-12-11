import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import type { Component } from "vue";
import Viewer from "../views/Viewer.vue";

export type RouteType = {
    path: string;
    name: string;
    component: Component | null;
    title: string;
    subtext: string;
    navHeader: string;
};

export const homeRoute: RouteType = {
    path: "/",
    name: "home",
    component: HomeView,
    title: "",
    subtext: "",
    navHeader: "Home",
};
export const routeInfo: RouteType[] = [
    {
        path: "/data/view",
        name: "view",
        component: Viewer,
        title: "Data viewer",
        subtext: "View the recent data from the S&P-500 stock market.",
        navHeader: "Viewer",
    },
    {
        path: "/",
        name: "request",
        component: null,
        title: "Data editor",
        subtext: "",
        navHeader: "Editor",
    },
    {
        path: "/",
        name: "home",
        component: null,
        title: "",
        subtext: "",
        navHeader: "",
    },
    {
        path: "/",
        name: "home",
        component: null,
        title: "",
        subtext: "",
        navHeader: "",
    },
];

const registeredRoutes = [
    {
        path: homeRoute.path,
        name: homeRoute.name,
        component: HomeView as Component,
    },
];

routeInfo.forEach((localRoute) => {
    if (localRoute.path !== "/")
        registeredRoutes.push({
            path: localRoute.path,
            name: localRoute.name,
            component: localRoute.component as Component,
        });
});

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: registeredRoutes,
});

export default router;
