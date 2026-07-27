<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:12px">
        <el-button v-if="currentProject" text @click="$router.push('/')">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2 style="margin:0">{{ currentProject ? currentProject.name + ' — 原型' : '请选择项目' }}</h2>
      </div>
      <el-button v-if="currentProject" type="primary" @click="showCreate = true">新建原型</el-button>
    </div>

    <!-- 项目选择（无项目时显示） -->
    <el-card v-if="!currentProject" shadow="never">
      <template #header>选择一个项目</template>
      <el-table :data="projects" stripe @row-click="selectProject">
        <el-table-column prop="name" label="项目" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="原型数" width="100">
          <template #default="{ row }"><el-tag>{{ row.prototype_count || 0 }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 项目内的原型列表 -->
    <template v-else>
      <el-table :data="prototypes" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push('/prototypes/' + row.id)">打开</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!prototypes.length && !loading" description="暂无原型，点击右上角新建" />

      <el-dialog v-model="showCreate" title="新建原型" width="480">
        <el-form :model="form">
          <el-form-item label="名称" required>
            <el-input v-model="form.name" placeholder="原型名称" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCreate = false">取消</el-button>
          <el-button type="primary" @click="handleCreate">创建</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectApi, prototypeApi } from '@/api'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const projects = ref<any[]>([])
const prototypes = ref<any[]>([])
const currentProject = ref<any>(null)
const loading = ref(false)
const showCreate = ref(false)
const form = reactive({ name: '', description: '' })

async function load() {
  const projectId = route.query.project
  if (projectId) {
    const res = await projectApi.get(Number(projectId))
    currentProject.value = res.data
    await loadPrototypes()
  } else {
    const res = await projectApi.list()
    projects.value = res.data?.data || []
  }
}

async function loadPrototypes() {
  if (!currentProject.value) return
  loading.value = true
  try {
    const res = await projectApi.listPrototypes(currentProject.value.id)
    prototypes.value = res.data?.data || []
  } finally { loading.value = false }
}

function selectProject(row: any) {
  router.push('/prototypes?project=' + row.id)
}

async function handleCreate() {
  if (!form.name) return ElMessage.warning('请输入名称')
  await projectApi.createPrototype(currentProject.value.id, form.name)
  showCreate.value = false
  form.name = ''; form.description = ''
  ElMessage.success('创建成功')
  await loadPrototypes()
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await prototypeApi.delete(id)
  ElMessage.success('已删除')
  await loadPrototypes()
}

onMounted(load)
</script>
