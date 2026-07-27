<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2 style="margin:0">原型</h2>
      <el-button type="primary" @click="dialogVisible = true">新建原型</el-button>
    </div>

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
    <el-pagination
      v-if="total > 0"
      v-model:current-page="page"
      v-model:page-size="size"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top:16px;justify-content:flex-end"
      @current-change="load"
    />

    <el-dialog v-model="dialogVisible" title="新建原型" width="480">
      <el-form :model="form">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="原型名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { prototypeApi } from '@/api'

const prototypes = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const form = reactive({ name: '', description: '' })

async function load() {
  loading.value = true
  try {
    const res = await prototypeApi.list(page.value, size.value)
    prototypes.value = res.data?.data || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

async function handleCreate() {
  if (!form.name) return ElMessage.warning('请输入名称')
  await prototypeApi.create({ name: form.name, description: form.description })
  dialogVisible.value = false
  form.name = ''; form.description = ''
  ElMessage.success('创建成功')
  await load()
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await prototypeApi.delete(id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>
