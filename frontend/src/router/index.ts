import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'dashboard', meta: { title: '仪表盘' }, component: () => import('@/pages/dashboard/index.vue') },
        { path: 'prototypes', name: 'prototypes', meta: { title: '原型' }, component: () => import('@/pages/prototypes/index.vue') },
        { path: 'prototypes/:id', name: 'prototype-detail', meta: { title: '原型详情' }, component: () => import('@/pages/prototypes/[id]/canvas.vue') },
        { path: 'knowledge', name: 'knowledge', meta: { title: '知识库' }, component: () => import('@/pages/knowledge/index.vue') },
        { path: 'reports', name: 'reports', meta: { title: '审查报告' }, component: () => import('@/pages/reports/index.vue') },
        { path: 'publish', name: 'publish', meta: { title: '发布' }, component: () => import('@/pages/publish/index.vue') },
        { path: 'settings', name: 'settings', meta: { title: '设置' }, component: () => import('@/pages/settings/index.vue') },
        { path: 'ai', name: 'ai', meta: { title: 'AI 助手' }, component: () => import('@/pages/ai/chat.vue') },
      ],
    },
  ],
})

export default router
