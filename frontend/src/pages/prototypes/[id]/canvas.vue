<template>
  <div class="canvas-page" v-loading="loading">
    <!-- 顶部工具栏 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2 class="page-title">{{ prototype?.name || '原型画布' }}</h2>
      </div>
      <div class="header-right">
        <el-radio-group v-model="device" size="small">
          <el-radio-button value="desktop">桌面</el-radio-button>
          <el-radio-button value="tablet">平板</el-radio-button>
          <el-radio-button value="mobile">手机</el-radio-button>
        </el-radio-group>
        <el-button type="primary" :icon="MagicStick" @click="openAiDialog">AI 生成标注</el-button>
      </div>
    </div>

    <el-row :gutter="16">
      <!-- 左侧画布区 -->
      <el-col :span="17">
        <el-card shadow="never" class="canvas-card">
          <template #header><span>原型信息</span></template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="名称">{{ prototype?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ prototype?.description || '-' }}</el-descriptions-item>
            <el-descriptions-item label="页面ID">{{ prototype?.page_id ?? '-' }}</el-descriptions-item>
          </el-descriptions>

          <!-- 设备外壳 -->
          <template v-if="hasCanvas">
            <div class="device-frame" :class="`device-${device}`">
              <iframe
                :src="previewUrl"
                class="device-iframe"
                :style="{ width: deviceWidth }"
                frameborder="0"
                allowfullscreen
              />
            </div>
          </template>
          <el-empty v-else description="canvas_data 为空，暂无画布内容" :image-size="100" />
        </el-card>
      </el-col>

      <!-- 右侧标注区 -->
      <el-col :span="7">
        <el-card shadow="never" class="side-card">
          <el-tabs v-model="activeTab">
            <!-- 标注标签页 -->
            <el-tab-pane label="标注" name="annotations">
              <div class="filter-bar">
                <el-radio-group v-model="scopeFilter" size="small">
                  <el-radio-button value="all">全部</el-radio-button>
                  <el-radio-button value="element">元素级</el-radio-button>
                  <el-radio-button value="page">页面级</el-radio-button>
                </el-radio-group>
                <el-button type="primary" size="small" :icon="Plus" @click="openAnnDialog()">新建</el-button>
              </div>

              <el-timeline v-if="filteredAnnotations.length" class="ann-timeline">
                <el-timeline-item
                  v-for="ann in filteredAnnotations"
                  :key="ann.id"
                  :color="ann.color || '#409EFF'"
                  :timestamp="fmtTime(ann.create_time || ann.update_time)"
                  placement="top"
                >
                  <div class="ann-item">
                    <div class="ann-head">
                      <span class="ann-title" :title="ann.title">{{ ann.title || '未命名标注' }}</span>
                      <el-tag size="small" :type="scopeTagType(ann.scope)">{{ scopeLabel(ann.scope) }}</el-tag>
                    </div>
                    <div class="ann-text">{{ ann.annotation_text || '-' }}</div>
                    <div class="ann-actions">
                      <el-button size="small" link type="primary" :icon="Edit" @click="openAnnDialog(ann)">编辑</el-button>
                      <el-button size="small" link type="danger" :icon="Delete" @click="handleDeleteAnn(ann)">删除</el-button>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-else description="暂无标注" :image-size="80" />
            </el-tab-pane>

            <!-- 版本标签页 -->
            <el-tab-pane label="版本" name="versions">
              <div class="filter-bar">
                <span class="panel-title">版本历史</span>
                <el-button type="primary" size="small" :icon="Plus" @click="openVersionDialog">创建版本</el-button>
              </div>

              <el-timeline v-if="versions.length" class="ann-timeline">
                <el-timeline-item
                  v-for="v in versions"
                  :key="v.id"
                  :timestamp="fmtTime(v.create_time)"
                  placement="top"
                >
                  <div class="ver-item">
                    <div class="ver-head">
                      <span class="ver-badge">v{{ v.version ?? v.id }}</span>
                      <el-tag :type="statusType(v.status)" size="small">{{ v.status || 'draft' }}</el-tag>
                      <el-button size="small" link type="warning" @click="handleRollback(v)">回滚</el-button>
                    </div>
                    <div class="ver-summary">{{ v.summary || '-' }}</div>
                    <div v-if="tagsOf(v).length" class="ver-tags">
                      <el-tag v-for="(t, i) in tagsOf(v)" :key="i" size="small" type="info" effect="plain">{{ t }}</el-tag>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-else description="暂无版本" :image-size="80" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI 生成标注对话框 -->
    <el-dialog v-model="showAiDialog" title="AI 生成标注" width="560">
      <el-input
        v-model="aiPrompt"
        type="textarea"
        :rows="3"
        placeholder="描述需要生成的标注内容，例如：为「登录表单」生成一条交互说明标注"
      />
      <div class="ai-toolbar">
        <el-button type="primary" :loading="aiLoading" :icon="MagicStick" @click="handleAiGenerate">
          生成
        </el-button>
      </div>
      <div v-if="aiGenerated" class="ai-result">
        <div class="ai-result-header">
          <span>生成结果</span>
          <el-button type="primary" size="small" :loading="aiCreating" @click="handleAiCreate">一键创建标注</el-button>
        </div>
        <pre class="ai-result-text">{{ aiResult }}</pre>
      </div>
    </el-dialog>

    <!-- 新建 / 编辑标注对话框 -->
    <el-dialog v-model="showAnnDialog" :title="editingId ? '编辑标注' : '新建标注'" width="480">
      <el-form :model="annForm" label-width="88">
        <el-form-item label="标题">
          <el-input v-model="annForm.title" placeholder="标注标题（可选）" maxlength="255" />
        </el-form-item>
        <el-form-item label="标注文本" required>
          <el-input v-model="annForm.annotation_text" type="textarea" :rows="4" placeholder="标注内容" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="annForm.color" />
        </el-form-item>
        <el-form-item label="作用范围">
          <el-select v-model="annForm.scope" style="width: 160px">
            <el-option label="元素级" value="element" />
            <el-option label="页面级" value="page" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAnnDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveAnn">
          {{ editingId ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建版本对话框 -->
    <el-dialog v-model="showVersionDialog" title="创建版本" width="460">
      <el-form label-width="64">
        <el-form-item label="说明" required>
          <el-input
            v-model="versionForm.summary"
            type="textarea"
            :rows="3"
            placeholder="本次版本变更说明"
            maxlength="500"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showVersionDialog = false">取消</el-button>
        <el-button type="primary" :loading="creatingVersion" @click="handleCreateVersion">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, Edit, MagicStick, Plus } from '@element-plus/icons-vue'
import { aiApi, annotationApi, prototypeApi } from '@/api'

const route = useRoute()
const router = useRouter()

const id = Number(route.params.id)

// ── 状态 ──
const loading = ref(false)
const prototype = ref<any>(null)
const annotations = ref<any[]>([])
const versions = ref<any[]>([])
const activeTab = ref('annotations')

// ── 设备外壳 ──
const device = ref<'desktop' | 'tablet' | 'mobile'>('desktop')
const deviceWidth = computed(() => {
  switch (device.value) {
    case 'tablet':
      return '768px'
    case 'mobile':
      return '390px'
    default:
      return '100%'
  }
})
const previewUrl = computed(() => `/preview/${id}`)
const hasCanvas = computed(() => {
  const cd = prototype.value?.canvas_data
  return cd != null && cd !== ''
})

// ── 标注过滤 ──
const scopeFilter = ref<'all' | 'element' | 'page'>('all')
const filteredAnnotations = computed(() => {
  if (scopeFilter.value === 'all') return annotations.value
  return annotations.value.filter((a) => a.scope === scopeFilter.value)
})

// ── AI 生成标注 ──
const showAiDialog = ref(false)
const aiPrompt = ref('')
const aiResult = ref('')
const aiGenerated = ref(false)
const aiLoading = ref(false)
const aiCreating = ref(false)

// ── 标注表单 ──
const showAnnDialog = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const annForm = reactive({
  title: '',
  annotation_text: '',
  color: '#409EFF',
  scope: 'element',
})

// ── 版本表单 ──
const showVersionDialog = ref(false)
const creatingVersion = ref(false)
const versionForm = reactive({ summary: '' })

// ── 工具函数 ──
const fmtTime = (t: string | null) => (t ? new Date(t).toLocaleString('zh-CN') : '-')

function scopeLabel(scope?: string) {
  if (scope === 'element') return '元素级'
  if (scope === 'page') return '页面级'
  return scope || '-'
}

function scopeTagType(scope?: string): 'primary' | 'warning' {
  return scope === 'page' ? 'warning' : 'primary'
}

function statusType(status?: string): 'success' | 'info' {
  return status === 'released' || status === 'active' ? 'success' : 'info'
}

function tagsOf(v: any): string[] {
  const t = v?.tags
  if (!t) return []
  if (Array.isArray(t)) return t.map(String)
  if (typeof t === 'string') {
    try {
      const parsed = JSON.parse(t)
      if (Array.isArray(parsed)) return parsed.map(String)
    } catch {
      /* 不是 JSON，按逗号分割 */
    }
    return t.split(',').map((s) => s.trim()).filter(Boolean)
  }
  return []
}

// ── 数据加载 ──
async function loadAnnotations() {
  try {
    const res = await annotationApi.list({ prototype_id: id })
    annotations.value = res.data?.data || []
  } catch (e) {
    console.error(e)
    ElMessage.error('标注加载失败')
  }
}

async function loadVersions() {
  try {
    const res = await annotationApi.versions(id)
    versions.value = res.data?.data || []
  } catch (e) {
    console.error(e)
    ElMessage.error('版本加载失败')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const [p, a, v] = await Promise.allSettled([
      prototypeApi.get(id),
      annotationApi.list({ prototype_id: id }),
      annotationApi.versions(id),
    ])
    if (p.status === 'fulfilled') prototype.value = p.value.data
    if (a.status === 'fulfilled') annotations.value = a.value.data?.data || []
    if (v.status === 'fulfilled') versions.value = v.value.data?.data || []
    if (p.status === 'rejected' || a.status === 'rejected' || v.status === 'rejected') {
      ElMessage.warning('部分数据加载失败')
    }
  } finally {
    loading.value = false
  }
})

