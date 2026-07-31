<template>
  <div>
    <!-- 顶部：标题 + 提交按钮 -->
    <div class="page-header">
      <div class="header-left">
        <h2 style="margin:0">审查报告</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openSubmit">
          <el-icon><Plus /></el-icon>提交审查报告
        </el-button>
      </div>
    </div>

    <!-- 列表 -->
    <el-table :data="reports" v-loading="loading" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column label="评分" width="90" align="center">
        <template #default="{ row }">
          <el-progress
            type="circle"
            :width="42"
            :stroke-width="5"
            :percentage="row.score || 0"
            :color="scoreColor"
            :format="formatScore"
          />
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="90" align="center">
        <template #default="{ row }">
          <span>{{ sourceLabel(row.source) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openView(row)">查看</el-button>
          <el-button size="small" type="primary" link @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!reports.length && !loading" description="暂无审查报告" />

    <el-pagination
      v-if="total > 0"
      v-model:current-page="page"
      v-model:page-size="size"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top:16px;justify-content:flex-end"
      @current-change="load"
      @size-change="onSizeChange"
    />

    <!-- 提交 / 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑审查报告' : '提交审查报告'"
      width="640"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="请输入审查标题" maxlength="255" show-word-limit />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="审查摘要（可选）" />
        </el-form-item>
        <el-form-item label="评分">
          <el-input-number v-model="form.score" :min="0" :max="100" :step="5" />
        </el-form-item>
        <el-form-item label="审查人">
          <el-select
            v-model="form.reviewers"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入审查人姓名后回车添加"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.categories" multiple placeholder="请选择审查分类" style="width:100%">
            <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="8" placeholder="审查内容（Markdown）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">
          {{ editingId ? '保存修改' : '提交' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="detailVisible" title="审查报告详情" width="680" top="6vh">
      <div v-loading="detailLoading" style="min-height:120px">
        <template v-if="detail">
          <div class="detail-head">
            <span class="detail-title">{{ detail.title }}</span>
            <el-tag :type="statusTag(detail.status)" size="small">{{ statusLabel(detail.status) }}</el-tag>
          </div>
          <div class="detail-meta">
            <span>评分：<b :style="{ color: scoreColor(detail.score || 0) }">{{ detail.score || 0 }}</b></span>
            <span>来源：{{ sourceLabel(detail.source) }}</span>
            <span>创建时间：{{ formatTime(detail.create_time) }}</span>
          </div>

          <div class="detail-block">
            <div class="detail-label">审查分类</div>
            <div v-if="(detail.categories || []).length" class="tags-wrap">
              <el-tag v-for="c in detail.categories" :key="c" size="small" effect="plain">
                {{ categoryLabel(c) }}
              </el-tag>
            </div>
            <span v-else class="detail-empty">—</span>
          </div>

          <div class="detail-block">
            <div class="detail-label">审查人</div>
            <div v-if="(detail.reviewers || []).length" class="tags-wrap">
              <el-tag v-for="r in detail.reviewers" :key="r" size="small" effect="plain" type="info">{{ r }}</el-tag>
            </div>
            <span v-else class="detail-empty">—</span>
          </div>

          <div class="detail-block">
            <div class="detail-label">摘要</div>
            <div class="detail-content">{{ detail.summary || '（无摘要）' }}</div>
          </div>

          <div class="detail-block">
            <div class="detail-label">审查内容</div>
            <div class="detail-content">{{ detail.content || '（无内容）' }}</div>
          </div>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { reviewReportApi } from '@/api'
import { Plus } from '@element-plus/icons-vue'

// ── 列表状态 ──
const loading = ref(false)
const reports = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)

// ── 提交 / 编辑 ──
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)

// ── 详情 ──
const detailVisible = ref(false)
const detailLoading = ref(false)
const detail = ref<any>(null)

const categoryOptions = [
  { value: 'function', label: '功能' },
  { value: 'security', label: '安全' },
  { value: 'ux', label: '体验 (UX)' },
  { value: 'accessibility', label: '无障碍' },
]

const emptyForm = () => ({
  title: '',
  summary: '',
  score: 80,
  reviewers: [] as string[],
  categories: [] as string[],
  content: '',
})
const form = reactive(emptyForm())

// ── 展示映射 ──
const STATUS_LABELS: Record<string, string> = { draft: '草稿', published: '已发布', archived: '已归档' }
const STATUS_TAGS: Record<string, 'info' | 'success' | 'warning' | 'danger'> = {
  draft: 'info',
  published: 'success',
  archived: 'danger',
}
const SOURCE_LABELS: Record<string, string> = { manual: '手动', ai: 'AI', axhub: 'Axhub' }
const statusLabel = (s: string) => STATUS_LABELS[s] || s
const statusTag = (s: string): 'info' | 'success' | 'warning' | 'danger' => STATUS_TAGS[s] || 'info'
const sourceLabel = (s: string) => SOURCE_LABELS[s] || s || '—'
const categoryLabel = (c: string) => categoryOptions.find((o) => o.value === c)?.label || c
const scoreColor = (p: number) => (p >= 80 ? '#67c23a' : p >= 60 ? '#e6a23c' : '#f56c6c')
const formatScore = (p: number) => `${p}`
const formatTime = (t?: string) => (t ? t.replace('T', ' ').slice(0, 16) : '—')

// ── 数据加载 ──
async function load() {
  loading.value = true
  try {
    const res = await reviewReportApi.list({ page: page.value, size: size.value })
    reports.value = res.data?.data || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

function onSizeChange() {
  page.value = 1
  load()
}

// ── 提交 / 编辑 ──
function openSubmit() {
  editingId.value = null
  Object.assign(form, emptyForm())
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    summary: row.summary || '',
    score: row.score ?? 80,
    reviewers: [...(row.reviewers || [])],
    categories: [...(row.categories || [])],
    content: row.content || '',
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.title.trim()) return ElMessage.warning('请输入标题')
  saving.value = true
  try {
    const data = {
      title: form.title.trim(),
      summary: form.summary.trim(),
      score: form.score,
      reviewers: form.reviewers,
      categories: form.categories,
      content: form.content,
    }
    if (editingId.value) {
      await reviewReportApi.update(editingId.value, data)
      ElMessage.success('已保存修改')
    } else {
      await reviewReportApi.submit(data)
      ElMessage.success('审查报告已提交')
    }
    dialogVisible.value = false
    await load()
  } catch {
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

// ── 查看详情 ──
async function openView(row: any) {
  detailVisible.value = true
  detailLoading.value = true
  detail.value = null
  try {
    const res = await reviewReportApi.get(row.id)
    detail.value = res.data || null
  } catch {
    ElMessage.error('加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

// ── 删除 ──
async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除审查报告「${row.title}」？`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  await reviewReportApi.delete(row.id)
  ElMessage.success('已删除')
  if (reports.value.length === 1 && page.value > 1) page.value -= 1
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.detail-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.detail-title {
  font-weight: 600;
  font-size: 16px;
  color: var(--el-text-color-primary);
}
.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-light);
  margin-bottom: 12px;
}
.detail-block {
  margin-bottom: 14px;
}
.detail-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
  margin-bottom: 6px;
}
.detail-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.7;
  color: var(--el-text-color-primary);
  background: var(--el-fill-color-light);
  border-radius: 6px;
  padding: 10px 12px;
}
.detail-empty {
  color: var(--el-text-color-placeholder);
}
.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
