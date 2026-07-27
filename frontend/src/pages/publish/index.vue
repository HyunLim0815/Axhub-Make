<template>
  <div>
    <h2 style="margin-bottom:16px">发布管理</h2>

    <el-row :gutter="16">
      <el-col v-for="ch in channels" :key="ch.id" :span="8">
        <el-card shadow="never" style="margin-bottom:16px">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>{{ ch.name }}</span>
              <el-tag :type="ch.status === 'published' ? 'success' : 'info'" size="small">{{ ch.status }}</el-tag>
            </div>
          </template>
          <div style="font-size:13px;line-height:2">
            <div>类型: {{ ch.type }}</div>
            <div>当前版本: v{{ ch.current_version || '-' }}</div>
            <div>地址: {{ ch.base_url || '-' }}</div>
          </div>
          <div style="margin-top:12px">
            <el-button size="small" type="primary" @click="handleDeploy(ch.id)">发布</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header><span>发布记录</span></template>
      <el-table :data="records" v-if="records.length" stripe style="width:100%">
        <el-table-column label="版本" width="80"><template #default="{row}">v{{ row.version }}</template></el-table-column>
        <el-table-column prop="summary" label="说明" />
        <el-table-column label="通道" width="120"><template #default="{row}">{{ channelName(row.channel_id) }}</template></el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{row}"><el-tag :type="row.status === 'published' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="时间" width="180"><template #default="{row}">{{ fmtTime(row.create_time) }}</template></el-table-column>
      </el-table>
      <el-empty v-else description="暂无发布记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { publishApi } from '@/api'

const channels = ref<any[]>([])
const records = ref<any[]>([])
const fmtTime = (t: string) => t ? new Date(t).toLocaleString('zh-CN') : '-'
const channelName = (id: number) => channels.value.find(c => c.id === id)?.name || `#${id}`

async function load() {
  const [cr, rr] = await Promise.all([publishApi.channels(), publishApi.records()])
  channels.value = cr.data || []
  records.value = rr.data || []
}

async function handleDeploy(id: number) {
  await publishApi.deploy(id)
  ElMessage.success('发布成功')
  await load()
}

onMounted(load)
</script>
