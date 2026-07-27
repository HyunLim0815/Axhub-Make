<template>
  <div>
    <n-page-header>
      <template #title>{{ prototype?.name || '加载中...' }}</template>
      <template #extra>
        <n-button @click="$router.push('/prototypes')">返回列表</n-button>
      </template>
    </n-page-header>

    <n-grid :cols="2" :x-gap="16" class="mt-4" style="height: calc(100vh - 140px)">
      <!-- 画布区域 (iframe 嵌入现有 Excalidraw) -->
      <n-grid-item>
        <n-card title="画布" size="small" style="height:100%">
          <div style="width:100%;height:100%;min-height:500px;background:#f5f5f5;display:flex;align-items:center;justify-content:center;color:#999">
            <div style="text-align:center">
              <div style="font-size:48px;margin-bottom:8px">📐</div>
              <div>Excalidraw 画布 (iframe)</div>
              <div style="font-size:12px;margin-top:4px">需要编译现有 React Excalidraw 为独立 HTML</div>
            </div>
          </div>
        </n-card>
      </n-grid-item>

      <!-- 标注面板 -->
      <n-grid-item>
        <n-card title="标注" size="small" style="height:100%;display:flex;flex-direction:column">
          <template #header-extra>
            <n-button size="tiny" @click="showVersionPanel = !showVersionPanel">
              {{ showVersionPanel ? '标注列表' : '版本历史' }}
            </n-button>
          </template>

          <!-- 标注列表 -->
          <n-list v-if="!showVersionPanel" style="flex:1;overflow:auto">
            <n-list-item v-for="ann in annotations" :key="ann.id">
              <template #prefix>
                <div :style="{ width:12,height:12,borderRadius:'50%',background:ann.color }" />
              </template>
              <n-ellipsis style="max-width:200px">{{ ann.title || ann.annotation_text?.slice(0,50) }}</n-ellipsis>
              <template #suffix>
                <n-tag size="tiny">{{ ann.scope }}</n-tag>
              </template>
            </n-list-item>
            <n-empty v-if="!annotations.length" description="暂无标注" style="padding:40px" />
          </n-list>

          <!-- 版本历史 -->
          <n-list v-else style="flex:1;overflow:auto">
            <n-list-item v-for="v in versions" :key="v.id">
              <template #prefix>
                <n-tag size="tiny">v{{ v.version }}</n-tag>
              </template>
              {{ v.summary }}
              <template #suffix>
                <n-tag size="tiny" :type="v.status === 'released' ? 'success' : 'info'">{{ v.status }}</n-tag>
              </template>
            </n-list-item>
            <n-empty v-if="!versions.length" description="暂无版本" style="padding:40px" />
          </n-list>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { annotationApi, prototypeApi } from '@/api'

const route = useRoute()
const router = useRouter()
const prototype = ref<any>(null)
const annotations = ref<any[]>([])
const versions = ref<any[]>([])
const showVersionPanel = ref(false)

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    const res = await prototypeApi.get(id)
    prototype.value = res.data
  } catch {}

  try {
    const res = await annotationApi.list({ prototype_id: id })
    annotations.value = res.data?.data || []
  } catch {}

  try {
    const res = await annotationApi.versions(id)
    versions.value = res.data?.data || []
  } catch {}
})
</script>
