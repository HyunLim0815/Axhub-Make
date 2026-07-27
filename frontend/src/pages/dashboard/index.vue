<template>
  <div>
    <h2 style="margin-bottom: 20px">项目概览</h2>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>原型</span></template>
          <div style="font-size: 32px; font-weight: 600; color: var(--el-color-primary)">{{ stats.prototypeCount }}</div>
          <div style="margin-top: 12px">
            <el-button link @click="$router.push('/prototypes')">查看全部 →</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>知识条目</span></template>
          <div style="font-size: 32px; font-weight: 600; color: var(--el-color-success)">{{ stats.knowledgeCount }}</div>
          <div style="margin-top: 12px">
            <el-button link @click="$router.push('/knowledge')">查看全部 →</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>发布通道</span></template>
          <div style="font-size: 32px; font-weight: 600; color: var(--el-color-warning)">{{ stats.channelCount }}</div>
          <div style="margin-top: 12px">
            <el-button link @click="$router.push('/publish')">查看全部 →</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" style="margin-top: 20px">
      <template #header><span>发布通道状态</span></template>
      <el-table :data="channels" v-if="channels.length" stripe style="width:100%">
        <el-table-column prop="name" label="通道" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="current_version" label="当前版本" width="120">
          <template #default="{ row }">v{{ row.current_version || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无通道" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { publishApi } from '@/api'
import { Odometer, Promotion } from '@element-plus/icons-vue'

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
