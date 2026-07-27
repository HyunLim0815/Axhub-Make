<template>
  <div>
    <n-page-header>
      <template #title>产品知识库</template>
      <template #extra>
        <n-button type="primary" @click="openCreate">新增条目</n-button>
      </template>
    </n-page-header>

    <n-space class="mt-4">
      <n-input v-model:value="searchQuery" placeholder="搜索知识库..." clearable style="width:300px" />
      <n-select v-model:value="typeFilter" :options="typeOptions" clearable placeholder="类型" style="width:150px" />
    </n-space>

    <n-list class="mt-4">
      <n-list-item v-for="entry in filteredEntries" :key="entry.id">
        <template #prefix>
          <n-tag :color="{ color: typeColor(entry.type) }">{{ typeLabel(entry.type) }}</n-tag>
        </template>
        <n-thing :title="entry.title" :description="entry.content?.slice(0,200)">
          <template #footer>
            <n-space>
              <n-tag v-for="tag in entry.tags" :key="tag" size="tiny">{{ tag }}</n-tag>
            </n-space>
          </template>
        </n-thing>
        <template #suffix>
          <n-button size="tiny" quaternary @click="openEdit(entry)">编辑</n-button>
          <n-button size="tiny" quaternary type="error" @click="handleDelete(entry.id)">删除</n-button>
        </template>
      </n-list-item>
      <n-empty v-if="!filteredEntries.length" description="暂无条目" style="padding:60px" />
    </n-list>

    <n-modal v-model:show="showModal" :title="editingId ? '编辑条目' : '新增条目'" style="width:600px">
      <n-form>
        <n-form-item label="类型">
          <n-select v-model:value="form.type" :options="typeOptions" />
        </n-form-item>
        <n-form-item label="标题">
          <n-input v-model:value="form.title" />
        </n-form-item>
        <n-form-item label="内容">
          <n-input v-model:value="form.content" type="textarea" rows="6" />
        </n-form-item>
        <n-form-item label="标签">
          <n-input v-model:value="form.tags" placeholder="逗号分隔" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSave">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { knowledgeApi } from '@/api'

const message = useMessage()
const entries = ref<any[]>([])
const searchQuery = ref('')
const typeFilter = ref<string | null>(null)
const showModal = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ type: 'decision', title: '', content: '', tags: '' })

const typeOptions = [
  { label: '术语', value: 'term' },
  { label: '设计决策', value: 'decision' },
  { label: '约束条件', value: 'constraint' },
  { label: '用户反馈', value: 'user-feedback' },
  { label: '设计规则', value: 'design-rule' },
]

const typeLabel = (t: string) => typeOptions.find(o => o.value === t)?.label || t
const typeColor = (t: string) => {
  const map: Record<string, string> = { term: '#1677ff', decision: '#722ed1', constraint: '#fa8c16', 'user-feedback': '#52c41a', 'design-rule': '#eb2f96' }
  return map[t] || '#999'
}

const filteredEntries = computed(() => {
  let list = entries.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(e => e.title?.toLowerCase().includes(q) || e.content?.toLowerCase().includes(q))
  }
  if (typeFilter.value) list = list.filter(e => e.type === typeFilter.value)
  return list
})

async function load() {
  const res = await knowledgeApi.list()
  entries.value = res.data?.data || []
}
function openCreate() { editingId.value = null; form.type = 'decision'; form.title = ''; form.content = ''; form.tags = ''; showModal.value = true }
function openEdit(entry: any) { editingId.value = entry.id; form.type = entry.type; form.title = entry.title; form.content = entry.content; form.tags = (entry.tags || []).join(', '); showModal.value = true }

async function handleSave() {
  const data = { type: form.type, title: form.title, content: form.content, tags: form.tags.split(',').map((s: string) => s.trim()).filter(Boolean) }
  if (editingId.value) await knowledgeApi.update(editingId.value, data)
  else await knowledgeApi.create(data)
  showModal.value = false; message.success('已保存'); await load()
}

async function handleDelete(id: number) {
  await knowledgeApi.delete(id); message.success('已删除'); await load()
}

onMounted(load)
</script>
