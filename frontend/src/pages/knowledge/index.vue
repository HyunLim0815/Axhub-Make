<template>
  <div>
    <!-- 顶部：标题 + 范围切换 + 搜索 + 操作 -->
    <div class="page-header">
      <div class="header-left">
        <h2 style="margin:0">知识库</h2>
        <el-radio-group v-model="scope" @change="onScopeChange">
          <el-radio-button value="project">项目知识库</el-radio-button>
          <el-radio-button value="team">团队知识库</el-radio-button>
        </el-radio-group>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchInput"
          placeholder="搜索知识库..."
          clearable
          style="width:280px"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" plain @click="openExtract">
          <el-icon><MagicStick /></el-icon>AI 抽取知识
        </el-button>
        <el-button type="primary" @click="openCreate">新建条目</el-button>
      </div>
    </div>

    <!-- 类型过滤 -->
    <div style="margin-bottom:16px">
      <el-select v-model="typeFilter" placeholder="全部类型" clearable style="width:160px" @change="onTypeChange">
        <el-option label="全部类型" value="" />
        <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
      </el-select>
      <span v-if="keyword" style="margin-left:12px;font-size:13px;color:var(--el-color-primary)">
        正在搜索「{{ keyword }}」，共 {{ total }} 条结果
      </span>
    </div>

    <!-- 列表 -->
    <el-table :data="entries" v-loading="loading" stripe style="width:100%">
      <el-table-column label="类型" width="110">
        <template #default="{ row }">
          <el-tag :type="typeTag(row.type)" size="small">{{ typeLabel(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
      <el-table-column prop="content" label="内容" min-width="240" show-overflow-tooltip />
      <el-table-column label="标签" width="200">
        <template #default="{ row }">
          <el-tag
            v-for="tag in (row.tags || [])"
            :key="tag"
            size="small"
            effect="plain"
            style="margin-right:4px;margin-bottom:2px"
          >{{ tag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.source || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!entries.length && !loading" description="暂无知识条目" />

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

    <!-- 新建 / 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑条目' : '新建条目'" width="620">
      <el-form :model="form" label-width="60px">
        <el-form-item label="类型" required>
          <el-select v-model="form.type" style="width:100%">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="请输入标题" maxlength="255" show-word-limit />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="form.content" type="textarea" :rows="6" placeholder="请输入内容" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="form.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入标签后回车添加"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="form.source" placeholder="来源（可选），如需求文档、评审记录" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- AI 抽取知识对话框 -->
    <el-dialog v-model="extractVisible" title="AI 抽取知识" width="640" :close-on-click-modal="false">
      <template v-if="!extractResult.length">
        <el-input
          v-model="extractText"
          type="textarea"
          :rows="8"
          placeholder="粘贴一段文本（评审记录、需求讨论、用户反馈等），AI 将自动提取知识条目..."
        />
        <el-input
          v-model="extractSource"
          placeholder="来源（可选），将自动附加到抽取的条目上"
          clearable
          style="margin-top:12px"
        />
      </template>
      <template v-else>
        <el-alert
          type="success"
          :closable="false"
          show-icon
          style="margin-bottom:12px"
          :title="`已抽取 ${extractResult.length} 条知识，勾选需要导入的条目`"
        />
        <div
          v-for="(item, idx) in extractResult"
          :key="idx"
          class="extract-item"
          :class="{ checked: extractChecked[idx] }"
        >
          <el-checkbox v-model="extractChecked[idx]" />
          <div class="extract-body">
            <div class="extract-head">
              <el-tag :type="typeTag(item.type)" size="small">{{ typeLabel(item.type) }}</el-tag>
              <span class="extract-title">{{ item.title }}</span>
            </div>
            <div class="extract-content">{{ item.content }}</div>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="closeExtract">取消</el-button>
        <template v-if="!extractResult.length">
          <el-button
            type="primary"
            :loading="extracting"
            :disabled="!extractText.trim()"
            @click="doExtract"
          >抽取</el-button>
        </template>
        <template v-else>
          <el-button @click="resetExtract">重新输入</el-button>
          <el-button type="primary" :loading="importing" @click="importExtracted">导入 {{ extractCheckedCount }} 条</el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { knowledgeApi } from '@/api'
import { MagicStick, Search } from '@element-plus/icons-vue'

type KnowledgeType = 'term' | 'decision' | 'constraint' | 'user-feedback' | 'design-rule'

// ── 过滤与列表状态 ──
const scope = ref<'project' | 'team'>('project')
const typeFilter = ref('')
const searchInput = ref('')
const keyword = ref('')
const entries = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)

// ── 新建 / 编辑 ──
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const emptyForm = () => ({ type: 'decision' as KnowledgeType, title: '', content: '', tags: [] as string[], source: '' })
const form = reactive(emptyForm())

// ── AI 抽取 ──
const extractVisible = ref(false)
const extractText = ref('')
const extractSource = ref('')
const extractResult = ref<any[]>([])
const extractChecked = ref<boolean[]>([])
const extracting = ref(false)
const importing = ref(false)

const typeOptions: { value: KnowledgeType; label: string }[] = [
  { value: 'term', label: '术语' },
  { value: 'decision', label: '决策' },
  { value: 'constraint', label: '约束' },
  { value: 'user-feedback', label: '用户反馈' },
  { value: 'design-rule', label: '设计规则' },
]

const typeLabel = (t: string) => typeOptions.find((o) => o.value === t)?.label || t

const TYPE_TAG_MAP: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
  term: 'primary',
  decision: 'success',
  constraint: 'warning',
  'user-feedback': 'danger',
  'design-rule': 'info',
}

const typeTag = (t: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' =>
  TYPE_TAG_MAP[t] || 'info'

const extractCheckedCount = computed(() => extractChecked.value.filter(Boolean).length)

// ── 数据加载 ──
async function load() {
  loading.value = true
  try {
    // 搜索模式：只传 q（后端全文搜索）
    if (keyword.value) {
      const res = await knowledgeApi.list({ q: keyword.value })
      entries.value = res.data?.data || []
      total.value = res.data?.total || 0
    } else {
      const params: Record<string, any> = { scope: scope.value, page: page.value, size: size.value }
      if (typeFilter.value) params.type = typeFilter.value
      const res = await knowledgeApi.list(params)
      entries.value = res.data?.data || []
      total.value = res.data?.total || 0
    }
  } finally {
    loading.value = false
  }
}

function onScopeChange() {
  clearSearch()
  page.value = 1
  load()
}

function onTypeChange() {
  clearSearch()
  page.value = 1
  load()
}

function onSizeChange() {
  page.value = 1
  load()
}

function clearSearch() {
  keyword.value = ''
  searchInput.value = ''
}

function handleSearch() {
  keyword.value = searchInput.value.trim()
  page.value = 1
  load()
}

// ── 新建 / 编辑 ──
function openCreate() {
  editingId.value = null
  Object.assign(form, emptyForm())
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  Object.assign(form, {
    type: row.type,
    title: row.title,
    content: row.content,
    tags: [...(row.tags || [])],
    source: row.source || '',
  })
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.title.trim()) return ElMessage.warning('请输入标题')
  if (!form.content.trim()) return ElMessage.warning('请输入内容')
  saving.value = true
  try {
    const data = {
      type: form.type,
      title: form.title.trim(),
      content: form.content.trim(),
      tags: form.tags,
      source: form.source.trim(),
    }
    if (editingId.value) {
      await knowledgeApi.update(editingId.value, data)
      ElMessage.success('已更新')
    } else {
      await knowledgeApi.create({ ...data, scope: scope.value })
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    await load()
  } catch {
    ElMessage.error('保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除知识条目「${row.title}」？`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  await knowledgeApi.delete(row.id)
  ElMessage.success('已删除')
  await load()
}

// ── AI 抽取 ──
function openExtract() {
  extractVisible.value = true
  resetExtract()
}

function resetExtract() {
  extractText.value = ''
  extractSource.value = ''
  extractResult.value = []
  extractChecked.value = []
}

function closeExtract() {
  extractVisible.value = false
  resetExtract()
}

async function doExtract() {
  if (!extractText.value.trim()) return
  extracting.value = true
  try {
    const res = await knowledgeApi.extract(extractText.value.trim(), extractSource.value.trim())
    const items: any[] = res.data?.entries || []
    if (!items.length) {
      ElMessage.info('未从文本中抽取到知识条目，请尝试更明确的文本')
      return
    }
    extractResult.value = items
    extractChecked.value = items.map(() => true)
  } catch {
    ElMessage.error('抽取失败，请稍后重试')
  } finally {
    extracting.value = false
  }
}

async function importExtracted() {
  const selected = extractResult.value.filter((_, idx) => extractChecked.value[idx])
  if (!selected.length) return ElMessage.warning('请至少勾选一条知识')
  importing.value = true
  try {
    let ok = 0
    let failed = 0
    for (const item of selected) {
      try {
        await knowledgeApi.create({
          type: item.type || 'decision',
          title: item.title,
          content: item.content,
          tags: item.tags || [],
          source: item.source || extractSource.value.trim(),
          scope: scope.value,
        })
        ok++
      } catch {
        failed++
      }
    }
    if (failed) {
      ElMessage.warning(`导入完成：成功 ${ok} 条，失败 ${failed} 条`)
    } else {
      ElMessage.success(`已导入 ${ok} 条知识`)
    }
    closeExtract()
    await load()
  } finally {
    importing.value = false
  }
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
.extract-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  margin-bottom: 10px;
  transition: border-color 0.2s, background-color 0.2s;
}
.extract-item.checked {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.extract-body {
  flex: 1;
  min-width: 0;
}
.extract-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.extract-title {
  font-weight: 500;
  color: var(--el-text-color-primary);
}
.extract-content {
  margin-top: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
