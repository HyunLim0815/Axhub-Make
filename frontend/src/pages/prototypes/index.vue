<template>
  <div>
    <n-page-header>
      <template #title>原型列表</template>
      <template #extra>
        <n-button type="primary" @click="showCreate = true">新建原型</n-button>
      </template>
    </n-page-header>

    <n-data-table
      :columns="columns"
      :data="prototypes"
      :loading="loading"
      :pagination="pagination"
      class="mt-4"
    />

    <n-modal v-model:show="showCreate" title="新建原型">
      <n-card style="width:480px" title="新建原型" closable @close="showCreate = false">
        <n-form>
          <n-form-item label="名称">
            <n-input v-model:value="form.name" placeholder="原型名称" />
          </n-form-item>
          <n-form-item label="描述">
            <n-input v-model:value="form.description" type="textarea" rows="3" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showCreate = false">取消</n-button>
            <n-button type="primary" @click="handleCreate">创建</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, useMessage } from 'naive-ui'
import { prototypeApi } from '@/api'

const router = useRouter()
const message = useMessage()
const prototypes = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const form = reactive({ name: '', description: '' })
const pagination = reactive({ page: 1, pageSize: 10, pageCount: 1 })

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '描述', key: 'description', ellipsis: true },
  {
    title: '操作', width: 120,
    render(row: any) {
      return h(NButton, { text, onClick: () => router.push(`/prototypes/${row.id}`) }, '打开')
    },
  },
]

async function load() {
  loading.value = true
  try {
    const res = await prototypeApi.list(pagination.page, pagination.pageSize)
    prototypes.value = res.data.data || []
    pagination.pageCount = res.data.last_page || 1
  } finally { loading.value = false }
}

async function handleCreate() {
  if (!form.name) { message.warning('请输入名称'); return }
  await prototypeApi.create(form)
  showCreate.value = false
  form.name = ''; form.description = ''
  await load()
}

onMounted(load)
</script>
