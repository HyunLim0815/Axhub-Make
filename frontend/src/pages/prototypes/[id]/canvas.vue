<template>
  <div>
    <el-page-header :title="prototype?.name || '加载中...'" @back="$router.push('/prototypes')" style="margin-bottom:16px" />

    <el-row :gutter="16" style="flex:1;min-height:0">
      <!-- 画布区域 -->
      <el-col :span="16">
        <el-card shadow="never" style="height:100%">
          <template #header><span>画布</span></template>
          <div style="height:100%;display:flex;align-items:center;justify-content:center;color:#999;background:#f8f9fa;border-radius:4px;min-height:500px">
            <div style="text-align:center">
              <div style="font-size:48px;margin-bottom:8px">📐</div>
              <div>Excalidraw 画布</div>
              <div style="font-size:12px;margin-top:4px;color:#bbb">需要编译现有 React Excalidraw 为独立 HTML 后通过 iframe 嵌入</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧面板：标注 + 版本 -->
      <el-col :span="8">
        <el-card shadow="never" style="height:100%;display:flex;flex-direction:column">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>{{ showVersion ? '版本历史' : '标注' }}</span>
              <el-button size="small" @click="showVersion = !showVersion">
                {{ showVersion ? '标注列表' : '版本历史' }}
              </el-button>
            </div>
          </template>

          <!-- 标注列表 -->
          <div v-if="!showVersion" style="flex:1;overflow:auto">
            <div v-for="ann in annotations" :key="ann.id" style="padding:8px 0;border-bottom:1px solid var(--el-border-color-light)">
              <div style="display:flex;align-items:center;gap:8px">
                <span :style="{ width:10,height:10,borderRadius:'50%',background:ann.color,display:'inline-block' }" />
                <el-tag size="small">{{ ann.scope }}</el-tag>
                <span style="font-size:13px">{{ ann.title || ann.annotation_text?.slice(0, 40) }}</span>
              </div>
            </div>
            <el-empty v-if="!annotations.length" description="暂无标注" />
          </div>

          <!-- 版本历史 -->
          <div v-else style="flex:1;overflow:auto">
            <div v-for="v in versions" :key="v.id" style="padding:8px 0;border-bottom:1px solid var(--el-border-color-light)">
              <div style="display:flex;align-items:center;gap:8px">
                <el-tag size="small">v{{ v.version }}</el-tag>
                <span style="font-size:13px">{{ v.summary }}</span>
                <el-tag :type="v.status === 'released' ? 'success' : 'info'" size="small" style="margin-left:auto">{{ v.status }}</el-tag>
              </div>
            </div>
            <el-empty v-if="!versions.length" description="暂无版本" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { annotationApi, prototypeApi } from '@/api'

const route = useRoute()
const prototype = ref<any>(null)
const annotations = ref<any[]>([])
const versions = ref<any[]>([])
const showVersion = ref(false)

onMounted(async () => {
  const id = Number(route.params.id)
  try { const r = await prototypeApi.get(id); prototype.value = r.data } catch {}
  try { const r = await annotationApi.list({ prototype_id: id }); annotations.value = r.data?.data || [] } catch {}
  try { const r = await annotationApi.versions(id); versions.value = r.data?.data || [] } catch {}
})
</script>
