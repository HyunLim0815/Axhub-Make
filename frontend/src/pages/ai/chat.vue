<template>
  <div class="ai-page">
    <el-row :gutter="16" class="ai-row">
      <!-- ── 左栏：对话区 ── -->
      <el-col :span="16" class="ai-col">
        <div class="chat-panel">
          <!-- 顶部：标题 + 模型选择（纯展示） -->
          <div class="chat-header">
            <div class="chat-header-left">
              <span class="chat-title">AI 助手</span>
              <el-tag size="small" type="success" effect="plain" round>在线</el-tag>
            </div>
            <el-select v-model="model" class="model-select" size="small">
              <el-option v-for="m in models" :key="m" :label="m" :value="m" />
            </el-select>
          </div>

          <!-- 消息列表 -->
          <div ref="msgListRef" class="msg-list">
            <el-empty
              v-if="!messages.length"
              description="开始对话，或点击下方快捷提示"
              :image-size="80"
            />
            <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
              <div class="msg-meta">
                <span class="msg-role">{{ msg.role === 'user' ? '你' : 'AI' }}</span>
                <el-tag v-if="msg.kind === 'review'" size="small" type="warning" effect="plain">
                  评审
                </el-tag>
              </div>
              <div class="msg-bubble">{{ msg.content }}</div>
            </div>
          </div>

          <!-- 快捷提示 chips -->
          <div class="quick-chips">
            <span class="quick-label">快捷提示：</span>
            <el-tag
              v-for="chip in quickChips"
              :key="chip.label"
              class="quick-chip"
              :type="chip.mode === 'review' ? 'warning' : undefined"
              effect="plain"
              @click="applyChip(chip)"
            >
              {{ chip.label }}
            </el-tag>
          </div>

          <!-- 底部输入区 -->
          <div class="chat-input">
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="3"
              resize="none"
              :disabled="loading"
              placeholder="输入需求，Enter 发送，Shift+Enter 换行"
              @keydown="onKeydown"
            />
            <el-button type="primary" :loading="loading" class="send-btn" @click="handleSend">
              发送
            </el-button>
          </div>
        </div>
      </el-col>

      <!-- ── 右栏：工具面板 ── -->
      <el-col :span="8" class="ai-col">
        <div class="side-panel">
          <!-- 1. Context Bundle -->
          <el-card shadow="never" class="tool-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">Context Bundle</span>
                <el-button
                  size="small"
                  type="primary"
                  plain
                  :loading="contextLoading"
                  @click="loadContext"
                >
                  加载上下文
                </el-button>
              </div>
            </template>

            <div v-if="bundle">
              <el-collapse v-model="ctxActive">
                <el-collapse-item
                  :title="`项目${bundle.project && Object.keys(bundle.project).length ? ' ✓' : ''}`"
                  name="project"
                >
                  <template v-if="bundle.project && Object.keys(bundle.project).length">
                    <div class="kv">
                      <span class="kv-key">名称</span>{{ bundle.project.name || '-' }}
                    </div>
                    <div class="kv">
                      <span class="kv-key">描述</span>{{ bundle.project.description || '-' }}
                    </div>
                  </template>
                  <div v-else class="muted-text">无项目上下文</div>
                </el-collapse-item>

                <el-collapse-item :title="`页面 (${bundle.pages?.length ?? 0})`" name="pages">
                  <pre v-if="bundle.pages?.length" class="ctx-json">{{
                    JSON.stringify(bundle.pages, null, 2)
                  }}</pre>
                  <div v-else class="muted-text">暂无页面数据</div>
                </el-collapse-item>

                <el-collapse-item
                  :title="`标注 (${bundle.annotations?.length ?? 0})`"
                  name="annotations"
                >
                  <div v-if="bundle.annotations?.length" class="ctx-list">
                    <div v-for="(a, idx) in bundle.annotations" :key="idx" class="ctx-item">
                      <span class="ctx-title">{{ a.title }}</span>
                      <span class="ctx-summary">{{ a.summary }}</span>
                    </div>
                  </div>
                  <div v-else class="muted-text">暂无标注</div>
                </el-collapse-item>

                <el-collapse-item title="知识库" name="knowledge">
                  <template v-if="bundle.knowledge">
                    <div class="kv">
                      <span class="kv-key">术语</span>{{ bundle.knowledge.terms?.length ?? 0 }}
                    </div>
                    <div class="kv">
                      <span class="kv-key">决策</span>{{ bundle.knowledge.decisions?.length ?? 0 }}
                    </div>
                    <div class="kv">
                      <span class="kv-key">约束</span>{{ bundle.knowledge.constraints?.length ?? 0 }}
                    </div>
                  </template>
                  <div v-else class="muted-text">暂无知识库</div>
                </el-collapse-item>

                <el-collapse-item title="原始 JSON" name="raw">
                  <pre class="ctx-json">{{ JSON.stringify(bundle, null, 2) }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
            <el-empty v-else description="点击按钮加载上下文" :image-size="50" />
          </el-card>

          <!-- 2. Prompt Pack -->
          <el-card shadow="never" class="tool-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">Prompt Pack</span>
              </div>
            </template>

            <div class="pack-row">
              <el-select v-model="packRole" class="pack-select">
                <el-option label="工程实现 (engineering)" value="engineering" />
                <el-option label="测试用例 (testing)" value="testing" />
                <el-option label="评审专家 (review)" value="review" />
              </el-select>
              <el-button type="primary" plain :loading="packLoading" @click="generatePack">
                生成
              </el-button>
            </div>

            <div v-if="packPrompt" class="pack-result">
              <div class="pack-toolbar">
                <el-tag size="small" effect="plain">{{ packRole }}</el-tag>
                <el-tooltip :content="copied ? '已复制' : '复制 Prompt'" placement="top">
                  <el-button size="small" circle :icon="CopyDocument" @click="copyPack" />
                </el-tooltip>
              </div>
              <pre class="pack-text">{{ packPrompt }}</pre>
            </div>
            <el-empty v-else description="选择角色并生成" :image-size="50" />
          </el-card>

          <!-- 3. AI 运行记录 -->
          <el-card shadow="never" class="tool-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">AI 运行记录</span>
                <el-button size="small" :loading="runsLoading" @click="loadRuns">刷新</el-button>
              </div>
            </template>

            <div v-if="runs.length" class="runs-list">
              <div v-for="run in runs" :key="run.id" class="run-item">
                <div class="run-info">
                  <div class="run-top">
                    <span class="run-name" :title="run.name">{{ run.name || run.agent_type }}</span>
                    <el-tag size="small" :type="statusType(run.status)">{{ run.status }}</el-tag>
                  </div>
                  <div class="run-sub">
                    <span class="run-agent">{{ run.agent_type }}</span>
                    <span class="run-time">{{ formatTime(run.create_time) }}</span>
                  </div>
                </div>
                <el-button
                  size="small"
                  type="primary"
                  plain
                  :loading="executingId === run.id"
                  @click="executeRun(run.id)"
                >
                  执行
                </el-button>
              </div>
            </div>
            <el-empty v-else description="暂无运行记录" :image-size="50" />
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { CopyDocument } from '@element-plus/icons-vue'
import { aiApi } from '@/api'

// ── 对话区 ──

const models = ['gpt-4o', 'gpt-4o-mini', 'o3-mini']
const model = ref('gpt-4o')

interface QuickChip {
  label: string
  text: string
  mode: 'chat' | 'review'
}

const quickChips: QuickChip[] = [
  {
    label: '生成原型结构',
    text: '请根据当前项目信息生成完整的原型结构，包括页面划分、核心功能和交互说明。',
    mode: 'chat',
  },
  {
    label: '评审当前原型',
    text: '请评审当前原型，从功能完整性、用户体验和一致性角度给出评审意见。',
    mode: 'review',
  },
  {
    label: '抽取知识',
    text: '请抽取当前标注中的知识条目（术语、决策、约束）。',
    mode: 'chat',
  },
]

interface ChatMsg {
  role: 'user' | 'assistant'
  content: string
  kind?: 'chat' | 'review'
}

const messages = ref<ChatMsg[]>([])
const inputText = ref('')
const loading = ref(false)
const pendingMode = ref<'chat' | 'review' | null>(null)
const msgListRef = ref<HTMLElement>()

function scrollToBottom() {
  nextTick(() => {
    const el = msgListRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function applyChip(chip: QuickChip) {
  inputText.value = chip.text
  pendingMode.value = chip.mode === 'review' ? 'review' : 'chat'
}

function onKeydown(e: KeyboardEvent) {
  // 回车发送，Shift+Enter 换行；isComposing 避免中文输入法候选确认时误发送
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault()
    handleSend()
  }
}

function formatAssistantContent(data: any): string {
  if (data == null || data === '') return '(无响应)'
  if (typeof data === 'string') return data
  if (typeof data.content === 'string') return data.content
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  const mode = pendingMode.value
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  pendingMode.value = null
  loading.value = true
  scrollToBottom()

  try {
    if (mode === 'review') {
      // 快捷评审 → aiApi.review
      const res = await aiApi.review(text)
      messages.value.push({
        role: 'assistant',
        content: formatAssistantContent(res.data),
        kind: 'review',
      })
    } else {
      // 普通对话 → aiApi.chat
      const res = await aiApi.chat(text)
      messages.value.push({ role: 'assistant', content: formatAssistantContent(res.data) })
    }
  } catch (e: any) {
    messages.value.push({ role: 'assistant', content: `请求失败：${e?.message || e}` })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// ── Context Bundle ──

const bundle = ref<any>(null)
const contextLoading = ref(false)
const ctxActive = ref<string[]>(['project'])

async function loadContext() {
  contextLoading.value = true
  try {
    const res = await aiApi.context()
    bundle.value = res.data || {}
    ctxActive.value = ['project']
    ElMessage.success('上下文已加载')
  } catch (e: any) {
    ElMessage.error(`加载上下文失败：${e?.message || e}`)
  } finally {
    contextLoading.value = false
  }
}

// ── Prompt Pack ──

const packRole = ref('engineering')
const packPrompt = ref('')
const packLoading = ref(false)
const copied = ref(false)

async function generatePack() {
  packLoading.value = true
  try {
    const res = await aiApi.promptPack(packRole.value)
    packPrompt.value = res.data?.prompt || '(无输出)'
    copied.value = false
  } catch (e: any) {
    ElMessage.error(`生成失败：${e?.message || e}`)
  } finally {
    packLoading.value = false
  }
}

async function copyPack() {
  if (!packPrompt.value) return
  try {
    await navigator.clipboard.writeText(packPrompt.value)
    copied.value = true
    ElMessage.success('已复制')
    setTimeout(() => (copied.value = false), 1500)
  } catch {
    ElMessage.warning('复制失败，请手动选择文本复制')
  }
}

// ── AI 运行记录 ──

interface RunItem {
  id: number
  name: string
  agent_type: string
  status: string
  create_time: string
  [key: string]: any
}

const runs = ref<RunItem[]>([])
const runsLoading = ref(false)
const executingId = ref<number | null>(null)

function statusType(status: string): any {
  const s = (status || '').toLowerCase()
  if (['completed', 'success', 'done'].includes(s)) return 'success'
  if (['running', 'in_progress', 'processing'].includes(s)) return 'warning'
  if (['failed', 'error', 'cancelled', 'canceled'].includes(s)) return 'danger'
  return 'info'
}

function formatTime(t?: string) {
  if (!t) return '-'
  const d = new Date(t)
  if (isNaN(d.getTime())) return String(t).slice(0, 19)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadRuns() {
  runsLoading.value = true
  try {
    const res = await aiApi.runs({ page: 1, size: 20 })
    runs.value = res.data?.data || []
  } catch (e: any) {
    ElMessage.error(`加载运行记录失败：${e?.message || e}`)
  } finally {
    runsLoading.value = false
  }
}

async function executeRun(id: number) {
  executingId.value = id
  try {
    const res = await aiApi.executeRun(id)
    ElMessage.success(
      `执行完成：${res.data?.name || `Run #${id}`}（${res.data?.status || 'ok'}）`
    )
    await loadRuns()
  } catch (e: any) {
    ElMessage.error(`执行失败：${e?.message || e}`)
  } finally {
    executingId.value = null
  }
}

onMounted(loadRuns)
</script>

<style scoped>
.ai-page {
  height: 100%;
}
.ai-row {
  height: 100%;
}
.ai-col {
  height: 100%;
}

/* ── 左栏：对话区 ── */
.chat-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}
.chat-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.chat-title {
  font-size: 16px;
  font-weight: 600;
}
.model-select {
  width: 160px;
}

.msg-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
}
.msg-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 16px;
}
.msg-row.user {
  align-items: flex-end;
}
.msg-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #909399;
}
.msg-role {
  font-weight: 500;
}
.msg-bubble {
  max-width: 76%;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  background: #f0f2f5;
  color: var(--el-text-color-primary);
}
.msg-row.user .msg-bubble {
  background: var(--el-color-primary);
  color: #fff;
}

.quick-chips {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}
.quick-label {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}
.quick-chip {
  cursor: pointer;
}

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
}
.chat-input .el-input {
  flex: 1;
}
.send-btn {
  height: 84px;
  width: 88px;
}

/* ── 右栏：工具面板 ── */
.side-panel {
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 4px;
}
.tool-card {
  flex-shrink: 0;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-title {
  font-weight: 600;
}

.kv {
  font-size: 13px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
}
.kv-key {
  display: inline-block;
  min-width: 44px;
  margin-right: 4px;
  color: #909399;
}
.muted-text {
  padding: 4px 0;
  font-size: 13px;
  color: #909399;
}
.ctx-json {
  margin: 0;
  padding: 8px;
  max-height: 220px;
  overflow: auto;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  font-size: 12px;
}
.ctx-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ctx-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 13px;
}
.ctx-title {
  font-weight: 500;
}
.ctx-summary {
  font-size: 12px;
  color: #909399;
}

.pack-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.pack-select {
  flex: 1;
}
.pack-result {
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
}
.pack-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  background: var(--el-fill-color-light);
}
.pack-text {
  margin: 0;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.runs-list {
  display: flex;
  flex-direction: column;
}
.run-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.run-item:last-child {
  border-bottom: none;
}
.run-info {
  flex: 1;
  min-width: 0;
}
.run-top {
  display: flex;
  align-items: center;
  gap: 6px;
}
.run-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 500;
}
.run-sub {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 2px;
  font-size: 12px;
  color: #909399;
}
</style>
