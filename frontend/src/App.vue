<template>
  <n-config-provider :theme="theme" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { zhCN, dateZhCN } from 'naive-ui'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const theme = computed(() => appStore.naiveTheme)
</script>
