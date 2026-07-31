<template>
  <div v-loading="loading" class="publish-page">
    <!-- 页头 -->
    <div class="page-header">
      <h2 style="margin: 0">发布管理</h2>
      <el-button :icon="Refresh" @click="loadAll">刷新</el-button>
    </div>

    <!-- 1. 通道状态卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col v-for="ch in channels" :key="ch.id" :xs="24" :sm="12" :md="8">
        <el-card shadow="never" class="channel-card">
          <template #header>
            <div class="channel-header">
              <span class="channel-name">{{ ch.name }}</span>
              <el-tag :type="statusMeta(ch.status)?.type || 'info'" size="small">
                {{ statusMeta(ch.status)?.label || ch.status }}
              </el-tag>
            </div>
          </template>
          <div class="channel-body">
            <div class="channel-row">
              <span class="label">类型</span>
              <el-tag :type="typeMeta(ch.type)?.type || 'info'" size="small">
                {{ typeMeta(ch.type)?.label || ch.type }}
              </el-tag>
            </div>
            <div class="channel-row">
              <span class="label">当前版本</span>
              <span class="value">v{{ ch.current_version ?? '-' }}</span>
            </div>
            <div class="channel-row">
              <span class="label">地址</span>
              <span class="value url">{{ ch.base_url || '-' }}</span>
            </div>
            <div class="channel-row">
              <span class="label">访问控制</span>
              <span class="value">{{ ACCESS_LABEL[ch.access_control ?? ''] || ch.access_control || '-' }}</span>
            </div>
          </div>
          <div class="channel-actions">
            <el-button size="small" type="primary" @click="openDeploy(ch)">部署</el-button>
            <el-button size="small" @click="openEditChannel(ch)">编辑</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="!channels.length && !loading" description="暂无发布通道" :image-size="80" />

    <!-- 2. 部署记录 -->
    <el-card shadow="never" class="section-card">
      <template #header><span>部署记录</span></template>
      <el-table :data="records" stripe style="width: 100%">
        <el-table-column label="版本" width="90" align="center">
          <template #default="{ row }">
            <span class="version-text">v{{ row.version }}</span>
          </template>
        </el-table-column>
        <el-table-column label="通道" width="130">
          <template #default="{ row }">{{ channelName(row.channel_id) }}</template>
        </el-table-column>
        <el-table-column prop="summary" label="说明" show-overflow-tooltip min-width="180" />
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMeta(row.status)?.type || 'info'" size="small">
              {{ statusMeta(row.status)?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ fmtTime(row.created_at || row.create_time) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!records.length && !loading" description="暂无发布记录" :image-size="80" />
    </el-card>

    <!-- 3. 云发布配置 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>云发布配置</span>
          <el-button link type="primary" :icon="Plus" @click="openCreateConfig">新建配置</el-button>
        </div>
      </template>
      <el-collapse v-if="configs.length" v-model="activeConfig" class="config-collapse">
        <el-collapse-item v-for="cfg in configs" :key="cfg.id" :name="cfg.id">
          <template #title>
            <div class="config-title">
              <span class="config-name">{{ cfg.name }}</span>
              <el-tag size="small" type="info">{{ cfg.provider }}</el-tag>
              <el-tag size="small" :type="cfg.enabled ? 'success' : 'info'">
                {{ cfg.enabled ? '启用' : '停用' }}
              </el-tag>
            </div>
          </template>
          <pre class="config-json">{{ formatConfig(cfg.config) }}</pre>
          <div class="config-actions">
            <el-button size="small" type="primary" @click="handleCloudPublish(cfg)">发布</el-button>
            <el-button size="small" @click="openEditConfig(cfg)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDeleteConfig(cfg)">删除</el-button>
          </div>
        </el-collapse-item>
      </el-collapse>
      <el-empty v-else-if="!loading" description="暂无云发布配置" :image-size="80" />
    </el-card>

    <!-- 4. Axhub 在线状态 -->
    <el-card shadow="never" class="section-card">
      <template #header><span>Axhub 在线状态</span></template>
      <template v-if="axhubStatus.connected">
        <div class="axhub-connected">
          <div class="axhub-head">
            <el-tag type="success" size="small">已连接</el-tag>
            <el-button size="small" type="danger" plain @click="handleDisconnect">断开连接</el-button>
          </div>
          <el-descriptions
            v-if="axhubUserInfoEntries.length"
            :column="2"
            size="small"
            border
            class="axhub-desc"
          >
            <el-descriptions-item v-for="[k, v] in axhubUserInfoEntries" :key="k" :label="k">
              {{ v }}
            </el-descriptions-item>
          </el-descriptions>
          <span v-else class="hint">已连接 Axhub 在线平台</span>
        </div>
      </template>
      <template v-else>
        <div class="axhub-disconnected">
          <el-tag type="info" size="small">未连接</el-tag>
          <span class="hint">连接后可将原型发布到 Axhub 在线平台</span>
          <el-button size="small" type="primary" @click="connectDialog.visible = true">连接</el-button>
        </div>
      </template>
    </el-card>

    <!-- ── Dialogs ── -->

    <!-- 部署对话框 -->
    <el-dialog v-model="deployDialog.visible" title="部署到通道" width="480px" destroy-on-close>
      <p style="margin: 0 0 12px">
        目标通道：<b>{{ deployDialog.channel?.name }}</b>（当前 v{{ deployDialog.channel?.current_version ?? '-' }}）
      </p>
      <el-form label-width="70px">
        <el-form-item label="说明">
          <el-input
            v-model="deployDialog.summary"
            type="textarea"
            :rows="3"
            placeholder="本次发布的说明（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deployDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="deployDialog.submitting" @click="submitDeploy">
          确认部署
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑通道对话框 -->
    <el-dialog v-model="channelDialog.visible" title="编辑通道" width="480px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="名称">
          <el-input v-model="channelDialog.name" />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="channelDialog.base_url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="访问控制">
          <el-select v-model="channelDialog.access_control" style="width: 100%">
            <el-option label="公开" value="public" />
            <el-option label="团队成员" value="team" />
            <el-option label="仅受邀" value="invite-only" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="channelDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="channelDialog.submitting" @click="submitChannelEdit">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑云发布配置对话框 -->
    <el-dialog
      v-model="configDialog.visible"
      :title="configDialog.mode === 'edit' ? '编辑配置' : '新建配置'"
      width="520px"
      destroy-on-close
    >
      <el-form label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="configDialog.name" placeholder="如：Axhub 在线" />
        </el-form-item>
        <el-form-item label="Provider">
          <el-select v-model="configDialog.provider" style="width: 100%">
            <el-option label="axhub" value="axhub" />
            <el-option label="figma" value="figma" />
            <el-option label="custom" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Config JSON">
          <el-input
            v-model="configDialog.configText"
            type="textarea"
            :rows="6"
            placeholder='{"token": "..."}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="configDialog.submitting" @click="submitConfig">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 云发布结果对话框 -->
    <el-dialog v-model="publishResult.visible" title="发布结果" width="480px">
      <el-result icon="success" title="已发布" :sub-title="publishResult.message || '发布完成'">
        <template #extra>
          <div class="publish-url">
            <el-link type="primary" :href="publishResult.url" target="_blank">
              {{ publishResult.url || '（无链接）' }}
            </el-link>
          </div>
          <el-button type="primary" @click="copyUrl(publishResult.url)">复制链接</el-button>
        </template>
      </el-result>
    </el-dialog>

    <!-- 连接 Axhub 对话框 -->
    <el-dialog v-model="connectDialog.visible" title="连接 Axhub" width="440px" destroy-on-close>
      <el-form label-width="70px">
        <el-form-item label="授权码">
          <el-input
            v-model="connectDialog.code"
            placeholder="输入 OAuth 授权码"
            @keyup.enter="submitConnect"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="connectDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="connectDialog.submitting" @click="submitConnect">
          连接
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { axhubApi, cloudPublishApi, publishApi } from '@/api'

/* ── 类型 ── */

interface Channel {
  id: number
  name: string
  type: string
  base_url?: string
  access_control?: string
  current_version?: number
  status: string
}

interface PublishRecordItem {
  id: number
  channel_id: number
  version: number
  summary: string
  status: string
  created_at?: string
  create_time?: string
}

interface CloudConfig {
  id: number
  name: string
  provider: string
  config: Record<string, unknown>
  enabled: boolean
}

interface AxhubStatus {
  connected: boolean
  user_info: Record<string, unknown>
  is_enterprise?: boolean
  expires_at?: string | null
}

/* ── 展示映射 ── */

const STATUS_META: Record<string, { label: string; type: 'info' | 'success' | 'warning' | 'danger' }> = {
  pending: { label: '未发布', type: 'info' },
  publishing: { label: '发布中', type: 'warning' },
  published: { label: '已发布', type: 'success' },
  failed: { label: '失败', type: 'danger' },
}
const statusMeta = (s?: string) => (s ? STATUS_META[s] : undefined)

const TYPE_META: Record<string, { label: string; type: 'primary' | 'warning' | 'danger' }> = {
  development: { label: '开发版', type: 'primary' },
  review: { label: '评审版', type: 'warning' },
  production: { label: '正式版', type: 'danger' },
}
const typeMeta = (t?: string) => (t ? TYPE_META[t] : undefined)

const ACCESS_LABEL: Record<string, string> = {
  public: '公开',
  team: '团队成员',
  'invite-only': '仅受邀',
}

/* ── 数据状态 ── */

const loading = ref(false)
const channels = ref<Channel[]>([])
const records = ref<PublishRecordItem[]>([])
const configs = ref<CloudConfig[]>([])
const axhubStatus = ref<AxhubStatus>({ connected: false, user_info: {} })
const activeConfig = ref<number[]>([])

/* ── 对话框状态 ── */

const deployDialog = reactive({
  visible: false,
  channel: null as Channel | null,
  summary: '',
  submitting: false,
})

const channelDialog = reactive({
  visible: false,
  id: 0,
  name: '',
  base_url: '',
  access_control: 'public',
  submitting: false,
})

const configDialog = reactive({
  visible: false,
  mode: 'create' as 'create' | 'edit',
  id: 0,
  name: '',
  provider: 'axhub',
  configText: '{}',
  submitting: false,
})

const publishResult = reactive({
  visible: false,
  url: '',
  message: '',
})

const connectDialog = reactive({
  visible: false,
  code: '',
  submitting: false,
})

/* ── 工具函数 ── */

const fmtTime = (t?: string | null) => (t ? new Date(t).toLocaleString('zh-CN') : '-')
const channelName = (id: number) => channels.value.find((c) => c.id === id)?.name || `#${id}`
const formatConfig = (cfg: unknown) => {
  try {
    return JSON.stringify(cfg || {}, null, 2)
  } catch {
    return String(cfg)
  }
}
const axhubUserInfoEntries = computed<Array<[string, string]>>(() =>
  Object.entries(axhubStatus.value.user_info || {}).map(([k, v]) => [
    k,
    typeof v === 'object' ? JSON.stringify(v) : String(v),
  ]),
)

async function copyUrl(url: string) {
  if (!url) return
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

/* ── 数据加载 ── */

async function loadChannels() {
  const res = await publishApi.channels()
  channels.value = res?.data || []
}

async function loadRecords() {
  const res = await publishApi.records()
  records.value = res?.data || []
}

async function loadConfigs() {
  const res = await cloudPublishApi.configs()
  configs.value = res?.data || []
}

async function loadAxhub() {
  const res = await axhubApi.status()
  axhubStatus.value = res?.data || { connected: false, user_info: {} }
}

async function loadAll() {
  loading.value = true
  try {
    await Promise.all([loadChannels(), loadRecords(), loadConfigs(), loadAxhub()])
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

/* ── 通道：部署 / 编辑 ── */

function openDeploy(ch: Channel) {
  deployDialog.channel = ch
  deployDialog.summary = ''
  deployDialog.visible = true
}

async function submitDeploy() {
  const ch = deployDialog.channel
  if (!ch) return
  deployDialog.submitting = true
  try {
    await publishApi.deploy(ch.id, deployDialog.summary)
    ElMessage.success(`已部署「${ch.name}」`)
    deployDialog.visible = false
    await Promise.all([loadChannels(), loadRecords()])
  } catch (e: any) {
    ElMessage.error(e?.message || '部署失败')
  } finally {
    deployDialog.submitting = false
  }
}

function openEditChannel(ch: Channel) {
  channelDialog.id = ch.id
  channelDialog.name = ch.name
  channelDialog.base_url = ch.base_url || ''
  channelDialog.access_control = ch.access_control || 'public'
  channelDialog.visible = true
}

async function submitChannelEdit() {
  channelDialog.submitting = true
  try {
    await publishApi.updateChannel(channelDialog.id, {
      name: channelDialog.name,
      base_url: channelDialog.base_url,
      access_control: channelDialog.access_control,
    })
    ElMessage.success('通道已更新')
    channelDialog.visible = false
    await loadChannels()
  } catch (e: any) {
    ElMessage.error(e?.message || '更新失败')
  } finally {
    channelDialog.submitting = false
  }
}

/* ── 云发布配置 ── */

function openCreateConfig() {
  configDialog.mode = 'create'
  configDialog.id = 0
  configDialog.name = ''
  configDialog.provider = 'axhub'
  configDialog.configText = '{}'
  configDialog.visible = true
}

function openEditConfig(cfg: CloudConfig) {
  configDialog.mode = 'edit'
  configDialog.id = cfg.id
  configDialog.name = cfg.name
  configDialog.provider = cfg.provider
  configDialog.configText = JSON.stringify(cfg.config || {}, null, 2)
  configDialog.visible = true
}

async function submitConfig() {
  if (!configDialog.name.trim()) {
    ElMessage.warning('请输入配置名称')
    return
  }
  let config: Record<string, unknown>
  try {
    config = JSON.parse(configDialog.configText || '{}')
  } catch {
    ElMessage.error('Config JSON 格式不正确')
    return
  }
  configDialog.submitting = true
  try {
    if (configDialog.mode === 'edit') {
      await cloudPublishApi.updateConfig(configDialog.id, {
        name: configDialog.name,
        provider: configDialog.provider,
        config,
      })
      ElMessage.success('配置已更新')
    } else {
      await cloudPublishApi.createConfig({
        name: configDialog.name,
        provider: configDialog.provider,
        config,
        enabled: true,
      })
      ElMessage.success('配置已创建')
    }
    configDialog.visible = false
    await loadConfigs()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    configDialog.submitting = false
  }
}

async function handleCloudPublish(cfg: CloudConfig) {
  try {
    const res = await cloudPublishApi.publish(cfg.id)
    const data = res?.data
    if (!data?.success) {
      ElMessage.error(data?.message || '发布失败')
      return
    }
    publishResult.url = data.url || ''
    publishResult.message = data.message || ''
    publishResult.visible = true
    await loadConfigs()
  } catch (e: any) {
    ElMessage.error(e?.message || '发布失败')
  }
}

async function handleDeleteConfig(cfg: CloudConfig) {
  try {
    await ElMessageBox.confirm(`确定删除配置「${cfg.name}」吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await cloudPublishApi.deleteConfig(cfg.id)
    ElMessage.success('配置已删除')
    await loadConfigs()
  } catch (e: any) {
    if (e === 'cancel' || e === 'close') return
    ElMessage.error(e?.message || '删除失败')
  }
}

/* ── Axhub 连接 ── */

async function submitConnect() {
  if (!connectDialog.code.trim()) {
    ElMessage.warning('请输入授权码')
    return
  }
  connectDialog.submitting = true
  try {
    const res = await axhubApi.connect(connectDialog.code.trim())
    if (res?.data?.success === false) throw new Error(res.data.message || '连接失败')
    ElMessage.success('已连接 Axhub')
    connectDialog.visible = false
    connectDialog.code = ''
    await loadAxhub()
  } catch (e: any) {
    ElMessage.error(e?.message || '连接失败')
  } finally {
    connectDialog.submitting = false
  }
}

async function handleDisconnect() {
  try {
    await ElMessageBox.confirm('确定断开 Axhub 连接吗？', '提示', {
      type: 'warning',
      confirmButtonText: '断开',
      cancelButtonText: '取消',
    })
    await axhubApi.disconnect()
    ElMessage.success('已断开 Axhub 连接')
    await loadAxhub()
  } catch (e: any) {
    if (e === 'cancel' || e === 'close') return
    ElMessage.error(e?.message || '断开失败')
  }
}

onMounted(loadAll)
</script>

<style scoped>
.publish-page {
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-card {
  margin-bottom: 16px;
}

.channel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-name {
  font-weight: 600;
}

.channel-body {
  font-size: 13px;
}

.channel-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  line-height: 20px;
}

.channel-row .label {
  color: #909399;
  flex-shrink: 0;
  margin-right: 12px;
}

.channel-row .value {
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.channel-row .value.url {
  color: #409eff;
}

.channel-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.version-text {
  font-weight: 600;
}

.config-collapse {
  border-top: none;
}

.config-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-name {
  font-weight: 600;
  margin-right: 4px;
}

.config-json {
  margin: 4px 0 12px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.config-actions {
  display: flex;
  gap: 8px;
}

.axhub-connected,
.axhub-disconnected {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.axhub-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.axhub-desc {
  width: 100%;
  margin-top: 4px;
}

.hint {
  color: #909399;
  font-size: 13px;
}

.publish-url {
  margin-bottom: 12px;
  max-width: 360px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
