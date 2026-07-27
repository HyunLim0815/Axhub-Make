<template>
  <div style="display:flex;flex-direction:column;height:calc(100vh - 100px)">
    <h2 style="margin-bottom:16px">AI 助手</h2>

    <el-card shadow="never" style="flex:1;overflow:auto;margin-bottom:12px">
      <div v-for="(msg, i) in messages" :key="i" :style="msgStyle(msg.role)">
        <div style="font-size:12px;color:#999;margin-bottom:4px">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
        <div :style="bubbleStyle(msg.role)">{{ msg.content }}</div>
      </div>
      <el-empty v-if="!messages.length" description="开始对话..." />
    </el-card>

    <div style="display:flex;gap:12px">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入你的需求... (Ctrl+Enter 发送)"
        @keydown.ctrl.enter="handleSend"
      />
      <el-button type="primary" :loading="loading" @click="handleSend" style="height:56px;width:80px">发送</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { aiApi } from '@/api'

const inputText = ref('')
const loading = ref(false)
const messages = ref<{ role: string; content: string }[]>([])

const msgStyle = (role: string) => ({
  display: 'flex', flexDirection: 'column' as const,
  alignItems: role === 'user' ? 'flex-end' as const : 'flex-start' as const,
  marginBottom: '16px',
})

const bubbleStyle = (role: string) => ({
  maxWidth: '70%',
  padding: '8px 14px',
  borderRadius: '8px',
  background: role === 'user' ? 'var(--el-color-primary)' : '#f0f2f5',
  color: role === 'user' ? '#fff' : 'var(--el-text-color-primary)',
  whiteSpace: 'pre-wrap' as const,
  fontSize: '14px',
  lineHeight: '1.6',
})

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  try {
    const res = await aiApi.chat(text)
    messages.value.push({ role: 'assistant', content: res.data?.content || '(无响应)' })
  } catch (e: any) {
    messages.value.push({ role: 'assistant', content: `错误: ${e.message}` })
  } finally { loading.value = false }
}
</script>
