<template>
  <div>
    <h2 style="margin-bottom:16px">设置</h2>
    <el-card shadow="never">
      <template #header><span>AI 配置</span></template>
      <el-form label-width="140px" style="max-width:600px">
        <el-form-item label="API Key">
          <el-input v-model="config.aiApiKey" type="password" placeholder="sk-..." show-password />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="config.aiBaseUrl" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="默认模型">
          <el-input v-model="config.aiModel" placeholder="gpt-4o" />
        </el-form-item>
        <el-form-item label="简单任务模型">
          <el-input v-model="config.aiSimpleModel" placeholder="gpt-4o-mini" />
        </el-form-item>
        <el-form-item label="复杂任务模型">
          <el-input v-model="config.aiComplexModel" placeholder="o3-mini" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const config = reactive({
  aiApiKey: localStorage.getItem('ai_api_key') || '',
  aiBaseUrl: localStorage.getItem('ai_base_url') || 'https://api.openai.com/v1',
  aiModel: localStorage.getItem('ai_model') || 'gpt-4o',
  aiSimpleModel: localStorage.getItem('ai_simple_model') || 'gpt-4o-mini',
  aiComplexModel: localStorage.getItem('ai_complex_model') || 'o3-mini',
})

function handleSave() {
  Object.entries(config).forEach(([k, v]) => localStorage.setItem(`ai_${k.replace(/([A-Z])/g, '_$1').toLowerCase()}`, v))
  ElMessage.success('配置已保存')
}
</script>