// ── 导航 ──
function goBack() {
  router.push('/prototypes')
}

// ── AI 生成标注 ──
function openAiDialog() {
  aiPrompt.value = ''
  aiResult.value = ''
  aiGenerated.value = false
  showAiDialog.value = true
}

function normalizeAiResult(annotation: any): string {
  if (annotation == null) return ''
  if (typeof annotation === 'string') return annotation
  try {
    return JSON.stringify(annotation, null, 2)
  } catch {
    return String(annotation)
  }
}

async function handleAiGenerate() {
  if (!aiPrompt.value.trim()) return ElMessage.warning('请输入标注 prompt')
  aiLoading.value = true
  try {
    const res = await aiApi.annotate(aiPrompt.value.trim())
    aiResult.value = normalizeAiResult(res.data?.annotation)
    aiGenerated.value = true
    if (!aiResult.value) ElMessage.warning('AI 未返回标注内容')
  } catch (e) {
    console.error(e)
    ElMessage.error('AI 标注生成失败')
  } finally {
    aiLoading.value = false
  }
}

async function handleAiCreate() {
  if (!aiResult.value.trim()) return ElMessage.warning('暂无生成结果')
  aiCreating.value = true
  try {
    await annotationApi.create({
      prototype_id: id,
      title: 'AI 标注',
      annotation_text: aiResult.value,
      scope: 'element',
      color: '#409EFF',
    })
    ElMessage.success('标注已创建')
    showAiDialog.value = false
    await loadAnnotations()
  } catch (e) {
    console.error(e)
    ElMessage.error('创建标注失败')
  } finally {
    aiCreating.value = false
  }
}

