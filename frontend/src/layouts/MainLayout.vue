<template>
  <el-container style="height: 100vh; flex-direction: column">
    <!-- 顶部导航栏 -->
    <el-header class="app-header" height="52px">
      <div class="header-left">
        <span class="app-logo">产品原型工作台</span>
        <el-menu
          :default-active="route.path"
          mode="horizontal"
          @select="handleSelect"
          style="border-bottom: none; margin-left: 24px; width: 800px !important"
        >
          <el-menu-item index="/"><el-icon><Odometer /></el-icon>项目</el-menu-item>
          <el-menu-item index="/prototypes"><el-icon><Document /></el-icon>原型</el-menu-item>
          <el-menu-item index="/knowledge"><el-icon><Notebook /></el-icon>知识库</el-menu-item>
          <el-menu-item index="/reports"><el-icon><DocumentChecked /></el-icon>审查报告</el-menu-item>
          <el-menu-item index="/publish"><el-icon><Promotion /></el-icon>发布</el-menu-item>
          <el-menu-item index="/ai"><el-icon><ChatLineSquare /></el-icon>AI 助手</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <el-button text @click="$router.push('/settings')">
          <el-icon><Setting /></el-icon>
        </el-button>
        <el-button text @click="appStore.toggleDark">
          <el-icon><Moon v-if="!appStore.darkMode" /><Sunny v-else /></el-icon>
        </el-button>
      </div>
    </el-header>

    <!-- 内容区 — 自动填充剩余高度 -->
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { Moon, Sunny, Odometer, Document, Notebook, Promotion, ChatLineSquare, Setting, DocumentChecked } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

function handleSelect(index: string) {
  router.push(index)
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  padding: 0 16px;
  height: 70px !important;
}

.el-menu{
    min-width: 400px !important;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}
.app-logo {
  font-weight: 700;
  font-size: 16px;
  color: var(--el-color-primary);
  white-space: nowrap;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}
.app-main {
  background: var(--el-bg-color-page);
  padding: 20px;
  overflow: auto;
  flex: 1;
  height: 0;
  min-height: 0;
}
</style>
