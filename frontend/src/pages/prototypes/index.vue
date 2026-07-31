<template>
  <div class="prototypes-page" v-loading="loading">
    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2 class="page-title">{{ projectId ? (currentProject?.name || '项目原型') : '选择项目' }}</h2>
      </div>
      <div class="header-right">
        <el-button v-if="!projectId" type="primary" :icon="Plus" @click="openProjectDialog">
          新建项目
        </el-button>
        <el-button v-else type="primary" :icon="Plus" @click="openPrototypeDialog">
          新建原型
        </el-button>
      </div>
    </div>

    <!-- 项目选择模式（URL 无 ?project=） -->
    <template v-if="!projectId">
      <el-empty
        v-if="!projects.length && !loading"
        description="暂无项目，点击新建"
        :image-size="100"
      />
      <el-row :gutter="16">
        <el-col v-for="p in projects" :key="p.id" :xs="24" :sm="12" :md="8" :lg="6">
          <el-card
            class="project-card"
            shadow="hover"
            @click="selectProject(p)"
          >
            <div class="project-name">
              <el-icon :size="18"><Folder /></el-icon>
              <span class="project-name-text">{{ p.name }}</span>
            </div>
            <div class="project-desc" :title="p.description || '暂无描述'">
              {{ p.description || '暂无描述' }}
            </div>
            <div class="project-meta">
              <el-tag size="small" type="info">{{ p.prototype_count || 0 }} 个原型</el-tag>
              <span class="project-time">创建于 {{ fmtTime(p.create_time) }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <!-- 原型列表模式（URL 有 ?project=） -->
    <template v-else>
      <el-table :data="prototypes" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140">
          <template #default="{ row }">
            <span style="font-weight: 500">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip min-width="160">
          <template #default="{ row }">{{ row.description || '-' }}</template>
        </el-table-column>
        <el-table-column prop="page_id" label="页面ID" width="100">
          <template #default="{ row }">{{ row.page_id || '-' }}</template>
        </el-table-column>
        <el-table-column label="更新时间" width="170">
          <template #default="{ row }">{{ fmtTime(row.update_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openPrototype(row)">打开</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty
        v-if="!prototypes.length && !loading"
        description="暂无原型，点击右上角新建"
        :image-size="100"
        style="margin-top: 24px"
      />
    </template>

    <!-- 新建原型对话框 -->
    <el-dialog v-model="showPrototypeDialog" title="新建原型" width="480" @closed="resetPrototypeForm">
      <el-form :model="prototypeForm" label-width="64">
        <el-form-item label="名称" required>
          <el-input v-model="prototypeForm.name" placeholder="请输入原型名称" maxlength="255" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="prototypeForm.description"
            type="textarea"
            :rows="3"
            placeholder="原型描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPrototypeDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreatePrototype">创建</el-button>
      </template>
    </el-dialog>

    <!-- 新建项目对话框 -->
    <el-dialog v-model="showProjectDialog" title="新建项目" width="480" @closed="resetProjectForm">
      <el-form :model="projectForm" label-width="64">
        <el-form-item label="名称" required>
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" maxlength="255" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="项目描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProjectDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateProject">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Folder, Plus } from '@element-plus/icons-vue'
import { projectApi, prototypeApi } from '@/api'

const route = useRoute()
const router = useRouter()

// ── 状态 ──
const projectId = ref<number | null>(null)
const currentProject = ref<any>(null)
const projects = ref<any[]>([])
const prototypes = ref<any[]>([])
const loading = ref(false)
const creating = ref(false)

// ── 对话框 ──
const showProjectDialog = ref(false)
const showPrototypeDialog = ref(false)
const projectForm = reactive({ name: '', description: '' })
const prototypeForm = reactive({ name: '', description: '' })

// ── 工具函数 ──
const fmtTime = (t: string | null) => (t ? new Date(t).toLocaleString('zh-CN') : '-')

// ── 数据加载：根据 URL ?project= 切换模式 ──
async function load() {
  const pid = route.query.project ? Number(route.query.project) : null
  projectId.value = pid
  loading.value = true
  try {
    if (pid) {
      const [pRes, protoRes] = await Promise.all([
        projectApi.get(pid),
        projectApi.listPrototypes(pid),
      ])
      currentProject.value = pRes.data
      prototypes.value = protoRes.data?.data || []
    } else {
      currentProject.value = null
      const res = await projectApi.list(1, 100)
      projects.value = res.data?.data || []
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

watch(() => route.query.project, load)
onMounted(load)

// ── 导航 ──
function goBack() {
  // 原型列表模式 → 返回项目选择；项目选择模式 → 返回仪表盘
  router.push(projectId.value ? '/prototypes' : '/')
}

function selectProject(p: any) {
  router.push('/prototypes?project=' + p.id)
}

function openPrototype(row: any) {
  router.push('/prototypes/' + row.id)
}

// ── 新建原型 ──
function openPrototypeDialog() {
  resetPrototypeForm()
  showPrototypeDialog.value = true
}

function resetPrototypeForm() {
  prototypeForm.name = ''
  prototypeForm.description = ''
}

async function handleCreatePrototype() {
  if (!prototypeForm.name.trim()) return ElMessage.warning('请输入原型名称')
  if (!projectId.value) return
  creating.value = true
  try {
    await projectApi.createPrototype(projectId.value, prototypeForm.name.trim())
    ElMessage.success('创建成功')
    showPrototypeDialog.value = false
    await load()
  } finally {
    creating.value = false
  }
}

// ── 新建项目 ──
function openProjectDialog() {
  resetProjectForm()
  showProjectDialog.value = true
}

function resetProjectForm() {
  projectForm.name = ''
  projectForm.description = ''
}

async function handleCreateProject() {
  if (!projectForm.name.trim()) return ElMessage.warning('请输入项目名称')
  creating.value = true
  try {
    await projectApi.create({
      name: projectForm.name.trim(),
      description: projectForm.description,
    })
    ElMessage.success('项目创建成功')
    showProjectDialog.value = false
    await load()
  } finally {
    creating.value = false
  }
}

// ── 删除原型 ──
async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除原型「${row.name}」？此操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return // 用户取消
  }
  try {
    await prototypeApi.delete(row.id)
    ElMessage.success('删除成功')
    await load()
  } catch (e) {
    console.error(e)
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.prototypes-page {
  min-height: 200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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
  gap: 8px;
}

/* 项目卡片 */
.project-card {
  border-radius: 8px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.project-card:hover {
  transform: translateY(-2px);
}

.project-name {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  color: var(--el-color-primary);
}

.project-name-text {
  font-weight: 600;
  font-size: 15px;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  min-height: 38px;
  line-height: 1.5;
  margin-bottom: 12px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.project-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.project-time {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
</style>
