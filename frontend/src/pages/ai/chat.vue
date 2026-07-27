<template>
  <div style="display:flex;flex-direction:column;height:calc(100vh - 140px)">
    <n-page-header>
      <template #title>AI 助手</template>
    </n-page-header>

    <!-- 聊天消息 -->
    <n-card style="flex:1;overflow:auto;margin-top:16px" content-style="min-height:300px">
      <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
        <n-avatar :style="{ background: msg.role === 'user' ? '#1677ff' : '#52c41a' }" size="small" circle>
          {{ msg.role === 'user' ? 'U' : 'A' }}
        </n-avatar>
        <div class="msg-content">
          <div class="msg-role">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
          <div class="msg-text">{{ msg.content }}</div>
        </div>
      </div>
      <n-empty v-if="!messages.length" description="开始对话..." style="padding:60px" />
    </n-card>

    <!-- 输入区 -->
    <n-space class="mt-4">
      <n-input
        v-model:value="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入你的需求..."
        @keydown.enter.ctrl="handleSend"
      />
      <n-button type="primary" :loading="loading" @click="handleSend" style="height:56px">发送</n-button>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { aiApi } from '@/api'

const inputText = ref('')
const loading = ref(false)
const messages = ref<{ role: string; content: string }[]>([])

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
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.msg-row { display: flex; gap: 12px; margin-bottom: 16px; }
.msg-row.user { flex-direction: row-reverse; }
.msg-content { max-width: 70%; }
.msg-role { font-size: 12px; color: #999; margin-bottom: 4px; }
.msg-row.user .msg-role { text-align: right; }
.msg-text { background: #f5f5f5; border-radius: 8px; padding: 8px 12px; white-space: pre-wrap; }
.msg-row.user .msg-text { background: #1677ff; color: #fff; }
</style>
