<template>
  <div>
    <n-page-header>
      <template #title>设置</template>
    </n-page-header>

    <n-card title="AI 配置" class="mt-4">
      <n-form label-placement="left">
        <n-form-item label="API Key">
          <n-input v-model:value="config.aiApiKey" type="password" placeholder="sk-..." />
        </n-form-item>
        <n-form-item label="Base URL">
          <n-input v-model:value="config.aiBaseUrl" placeholder="https://api.openai.com/v1" />
        </n-form-item>
        <n-form-item label="模型">
          <n-input v-model:value="config.aiModel" placeholder="gpt-4o" />
        </n-form-item>
        <n-form-item label="简单任务模型">
          <n-input v-model:value="config.aiSimpleModel" placeholder="gpt-4o-mini" />
        </n-form-item>
        <n-form-item label="复杂任务模型">
          <n-input v-model:value="config.aiComplexModel" placeholder="o3-mini" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button type="primary" @click="handleSave">保存配置</n-button>
        </n-space>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useMessage } from 'naive-ui'

const message = useMessage()
const config = reactive({
  aiApiKey: localStorage.getItem('ai_api_key') || '',
  aiBaseUrl: localStorage.getItem('ai_base_url') || 'https://api.openai.com/v1',
  aiModel: localStorage.getItem('ai_model') || 'gpt-4o',
  aiSimpleModel: localStorage.getItem('ai_simple_model') || 'gpt-4o-mini',
  aiComplexModel: localStorage.getItem('ai_complex_model') || 'o3-mini',
})

function handleSave() {
  localStorage.setItem('ai_api_key', config.aiApiKey)
  localStorage.setItem('ai_base_url', config.aiBaseUrl)
  localStorage.setItem('ai_model', config.aiModel)
  localStorage.setItem('ai_simple_model', config.aiSimpleModel)
  localStorage.setItem('ai_complex_model', config.aiComplexModel)
  message.success('配置已保存')
}
</script>
