import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/lesson/:moduleId/:lessonId', component: HomeView },
    { path: '/login', component: () => import('../views/LoginView.vue') },
    { path: '/stats', component: () => import('../views/StatsView.vue') },
    { path: '/review', component: () => import('../views/ReviewView.vue') },
    { path: '/plan', component: () => import('../views/PlanView.vue') },
    { path: '/resources', component: () => import('../views/ResourcesView.vue') },
  ],
})

export default router
