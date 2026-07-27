<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:12px">
        <el-button v-if="currentProject" text @click="clearProject">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2 style="margin:0">{{ currentProject ? currentProject.name + ' — 知识库' : '团队知识库' }}</h2>
      </div>
      <div style="display:flex;gap:8px">
        <el-button v-if="currentProject" @click="openCreate('project')">项目知识条目</el-button>
        <el-button type="primary" @click="openCreate('team')">团队知识条目</el-button>
      </div>
    </div>

    <div style="margin-bottom:16px;display:flex;gap:12px;align-items:center">
      <el-input v-model="searchQuery" placeholder="搜索知识库..." clearable style="width:300px" prefix-icon="Search" />
      <el-select v-model="typeFilter" placeholder="类型" clearable style="width:140px">
        <el-option label="术语" value="term" />
        <el-option label="设计决策" value="decision" />
        <el-option label="约束条件" value="constraint" />
        <el-option label="用户反馈" value="user-feedback" />
        <el-option label="设计规则" value="design-rule" />
      </el-select>
      <el-select v-model="scopeFilter" placeholder="范围" clearable style="width:130px">
        <el-option label="项目知识库" value="project" />
        <el-option label="团队知识库" value="team" />
      </el-select>
      <span v-if="!currentProject && !scopeFilter" style="font-size:12px;color:#999">选择一个项目以查看项目级知识</span>
    </div>

    <!-- 项目选择（当前无项目时显示） -->
    <el-card v-if="!currentProject" shadow="never" style="margin-bottom:16px">
      <template #header>选择项目查看项目知识库</template>
      <el-table :data="projects" stripe @row-click="selectProject">
        <el-table-column prop="name" label="项目" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="知识条目" width="120">
          <template #default="{ row }"><el-tag>{{ row.prototype_count || 0 }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 知识条目列表 -->
    <el-table :data="filteredEntries" v-loading="loading" stripe style="width:100%">
      <el-table-column label="范围" width="80">
        <template #default="{ row }">
          <el-tag :type="row.scope === 'team' ? 'warning' : 'primary'" size="small">
            {{ row.scope === 'team' ? '团队' : '项目' }}
          </el-tag>
        </template>
      </el-table-column>
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
        <el-form-item label="范围" v-if="!editingId">
          <el-select v-model="form.scope">
            <el-option label="项目知识库" value="project" />
            <el-option label="团队知识库" value="team" />
          </el-select>
        </el-form-item>
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { knowledgeApi, projectApi } from '@/api'
import { ArrowLeft, Search } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const entries = ref<any[]>([])
const projects = ref<any[]>([])
const currentProject = ref<any>(null)
const searchQuery = ref('')
const typeFilter = ref('')
const scopeFilter = ref('')
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const loading = ref(false)
const form = reactive({ scope: 'project', type: 'decision', title: '', content: '', tags: '' })

const typeLabel = (t: string) => ({ term:'术语', decision:'设计决策', constraint:'约束', 'user-feedback':'反馈', 'design-rule':'规则' })[t] || t
const typeColor = (t: string) => ({ term:'#1677ff', decision:'#722ed1', constraint:'#fa8c16', 'user-feedback':'#52c41a', 'design-rule':'#eb2f96' })[t] || '#999'

const filteredEntries = computed(() => {
  let list = entries.value
  if (searchQuery.value) { const q = searchQuery.value.toLowerCase(); list = list.filter((e:any) => e.title?.toLowerCase().includes(q) || e.content?.toLowerCase().includes(q)) }
  if (typeFilter.value) list = list.filter((e:any) => e.type === typeFilter.value)
  if (scopeFilter.value) list = list.filter((e:any) => e.scope === scopeFilter.value)
  return list
})

async function load() {
  const projectId = route.query.project
  if (projectId) {
    const res = await projectApi.get(Number(projectId))
    currentProject.value = res.data
  } else {
    currentProject.value = null
    const res = await projectApi.list(1, 100)
    projects.value = res.data?.data || []
  }
  await loadEntries()
}

async function loadEntries() {
  loading.value = true
  try {
    const params: any = {}
    if (currentProject.value) {
      // 加载项目知识库 + 团队知识库
      const [projRes, teamRes] = await Promise.all([
        knowledgeApi.list({ project_id: currentProject.value.id, size: 100 }),
        knowledgeApi.list({ scope: 'team', size: 100 }),
      ])
      entries.value = [...(projRes.data?.data || []), ...(teamRes.data?.data || [])]
    } else {
      const res = await knowledgeApi.list({ scope: scopeFilter.value || undefined, size: 100 })
      entries.value = res.data?.data || []
    }
  } finally { loading.value = false }
}

function clearProject() { router.push('/knowledge') }

function selectProject(row: any) { router.push('/knowledge?project=' + row.id) }

function openCreate(scope: string) {
  editingId.value = null
  form.scope = scope
  form.type = 'decision'
  form.title = ''; form.content = ''; form.tags = ''
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  form.scope = row.scope || 'project'
  form.type = row.type
  form.title = row.title
  form.content = row.content
  form.tags = (row.tags || []).join(', ')
  dialogVisible.value = true
}

async function handleSave() {
  const data: any = {
    type: form.type,
    title: form.title,
    content: form.content,
    tags: form.tags.split(',').map((s: string) => s.trim()).filter(Boolean),
    scope: form.scope,
  }
  if (form.scope === 'project' && currentProject.value) {
    data.project_id = currentProject.value.id
  }
  if (editingId.value) {
    await knowledgeApi.update(editingId.value, data)
  } else {
    await knowledgeApi.create(data)
  }
  dialogVisible.value = false
  ElMessage.success('已保存')
  await loadEntries()
}

async function handleDelete(id: number) {
  await knowledgeApi.delete(id)
  ElMessage.success('已删除')
  await loadEntries()
}

onMounted(load)
</script>
