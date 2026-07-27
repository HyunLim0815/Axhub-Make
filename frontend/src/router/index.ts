import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'dashboard', component: () => import('@/pages/dashboard/index.vue') },
        { path: 'prototypes', name: 'prototypes', component: () => import('@/pages/prototypes/index.vue') },
        { path: 'prototypes/:id', name: 'prototype-detail', component: () => import('@/pages/prototypes/[id]/canvas.vue') },
        { path: 'knowledge', name: 'knowledge', component: () => import('@/pages/knowledge/index.vue') },
        { path: 'publish', name: 'publish', component: () => import('@/pages/publish/index.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/pages/settings/index.vue') },
        { path: 'ai', name: 'ai', component: () => import('@/pages/ai/chat.vue') },
      ],
    },
  ],
})

export default router
