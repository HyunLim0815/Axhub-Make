<template>
  <n-layout position="absolute" has-sider>
    <n-layout-sider
      bordered
      :collapsed="appStore.sidebarCollapsed"
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :native-scrollbar="false"
    >
      <div class="sider-header">
        <n-h3 v-if="!appStore.sidebarCollapsed" style="margin:0">Axhub Make</n-h3>
        <n-h3 v-else style="margin:0;text-align:center">AM</n-h3>
      </div>
      <n-menu
        :collapsed="appStore.sidebarCollapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="route.path"
        @update:value="handleMenuSelect"
      />
    </n-layout-sider>

    <n-layout>
      <n-layout-header bordered class="layout-header">
        <n-space align="center">
          <n-button quaternary @click="appStore.toggleSidebar">
            <template #icon>
              <n-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M3 4h18v2H3V4zm0 7h18v2H3v-2zm0 7h18v2H3v-2z"/></svg></n-icon>
            </template>
          </n-button>
          <n-breadcrumb>
            <n-breadcrumb-item>{{ route.meta?.title || route.name }}</n-breadcrumb-item>
          </n-breadcrumb>
        </n-space>
        <n-space>
          <n-button quaternary @click="appStore.toggleDark">
            <template #icon>
              <n-icon>{{ appStore.darkMode ? '☀️' : '🌙' }}</n-icon>
            </template>
          </n-button>
        </n-space>
      </n-layout-header>

      <n-layout-content class="layout-content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const iconify = (icon: string) => () => h(NIcon, null, { default: () => icon })

const menuOptions = [
  { label: '仪表盘', key: '/', icon: iconify('📊') },
  { label: '原型', key: '/prototypes', icon: iconify('📐') },
  { label: '知识库', key: '/knowledge', icon: iconify('📚') },
  { label: '发布', key: '/publish', icon: iconify('🚀') },
  { label: 'AI 助手', key: '/ai', icon: iconify('🤖') },
  { label: '设置', key: '/settings', icon: iconify('⚙️') },
]

function handleMenuSelect(key: string) {
  router.push(key)
}
</script>

<style scoped>
.sider-header {
  padding: 16px;
  border-bottom: 1px solid var(--n-border-color);
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  height: 48px;
}
.layout-content {
  padding: 24px;
  min-height: calc(100vh - 48px);
}
</style>
