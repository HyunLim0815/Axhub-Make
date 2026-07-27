<template>
  <div>
    <n-page-header>
      <template #title>发布管理</template>
    </n-page-header>

    <n-grid :cols="3" :x-gap="16" class="mt-4">
      <n-grid-item v-for="ch in channels" :key="ch.id">
        <n-card :title="ch.name" size="small">
          <template #header-extra>
            <n-tag :type="ch.status === 'published' ? 'success' : 'default'" size="tiny">{{ ch.status }}</n-tag>
          </template>
          <n-description>
            <n-description-item label="类型">{{ ch.type }}</n-description-item>
            <n-description-item label="当前版本">v{{ ch.current_version || '-' }}</n-description-item>
            <n-description-item label="地址">{{ ch.base_url || '-' }}</n-description-item>
          </n-description>
          <template #footer>
            <n-button size="small" @click="handleDeploy(ch.id)">发布</n-button>
          </template>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="发布记录" class="mt-4">
      <n-table v-if="records.length" :bordered="false">
        <thead><tr><th>版本</th><th>通道</th><th>说明</th><th>时间</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td>v{{ r.version }}</td>
            <td>{{ channelName(r.channel_id) }}</td>
            <td>{{ r.summary }}</td>
            <td>{{ formatTime(r.create_time) }}</td>
            <td><n-tag :type="r.status === 'published' ? 'success' : 'error'" size="tiny">{{ r.status }}</n-tag></td>
          </tr>
        </tbody>
      </n-table>
      <n-empty v-else description="暂无发布记录" style="padding:40px" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { publishApi } from '@/api'

const message = useMessage()
const channels = ref<any[]>([])
const records = ref<any[]>([])

function formatTime(ts: string) {
  if (!ts) return '-'
  return new Date(ts).toLocaleString('zh-CN')
}

function channelName(id: number) {
  return channels.value.find(c => c.id === id)?.name || `#${id}`
}

async function load() {
  const res = await publishApi.channels()
  channels.value = res.data || []
  const rec = await publishApi.records()
  records.value = rec.data || []
}

async function handleDeploy(id: number) {
  await publishApi.deploy(id)
  message.success('发布成功')
  await load()
}

onMounted(load)
</script>
