<template>
  <el-container style="height: 100vh">
    <!-- 左侧边栏 -->
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '240px'" class="app-sidebar">
      <div class="sidebar-header">
        <span v-if="!appStore.sidebarCollapsed" class="sidebar-title">Axhub Make</span>
        <span v-else class="sidebar-title">AM</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="appStore.sidebarCollapsed"
        @select="handleSelect"
        style="border-right: none"
      >
        <el-menu-item index="/"><el-icon><Odometer /></el-icon><span>仪表盘</span></el-menu-item>
        <el-menu-item index="/prototypes"><el-icon><Document /></el-icon><span>原型</span></el-menu-item>
        <el-menu-item index="/knowledge"><el-icon><Notebook /></el-icon><span>知识库</span></el-menu-item>
        <el-menu-item index="/publish"><el-icon><Promotion /></el-icon><span>发布</span></el-menu-item>
        <el-menu-item index="/ai"><el-icon><ChatLineSquare /></el-icon><span>AI 助手</span></el-menu-item>
        <el-menu-item index="/settings"><el-icon><Setting /></el-icon><span>设置</span></el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="app-header" height="48px">
        <div class="header-left">
          <el-button text @click="appStore.toggleSidebar">
            <el-icon><Fold v-if="!appStore.sidebarCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <el-breadcrumb separator="/" style="margin-left: 12px">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta?.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button text @click="appStore.toggleDark">
            <el-icon><Moon v-if="!appStore.darkMode" /><Sunny v-else /></el-icon>
          </el-button>
        </div>
      </el-header>

      <!-- 内容 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { Fold, Expand, Moon, Sunny, Odometer, Document, Notebook, Promotion, ChatLineSquare, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

function handleSelect(index: string) {
  router.push(index)
}
</script>

<style scoped>
.app-sidebar {
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  transition: width 0.3s;
  overflow: hidden;
}
.sidebar-header {
  height: 48px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  font-weight: 600;
  font-size: 16px;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  padding: 0 16px;
}
.header-left, .header-right {
  display: flex;
  align-items: center;
}
.app-main {
  background: var(--el-bg-color-page);
  padding: 20px;
  overflow-y: auto;
}
</style>