// ── 标注新增 / 编辑 / 删除 ──
function openAnnDialog(ann?: any) {
  editingId.value = ann ? ann.id : null
  annForm.title = ann?.title || ''
  annForm.annotation_text = ann?.annotation_text || ''
  annForm.color = ann?.color || '#409EFF'
  annForm.scope = ann?.scope || 'element'
  showAnnDialog.value = true
}

async function handleSaveAnn() {
  if (!annForm.annotation_text.trim()) return ElMessage.warning('请输入标注文本')
  saving.value = true
  try {
    const payload = {
      prototype_id: id,
      title: annForm.title.trim(),
      annotation_text: annForm.annotation_text.trim(),
      color: annForm.color,
      scope: annForm.scope,
    }
    if (editingId.value) {
      await annotationApi.update(editingId.value, payload)
      ElMessage.success('标注已更新')
    } else {
      await annotationApi.create(payload)
      ElMessage.success('标注已创建')
    }
    showAnnDialog.value = false
    await loadAnnotations()
  } catch (e) {
    console.error(e)
    ElMessage.error('保存标注失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteAnn(ann: any) {
  try {
    await ElMessageBox.confirm('确定删除该标注？', '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return // 用户取消
  }
  try {
    await annotationApi.delete(ann.id)
    ElMessage.success('标注已删除')
    await loadAnnotations()
  } catch (e) {
    console.error(e)
    ElMessage.error('删除标注失败')
  }
}

// ── 版本创建 / 回滚 ──
function openVersionDialog() {
  versionForm.summary = ''
  showVersionDialog.value = true
}

async function handleCreateVersion() {
  if (!versionForm.summary.trim()) return ElMessage.warning('请输入版本说明')
  creatingVersion.value = true
  try {
    await annotationApi.createVersion(id, { summary: versionForm.summary.trim() })
    ElMessage.success('版本已创建')
    showVersionDialog.value = false
    await loadVersions()
  } catch (e) {
    console.error(e)
    ElMessage.error('创建版本失败')
  } finally {
    creatingVersion.value = false
  }
}

async function handleRollback(v: any) {
  const version = v.version ?? v.id
  try {
    await ElMessageBox.confirm(`确定回滚到 v${version}？当前标注将被替换为该版本的内容。`, '回滚确认', {
      type: 'warning',
      confirmButtonText: '回滚',
      cancelButtonText: '取消',
    })
  } catch {
    return // 用户取消
  }
  try {
    await annotationApi.rollback(id, version)
    ElMessage.success('回滚成功')
    await loadAnnotations()
    await loadVersions()
  } catch (e) {
    console.error(e)
    ElMessage.error('回滚失败')
  }
}
</script>

<style scoped>
.canvas-page {
  min-height: 200px;
}

/* 顶部工具栏 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 8px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 左侧画布 */
.canvas-card {
  border-radius: 8px;
}

/* 设备外壳 */
.device-frame {
  margin-top: 16px;
  min-height: 600px;
  background: #fff;
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.device-iframe {
  height: 600px;
  border: none;
  border-radius: 8px;
  background: #fff;
  transition: width 0.2s ease;
}

/* 平板 / 手机外壳模拟 */
.device-tablet .device-iframe,
.device-mobile .device-iframe {
  border: 8px solid #1f2329;
  border-top-width: 12px;
  border-radius: 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
}

/* 右侧面板 */
.side-card {
  border-radius: 8px;
  height: 100%;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
  flex-wrap: wrap;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.ann-timeline {
  max-height: 520px;
  overflow-y: auto;
  padding-right: 4px;
}

.ann-item,
.ver-item {
  background: var(--el-fill-color-light);
  border-radius: 8px;
  padding: 10px 12px;
}

.ann-head,
.ver-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.ann-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ann-text {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ann-actions {
  margin-top: 6px;
  text-align: right;
}

.ver-badge {
  font-size: 14px;
  font-weight: 700;
  color: var(--el-color-primary);
}

.ver-summary {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  word-break: break-word;
}

.ver-tags {
  margin-top: 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* AI 生成标注 */
.ai-toolbar {
  margin-top: 12px;
}

.ai-result {
  margin-top: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-fill-color-lighter);
  padding: 12px;
}

.ai-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
}

.ai-result-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  max-height: 240px;
  overflow-y: auto;
}
</style>
