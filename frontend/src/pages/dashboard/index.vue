<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2 style="margin:0">项目</h2>
      <el-button type="primary" @click="showCreate = true">新建项目</el-button>
    </div>

    <el-table :data="projects" v-loading="loading" stripe style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column label="原型数" width="100">
        <template #default="{ row }">
          <el-tag>{{ row.prototype_count || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="$router.push('/prototypes?project=' + row.id)">进入</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="total > 0"
      v-model:current-page="page"
      v-model:page-size="size"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top:16px;justify-content:flex-end"
      @current-change="load"
    />

    <el-dialog v-model="showCreate" :title="editingId ? '编辑项目' : '新建项目'" width="480">
      <el-form :model="form">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="项目名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectApi } from '@/api'

const projects = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const editingId = ref<number | null>(null)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const form = reactive({ name: '', description: '' })

async function load() {
  loading.value = true
  try {
    const res = await projectApi.list(page.value, size.value)
    projects.value = res.data?.data || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

function openEdit(row: any) {
  editingId.value = row.id
  form.name = row.name
  form.description = row.description || ''
  showCreate.value = true
}

async function handleSave() {
  if (!form.name) return ElMessage.warning('请输入名称')
  if (editingId.value) {
    await projectApi.update(editingId.value, { name: form.name, description: form.description })
    ElMessage.success('已更新')
  } else {
    await projectApi.create({ name: form.name, description: form.description })
    ElMessage.success('已创建')
  }
  showCreate.value = false
  editingId.value = null
  form.name = ''; form.description = ''
  await load()
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await projectApi.delete(id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>
