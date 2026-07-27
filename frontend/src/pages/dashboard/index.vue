<template>
  <div>
    <n-h2>项目概览</n-h2>
    <n-grid :cols="3" :x-gap="16">
      <n-grid-item>
        <n-card title="原型" size="small">
          <n-number-animation :from="0" :to="stats.prototypeCount" />
          <template #footer><n-button text @click="$router.push('/prototypes')">查看全部 →</n-button></template>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="知识条目" size="small">
          <n-number-animation :from="0" :to="stats.knowledgeCount" />
          <template #footer><n-button text @click="$router.push('/knowledge')">查看全部 →</n-button></template>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="发布通道" size="small">
          <n-number-animation :from="0" :to="stats.channelCount" />
          <template #footer><n-button text @click="$router.push('/publish')">查看全部 →</n-button></template>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="发布通道状态" class="mt-4">
      <n-table v-if="channels.length" :bordered="false">
        <thead><tr><th>通道</th><th>类型</th><th>当前版本</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="ch in channels" :key="ch.id">
            <td>{{ ch.name }}</td><td>{{ ch.type }}</td><td>v{{ ch.current_version || '-' }}</td>
            <td><n-tag :type="ch.status === 'published' ? 'success' : 'default'">{{ ch.status }}</n-tag></td>
          </tr>
        </tbody>
      </n-table>
      <n-empty v-else description="暂无通道" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { publishApi } from '@/api'

const stats = reactive({ prototypeCount: 0, knowledgeCount: 0, channelCount: 0 })
const channels = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await publishApi.dashboard()
    channels.value = res.data.channels || []
    stats.channelCount = channels.value.length
  } catch {}
})
</script>
