<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2 style="margin:0">产品知识库</h2>
      <el-button type="primary" @click="openCreate">新增条目</el-button>
    </div>

    <div style="margin-bottom:16px;display:flex;gap:12px">
      <el-input v-model="searchQuery" placeholder="搜索知识库..." clearable style="width:300px" prefix-icon="Search" />
      <el-select v-model="typeFilter" placeholder="类型" clearable style="width:140px">
        <el-option label="术语" value="term" />
        <el-option label="设计决策" value="decision" />
        <el-option label="约束条件" value="constraint" />
        <el-option label="用户反馈" value="user-feedback" />
        <el-option label="设计规则" value="design-rule" />
      </el-select>
    </div>

    <el-table :data="filteredEntries" stripe style="width:100%">
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :color="typeColor(row.type)" size="small" effect="plain">{{ typeLabel(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="content" label="内容" show-overflow-tooltip />
      <el-table-column label="标签" width="200">
        <template #default="{ row }">
          <el-tag v-for="tag in (row.tags||[])" :key="tag" size="small" style="margin-right:4px">{{ tag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!filteredEntries.length && !loading" description="暂无知识条目" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑条目' : '新增条目'" width="600">
      <el-form :model="form">
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option label="术语" value="term" />
            <el-option label="设计决策" value="decision" />
            <el-option label="约束条件" value="constraint" />
            <el-option label="用户反馈" value="user-feedback" />
            <el-option label="设计规则" value="design-rule" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="form.content" type="textarea" :rows="6" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { knowledgeApi } from '@/api'
import { Search } from '@element-plus/icons-vue'

const entries = ref<any[]>([])
const searchQuery = ref('')
const typeFilter = ref('')
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const loading = ref(false)
const form = reactive({ type: 'decision', title: '', content: '', tags: '' })

const typeLabel = (t: string) => ({ term:'术语', decision:'设计决策', constraint:'约束', 'user-feedback':'反馈', 'design-rule':'规则' })[t] || t
const typeColor = (t: string) => ({ term:'#1677ff', decision:'#722ed1', constraint:'#fa8c16', 'user-feedback':'#52c41a', 'design-rule':'#eb2f96' })[t] || '#999'

const filteredEntries = computed(() => {
  let list = entries.value
  if (searchQuery.value) { const q = searchQuery.value.toLowerCase(); list = list.filter(e => e.title?.toLowerCase().includes(q) || e.content?.toLowerCase().includes(q)) }
  if (typeFilter.value) list = list.filter(e => e.type === typeFilter.value)
  return list
})

async function load() { loading.value = true; try { const r = await knowledgeApi.list(); entries.value = r.data?.data || [] } finally { loading.value = false } }
function openCreate() { editingId.value = null; form.type = 'decision'; form.title = ''; form.content = ''; form.tags = ''; dialogVisible.value = true }
function openEdit(row: any) { editingId.value = row.id; form.type = row.type; form.title = row.title; form.content = row.content; form.tags = (row.tags||[]).join(', '); dialogVisible.value = true }

async function handleSave() {
  const data = { type: form.type, title: form.title, content: form.content, tags: form.tags.split(',').map((s:string) => s.trim()).filter(Boolean) }
  if (editingId.value) await knowledgeApi.update(editingId.value, data); else await knowledgeApi.create(data)
  dialogVisible.value = false; ElMessage.success('已保存'); await load()
}

async function handleDelete(id: number) { await knowledgeApi.delete(id); ElMessage.success('已删除'); await load() }

onMounted(load)
</script>
