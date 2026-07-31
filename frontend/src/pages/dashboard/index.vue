<template>
  <div v-loading="loading" class="dashboard-page">
    <!-- 页头 -->
    <div class="page-header">
      <h2 style="margin: 0">仪表盘</h2>
      <div style="display: flex; gap: 8px">
        <el-button :icon="Refresh" @click="load">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建项目</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 4px">
      <el-col v-for="card in statCards" :key="card.label" :xs="12" :sm="12" :md="6">
        <div class="stat-card">
          <div class="stat-icon" :style="{ backgroundColor: card.color + '1a', color: card.color }">
            <el-icon :size="26"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 项目列表 -->
      <el-col :xs="24" :md="16">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>项目列表</span>
              <el-button link type="primary" @click="openCreate">新建项目</el-button>
            </div>
          </template>
          <el-table
            :data="projects"
            stripe
            style="width: 100%"
            @row-click="goPrototypes"
            class="clickable-table"
          >
            <el-table-column prop="name" label="项目名称" min-width="140">
              <template #default="{ row }">
                <span style="font-weight: 500">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip min-width="160" />
            <el-table-column label="原型数" width="90" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.prototype_count || 0 }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="170">
              <template #default="{ row }">{{ fmtTime(row.create_time) }}</template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!projects.length && !loading" description="暂无项目，点击右上角新建" :image-size="80" />
        </el-card>
      </el-col>

      <!-- 右侧：发布通道 + 最近活动 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>发布通道</span>
              <el-button link type="primary" @click="router.push('/publish')">去发布</el-button>
            </div>
          </template>
          <div v-if="channels.length" class="channel-list">
            <div v-for="ch in channels" :key="ch.id" class="channel-item">
              <div class="channel-top">
                <span class="channel-name">{{ ch.name }}</span>
                <el-tag size="small" type="info">{{ channelTypeText[ch.type] || ch.type }}</el-tag>
              </div>
              <div class="channel-bottom">
                <span class="channel-version">当前版本：{{ ch.current_version ? 'v' + ch.current_version : '-' }}</span>
                <el-tag size="small" :type="channelStatus[ch.status]?.type || 'info'">
                  {{ channelStatus[ch.status]?.text || ch.status }}
                </el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无发布通道" :image-size="60" />
        </el-card>

        <el-card shadow="never" class="section-card">
          <template #header><span>最近活动</span></template>
          <el-timeline v-if="latestRecords.length">
            <el-timeline-item
              v-for="rec in latestRecords.slice(0, 5)"
              :key="rec.id"
              :timestamp="fmtTime(rec.create_time)"
              placement="top"
            >
              <div class="activity-item">
                <div class="activity-title">
                  <span class="activity-channel">{{ channelName(rec.channel_id) }}</span>
                  <el-tag size="small" type="success">v{{ rec.version }}</el-tag>
                </div>
                <div class="activity-summary">{{ rec.summary || '发布更新' }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无发布记录" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 新建项目对话框 -->
    <el-dialog v-model="showCreate" title="新建项目" width="480" @closed="resetCreateForm">
      <el-form :model="createForm" label-width="64">
        <el-form-item label="名称" required>
          <el-input v-model="createForm.name" placeholder="请输入项目名称" maxlength="255" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="项目描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Document, Folder, Plus, Promotion, Refresh } from '@element-plus/icons-vue'
import { annotationApi, projectApi, prototypeApi, publishApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const creating = ref(false)

// ── 数据 ──
const projects = ref<any[]>([])
const prototypeTotal = ref(0)
const annotationTotal = ref(0)
const channels = ref<any[]>([])
const latestRecords = ref<any[]>([])

// ── 统计卡片 ──
const statCards = computed(() => [
  { label: '项目总数', value: projects.value.length, icon: Folder, color: '#409eff' },
  { label: '原型总数', value: prototypeTotal.value, icon: Document, color: '#67c23a' },
  { label: '标注总数', value: annotationTotal.value, icon: ChatDotRound, color: '#e6a23c' },
  { label: '发布通道', value: channels.value.length, icon: Promotion, color: '#f56c6c' },
])

// ── 通道展示映射 ──
const channelTypeText: Record<string, string> = {
  development: '开发版',
  review: '评审版',
  production: '正式版',
}

const channelStatus: Record<string, { type: any; text: string }> = {
  published: { type: 'success', text: '已发布' },
  pending: { type: 'info', text: '未发布' },
  publishing: { type: 'warning', text: '发布中' },
  failed: { type: 'danger', text: '失败' },
}

// ── 工具函数 ──
const fmtTime = (t: string | null) => (t ? new Date(t).toLocaleString('zh-CN') : '-')

const channelName = (id: number) => channels.value.find((c) => c.id === id)?.name || `通道 #${id}`

// ── 数据加载（并行）──
async function load() {
  loading.value = true
  try {
    const [projRes, protoRes, annoRes, dashRes] = await Promise.all([
      projectApi.list(1, 100),
      prototypeApi.list({ page: 1, size: 1 }),
      annotationApi.list({ page: 1, size: 1 }),
      publishApi.dashboard(),
    ])
    projects.value = projRes.data?.data || []
    prototypeTotal.value = protoRes.data?.total || 0
    annotationTotal.value = annoRes.data?.total || 0
    const dash = dashRes.data || {}
    channels.value = dash.channels || []
    latestRecords.value = dash.latest_records || []
  } finally {
    loading.value = false
  }
}

// ── 新建项目 ──
const showCreate = ref(false)
const createForm = reactive({ name: '', description: '' })

function openCreate() {
  resetCreateForm()
  showCreate.value = true
}

function resetCreateForm() {
  createForm.name = ''
  createForm.description = ''
}

async function handleCreate() {
  if (!createForm.name.trim()) return ElMessage.warning('请输入项目名称')
  creating.value = true
  try {
    await projectApi.create({ name: createForm.name.trim(), description: createForm.description })
    ElMessage.success('项目创建成功')
    showCreate.value = false
    await load()
  } finally {
    creating.value = false
  }
}

// ── 跳转 ──
function goPrototypes(row: any) {
  router.push('/prototypes?project=' + row.id)
}

onMounted(load)
</script>

<style scoped>
.dashboard-page {
  min-height: 200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

/* 统计卡片 */
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: 600;
  line-height: 1.2;
  color: var(--el-text-color-primary);
}

.stat-label {
  margin-top: 2px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* 区块卡片 */
.section-card {
  border-radius: 8px;
  margin-bottom: 16px;
}

.clickable-table :deep(.el-table__row) {
  cursor: pointer;
}

/* 发布通道 */
.channel-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.channel-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
}

.channel-top,
.channel-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-top {
  margin-bottom: 8px;
}

.channel-name {
  font-weight: 500;
  font-size: 14px;
}

.channel-version {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* 最近活动 */
.activity-item {
  padding: 4px 0 8px;
}

.activity-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.activity-channel {
  font-weight: 500;
  font-size: 13px;
}

.activity-summary {
  font-size: 13px;
  color: var(--el-text-color-regular);
  word-break: break-all;
}
</style>
