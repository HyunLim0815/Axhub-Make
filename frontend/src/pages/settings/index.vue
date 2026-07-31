<template>
  <div class="settings-page">
    <h2 style="margin-bottom:16px">设置</h2>

    <div class="settings-body">
      <!-- 左侧菜单 -->
      <el-menu :default-active="activeMenu" class="settings-menu" @select="handleMenuSelect">
        <el-menu-item index="access">
          <el-icon><Lock /></el-icon>
          <span>访问控制</span>
        </el-menu-item>
        <el-menu-item index="git">
          <el-icon><Share /></el-icon>
          <span>Git 版本管理</span>
        </el-menu-item>
        <el-menu-item index="template">
          <el-icon><Files /></el-icon>
          <span>模板与主题</span>
        </el-menu-item>
        <el-menu-item index="file">
          <el-icon><FolderOpened /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
      </el-menu>

      <!-- 右侧内容区 -->
      <div class="settings-content" v-loading="loading">
        <!-- ═══ 1. 访问控制 ═══ -->
        <section v-show="activeMenu === 'access'" class="settings-section">
          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <span>访问控制状态</span>
                <el-button size="small" :icon="Refresh" @click="loadAccess">刷新</el-button>
              </div>
            </template>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="已设置密码">
                <el-tag :type="accessStatus.password_set ? 'success' : 'info'" size="small">
                  {{ accessStatus.password_set ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="共享令牌数量">
                {{ accessStatus.share_tokens_count ?? 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="登录保护">
                <el-tag :type="accessStatus.login_required ? 'warning' : 'info'" size="small">
                  {{ accessStatus.login_required ? '已开启' : '未开启' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card shadow="never" style="margin-top:16px">
            <template #header><span>设置访问密码</span></template>
            <el-form label-width="90px" style="max-width:480px">
              <el-form-item label="新密码">
                <el-input v-model="passwordForm.password" type="password" show-password placeholder="请输入新密码（至少 6 位）" />
              </el-form-item>
              <el-form-item label="确认密码">
                <el-input
                  v-model="passwordForm.confirm"
                  type="password"
                  show-password
                  placeholder="再次输入确认"
                  @keyup.enter="handleSetPassword"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="savingPassword" @click="handleSetPassword">保存密码</el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <el-card shadow="never" style="margin-top:16px">
            <template #header><span>创建共享令牌</span></template>
            <el-form inline label-width="70px">
              <el-form-item label="名称">
                <el-input v-model="tokenForm.name" placeholder="令牌名称（可选）" style="width:220px" maxlength="255" />
              </el-form-item>
              <el-form-item label="有效期">
                <el-input-number v-model="tokenForm.expiresInHours" :min="1" :max="8760" />
                <span style="margin-left:8px;font-size:13px;color:var(--el-text-color-secondary)">小时</span>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="creatingToken" @click="handleCreateToken">生成令牌</el-button>
              </el-form-item>
            </el-form>
            <el-alert v-if="generatedToken" type="success" :closable="false" show-icon style="margin-top:8px">
              <template #title>
                <div class="token-line">
                  <code class="token-value">{{ generatedToken }}</code>
                  <el-button size="small" link type="primary" :icon="CopyDocument" @click="copyToken">复制</el-button>
                </div>
              </template>
            </el-alert>
          </el-card>
        </section>

        <!-- ═══ 2. Git 版本管理 ═══ -->
        <section v-show="activeMenu === 'git'" class="settings-section">
          <div class="git-toolbar">
            <el-alert v-if="!gitStatus.branch" type="warning" :closable="false" show-icon style="flex:1">
              <template #title>当前目录尚未初始化 Git 仓库，可点击「初始化仓库」开始版本管理</template>
            </el-alert>
            <div v-else class="branch-info">
              <el-icon color="var(--el-color-primary)"><Share /></el-icon>
              <span class="branch-name">{{ gitStatus.branch }}</span>
              <el-tag v-if="gitStatus.dirty" type="warning" size="small">有未提交的变更</el-tag>
              <el-tag v-else type="success" size="small">工作区干净</el-tag>
            </div>
            <el-button size="small" :icon="Refresh" @click="loadGit">刷新</el-button>
            <el-button size="small" type="warning" plain :loading="initializing" @click="handleInitRepo">初始化仓库</el-button>
          </div>

          <template v-if="gitStatus.branch">
            <div class="git-grid">
              <el-card shadow="never">
                <template #header><span>变更列表</span></template>
                <el-table :data="gitStatus.changes" size="small" max-height="360" empty-text="暂无变更">
                  <el-table-column prop="path" label="路径" show-overflow-tooltip />
                  <el-table-column label="状态" width="120" align="center">
                    <template #default="{ row }">
                      <el-tag :type="gitStatusTag(row.status).type" size="small">{{ gitStatusTag(row.status).label }}</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>

              <el-card shadow="never">
                <template #header><span>提交历史</span></template>
                <el-timeline class="git-timeline">
                  <el-timeline-item
                    v-for="h in history"
                    :key="h.hash"
                    :timestamp="fmtTime(h.date)"
                    placement="top"
                    size="large"
                  >
                    <div class="commit-item">
                      <div class="commit-head">
                        <code class="commit-hash">{{ shortHash(h.hash) }}</code>
                        <span class="commit-author">{{ h.author }}</span>
                      </div>
                      <div class="commit-message">{{ h.message }}</div>
                    </div>
                  </el-timeline-item>
                </el-timeline>
                <el-empty v-if="!history.length" description="暂无提交记录" :image-size="80" />
              </el-card>
            </div>

            <el-card shadow="never" style="margin-top:16px">
              <template #header><span>提交变更</span></template>
              <div class="commit-bar">
                <el-input
                  v-model="commitMessage"
                  placeholder="请输入提交信息，如：feat: 添加设置页面"
                  clearable
                  @keyup.enter="handleCommit"
                />
                <el-button type="primary" :loading="committing" @click="handleCommit">提交</el-button>
              </div>
            </el-card>
          </template>
        </section>

        <!-- ═══ 3. 模板与主题 ═══ -->
        <section v-show="activeMenu === 'template'" class="settings-section">
          <el-card shadow="never">
            <el-tabs v-model="activeTab" @tab-change="handleTabChange">
              <!-- 模板库 -->
              <el-tab-pane label="模板库" name="templates">
                <div class="table-toolbar">
                  <span class="table-count">共 {{ templates.length }} 个模板</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="openTemplateDialog()">新建模板</el-button>
                </div>
                <el-table :data="templates" size="small">
                  <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
                  <el-table-column prop="category" label="分类" width="110">
                    <template #default="{ row }">
                      <el-tag size="small" type="info">{{ row.category }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="标签" min-width="160">
                    <template #default="{ row }">
                      <template v-if="row.tags && row.tags.length">
                        <el-tag v-for="t in row.tags" :key="t" size="small" type="success" class="tag-item">{{ t }}</el-tag>
                      </template>
                      <span v-else class="muted">-</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="description" label="描述" min-width="160" show-overflow-tooltip>
                    <template #default="{ row }">{{ row.description || '-' }}</template>
                  </el-table-column>
                  <el-table-column label="更新时间" width="160">
                    <template #default="{ row }">{{ fmtTime(row.update_time) }}</template>
                  </el-table-column>
                  <el-table-column label="操作" width="130" align="center" fixed="right">
                    <template #default="{ row }">
                      <el-button size="small" link type="primary" @click="openTemplateDialog(row)">编辑</el-button>
                      <el-button size="small" link type="danger" @click="handleDeleteTemplate(row)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-if="!templates.length" description="暂无模板" :image-size="80" />
              </el-tab-pane>

              <!-- 主题库 -->
              <el-tab-pane label="主题库" name="themes">
                <div class="table-toolbar">
                  <span class="table-count">共 {{ themes.length }} 个主题</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="openThemeDialog()">新建主题</el-button>
                </div>
                <el-table :data="themes" size="small">
                  <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
                  <el-table-column label="Token 数" width="110" align="center">
                    <template #default="{ row }">
                      <el-tag size="small" type="info">{{ Object.keys(row.tokens || {}).length }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="Token 摘要" min-width="220">
                    <template #default="{ row }">
                      <code class="token-summary" v-if="Object.keys(row.tokens || {}).length">
                        {{ Object.keys(row.tokens).slice(0, 3).join(', ') }}{{ Object.keys(row.tokens).length > 3 ? ' …' : '' }}
                      </code>
                      <span v-else class="muted">-</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="description" label="描述" min-width="160" show-overflow-tooltip>
                    <template #default="{ row }">{{ row.description || '-' }}</template>
                  </el-table-column>
                  <el-table-column label="更新时间" width="160">
                    <template #default="{ row }">{{ fmtTime(row.update_time) }}</template>
                  </el-table-column>
                  <el-table-column label="操作" width="130" align="center" fixed="right">
                    <template #default="{ row }">
                      <el-button size="small" link type="primary" @click="openThemeDialog(row)">编辑</el-button>
                      <el-button size="small" link type="danger" @click="handleDeleteTheme(row)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-if="!themes.length" description="暂无主题" :image-size="80" />
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </section>

        <!-- ═══ 4. 文件管理 ═══ -->
        <section v-show="activeMenu === 'file'" class="settings-section">
          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <span>文件列表</span>
                <div class="file-actions">
                  <el-upload :show-file-list="false" :http-request="handleUpload" multiple>
                    <el-button type="primary" size="small" :icon="Upload" :loading="uploading">上传文件</el-button>
                  </el-upload>
                  <el-button size="small" :icon="Refresh" @click="loadFiles">刷新</el-button>
                </div>
              </div>
            </template>
            <el-table :data="files" size="small">
              <el-table-column label="名称" min-width="240">
                <template #default="{ row }">
                  <div class="file-name">
                    <el-icon :color="row.is_dir ? 'var(--el-color-warning)' : 'var(--el-color-info)'">
                      <Folder v-if="row.is_dir" /><Document v-else />
                    </el-icon>
                    <span>{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="类型" width="90" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_dir ? 'warning' : 'info'" size="small">{{ row.is_dir ? '目录' : '文件' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="大小" width="110">
                <template #default="{ row }">{{ row.is_dir ? '-' : fmtSize(row.size) }}</template>
              </el-table-column>
              <el-table-column label="修改时间" width="170">
                <template #default="{ row }">{{ fmtTimestamp(row.modified_time) }}</template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!files.length" description="暂无文件" :image-size="80" />
          </el-card>
        </section>
      </div>
    </div>

    <!-- 新建/编辑模板对话框 -->
    <el-dialog v-model="showTemplateDialog" :title="templateForm.id != null ? '编辑模板' : '新建模板'" width="560" @closed="resetTemplateForm">
      <el-form :model="templateForm" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" maxlength="255" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="templateForm.category" placeholder="如 page / component" maxlength="64" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="templateForm.description" type="textarea" :rows="2" placeholder="模板描述（可选）" />
        </el-form-item>
        <el-form-item label="内容 JSON">
          <el-input
            v-model="templateForm.contentJson"
            type="textarea"
            :rows="8"
            class="mono"
            placeholder='如 {"type":"page","children":[]}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTemplateDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingTemplate" @click="handleSaveTemplate">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑主题对话框 -->
    <el-dialog v-model="showThemeDialog" :title="themeForm.id != null ? '编辑主题' : '新建主题'" width="560" @closed="resetThemeForm">
      <el-form :model="themeForm" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="themeForm.name" placeholder="请输入主题名称" maxlength="255" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="themeForm.description" type="textarea" :rows="2" placeholder="主题描述（可选）" />
        </el-form-item>
        <el-form-item label="tokens JSON">
          <el-input
            v-model="themeForm.tokensJson"
            type="textarea"
            :rows="8"
            class="mono"
            placeholder='如 {"--primary-color":"#409EFF","--font-size":"14px"}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showThemeDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingTheme" @click="handleSaveTheme">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  CopyDocument,
  Document,
  Files,
  Folder,
  FolderOpened,
  Lock,
  Plus,
  Refresh,
  Share,
  Upload,
} from '@element-plus/icons-vue'
import { accessApi, fileApi, gitApi, templateApi, themeApi } from '@/api'

// ── 菜单 ──
type MenuKey = 'access' | 'git' | 'template' | 'file'
const activeMenu = ref<MenuKey>('access')
const loading = ref(false)

function handleMenuSelect(index: string) {
  activeMenu.value = index as MenuKey
  loadCurrent()
}

async function loadCurrent() {
  switch (activeMenu.value) {
    case 'access':
      await loadAccess()
      break
    case 'git':
      await loadGit()
      break
    case 'template':
      await loadTemplate()
      break
    case 'file':
      await loadFiles()
      break
  }
}

onMounted(loadCurrent)

// ── 通用工具 ──
const fmtTime = (t: any) => (t ? new Date(t).toLocaleString('zh-CN') : '-')
const fmtTimestamp = (ts: any) => (ts ? new Date(ts * 1000).toLocaleString('zh-CN') : '-')
const shortHash = (h: string) => (h ? h.slice(0, 8) : '-')

function fmtSize(bytes: number) {
  if (bytes == null) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`
  return `${(bytes / 1024 ** 3).toFixed(2)} GB`
}

function parseJson(s: string, field: string) {
  try {
    return JSON.parse(s || '{}')
  } catch {
    ElMessage.error(`${field} 不是有效的 JSON`)
    return null
  }
}

// ── 1. 访问控制 ──
const accessStatus = ref<any>({ password_set: false, share_tokens_count: 0, login_required: false })
const passwordForm = reactive({ password: '', confirm: '' })
const savingPassword = ref(false)
const tokenForm = reactive({ name: '', expiresInHours: 24 })
const creatingToken = ref(false)
const generatedToken = ref('')

async function loadAccess() {
  loading.value = true
  try {
    const res = await accessApi.status()
    accessStatus.value = res.data || {}
  } catch (e) {
    console.error(e)
    ElMessage.error('加载访问状态失败')
  } finally {
    loading.value = false
  }
}

async function handleSetPassword() {
  if (!passwordForm.password) return ElMessage.warning('请输入新密码')
  if (passwordForm.password.length < 6) return ElMessage.warning('密码至少 6 位')
  if (passwordForm.password !== passwordForm.confirm) return ElMessage.warning('两次输入的密码不一致')
  savingPassword.value = true
  try {
    await accessApi.setPassword(passwordForm.password)
    ElMessage.success('密码设置成功')
    passwordForm.password = ''
    passwordForm.confirm = ''
    await loadAccess()
  } catch (e) {
    console.error(e)
    ElMessage.error('设置密码失败')
  } finally {
    savingPassword.value = false
  }
}

async function handleCreateToken() {
  creatingToken.value = true
  try {
    const res = await accessApi.createShareToken(tokenForm.name.trim(), tokenForm.expiresInHours)
    generatedToken.value = res.data?.token || ''
    ElMessage.success('令牌生成成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('生成令牌失败')
  } finally {
    creatingToken.value = false
  }
}

async function copyToken() {
  try {
    await navigator.clipboard.writeText(generatedToken.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.warning('复制失败，请手动选择复制')
  }
}

// ── 2. Git 版本管理 ──
const gitStatus = ref<any>({ branch: '', changes: [], dirty: false })
const history = ref<any[]>([])
const commitMessage = ref('')
const committing = ref(false)
const initializing = ref(false)

async function loadGit() {
  loading.value = true
  try {
    const [sRes, hRes] = await Promise.all([gitApi.status(), gitApi.history(20)])
    gitStatus.value = sRes.data || { branch: '', changes: [], dirty: false }
    history.value = hRes.data || []
  } catch (e) {
    console.error(e)
    ElMessage.error('加载 Git 状态失败')
  } finally {
    loading.value = false
  }
}

function gitStatusTag(code: string) {
  const c = (code || '').trim()
  if (!c) return { type: 'info' as const, label: '未知' }
  const map: Record<string, { type: 'success' | 'warning' | 'danger' | 'info'; label: string }> = {
    '??': { type: 'info', label: '未跟踪' },
    M: { type: 'warning', label: '已修改' },
    A: { type: 'success', label: '已新增' },
    D: { type: 'danger', label: '已删除' },
    R: { type: 'warning', label: '已重命名' },
    U: { type: 'danger', label: '冲突' },
  }
  return map[c] || map[c[0]] || { type: 'info', label: c }
}

async function handleCommit() {
  const msg = commitMessage.value.trim()
  if (!msg) return ElMessage.warning('请输入提交信息')
  committing.value = true
  try {
    await gitApi.commit(msg)
    ElMessage.success('提交成功')
    commitMessage.value = ''
    await loadGit()
  } catch (e) {
    console.error(e)
    ElMessage.error('提交失败')
  } finally {
    committing.value = false
  }
}

async function handleInitRepo() {
  try {
    await ElMessageBox.confirm('确定在项目目录初始化 Git 仓库？', '初始化仓库', {
      type: 'warning',
      confirmButtonText: '初始化',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  initializing.value = true
  try {
    await gitApi.initWorkspace('.')
    ElMessage.success('仓库初始化成功')
    await loadGit()
  } catch (e) {
    console.error(e)
    ElMessage.error('初始化失败')
  } finally {
    initializing.value = false
  }
}

// ── 3. 模板与主题 ──
const templates = ref<any[]>([])
const themes = ref<any[]>([])
const activeTab = ref('templates')

async function loadTemplate() {
  loading.value = true
  try {
    const res = await templateApi.list()
    templates.value = res.data?.data ?? res.data ?? []
  } catch (e) {
    console.error(e)
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

async function handleTabChange() {
  loading.value = true
  try {
    if (activeTab.value === 'templates') {
      const res = await templateApi.list()
      templates.value = res.data?.data ?? res.data ?? []
    } else {
      const res = await themeApi.list()
      themes.value = res.data?.data ?? res.data ?? []
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 模板对话框
const showTemplateDialog = ref(false)
const savingTemplate = ref(false)
const templateForm = reactive({
  id: null as number | null,
  name: '',
  category: 'page',
  description: '',
  contentJson: '{}',
})

function openTemplateDialog(row?: any) {
  if (row) {
    templateForm.id = row.id
    templateForm.name = row.name
    templateForm.category = row.category || 'page'
    templateForm.description = row.description || ''
    templateForm.contentJson = JSON.stringify(row.content || {}, null, 2)
  } else {
    resetTemplateForm()
  }
  showTemplateDialog.value = true
}

function resetTemplateForm() {
  templateForm.id = null
  templateForm.name = ''
  templateForm.category = 'page'
  templateForm.description = ''
  templateForm.contentJson = '{}'
}

async function handleSaveTemplate() {
  if (!templateForm.name.trim()) return ElMessage.warning('请输入模板名称')
  const content = parseJson(templateForm.contentJson, '内容')
  if (content === null) return
  savingTemplate.value = true
  try {
    const body = {
      name: templateForm.name.trim(),
      category: templateForm.category.trim() || 'page',
      description: templateForm.description,
      content,
    }
    if (templateForm.id != null) {
      await templateApi.update(templateForm.id, body)
      ElMessage.success('模板已更新')
    } else {
      await templateApi.create(body)
      ElMessage.success('模板已创建')
    }
    showTemplateDialog.value = false
    await handleTabChange()
  } catch (e) {
    console.error(e)
    ElMessage.error('保存模板失败')
  } finally {
    savingTemplate.value = false
  }
}

async function handleDeleteTemplate(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除模板「${row.name}」？此操作不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await templateApi.delete(row.id)
    ElMessage.success('删除成功')
    await handleTabChange()
  } catch (e) {
    console.error(e)
    ElMessage.error('删除失败')
  }
}

// 主题对话框
const showThemeDialog = ref(false)
const savingTheme = ref(false)
const themeForm = reactive({
  id: null as number | null,
  name: '',
  description: '',
  tokensJson: '{}',
})

function openThemeDialog(row?: any) {
  if (row) {
    themeForm.id = row.id
    themeForm.name = row.name
    themeForm.description = row.description || ''
    themeForm.tokensJson = JSON.stringify(row.tokens || {}, null, 2)
  } else {
    resetThemeForm()
  }
  showThemeDialog.value = true
}

function resetThemeForm() {
  themeForm.id = null
  themeForm.name = ''
  themeForm.description = ''
  themeForm.tokensJson = '{}'
}

async function handleSaveTheme() {
  if (!themeForm.name.trim()) return ElMessage.warning('请输入主题名称')
  const tokens = parseJson(themeForm.tokensJson, 'tokens')
  if (tokens === null) return
  savingTheme.value = true
  try {
    const body = {
      name: themeForm.name.trim(),
      description: themeForm.description,
      tokens,
    }
    if (themeForm.id != null) {
      await themeApi.update(themeForm.id, body)
      ElMessage.success('主题已更新')
    } else {
      await themeApi.create(body)
      ElMessage.success('主题已创建')
    }
    showThemeDialog.value = false
    await handleTabChange()
  } catch (e) {
    console.error(e)
    ElMessage.error('保存主题失败')
  } finally {
    savingTheme.value = false
  }
}

async function handleDeleteTheme(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除主题「${row.name}」？此操作不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await themeApi.delete(row.id)
    ElMessage.success('删除成功')
    await handleTabChange()
  } catch (e) {
    console.error(e)
    ElMessage.error('删除失败')
  }
}

// ── 4. 文件管理 ──
const files = ref<any[]>([])
const uploading = ref(false)

async function loadFiles() {
  loading.value = true
  try {
    const res = await fileApi.list()
    files.value = res.data || []
  } catch (e) {
    console.error(e)
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

async function handleUpload(options: any) {
  uploading.value = true
  try {
    await fileApi.upload(options.file)
    ElMessage.success(`文件 ${options.file.name} 上传成功`)
    await loadFiles()
  } catch (e) {
    console.error(e)
    ElMessage.error(`文件 ${options.file.name} 上传失败`)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.settings-body {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.settings-menu {
  width: 200px;
  flex-shrink: 0;
  border-right: none;
  border-radius: 8px;
  padding: 8px 0;
  background: var(--el-bg-color);
  box-shadow: var(--el-box-shadow-light);
}

.settings-content {
  flex: 1;
  min-width: 0;
}

.settings-section {
  min-height: 200px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 访问控制 */
.token-line {
  display: flex;
  align-items: center;
  gap: 10px;
}

.token-value {
  font-family: monospace;
  font-size: 13px;
  word-break: break-all;
}

/* Git */
.git-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.branch-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.branch-name {
  font-weight: 600;
  font-size: 15px;
}

.git-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.git-timeline {
  padding-left: 4px;
}

.commit-item {
  margin-bottom: 2px;
}

.commit-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.commit-hash {
  font-family: monospace;
  font-size: 12px;
  color: var(--el-color-primary);
}

.commit-author {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.commit-message {
  font-size: 13px;
  margin-top: 2px;
}

.commit-bar {
  display: flex;
  gap: 12px;
}

/* 模板与主题 */
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.table-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.tag-item {
  margin-right: 4px;
}

.token-summary {
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.mono :deep(textarea) {
  font-family: monospace;
  font-size: 12px;
}

/* 文件管理 */
.file-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 6px;
}

.muted {
  color: var(--el-text-color-placeholder);
}

@media (max-width: 1200px) {
  .git-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .settings-body {
    flex-direction: column;
  }

  .settings-menu {
    width: 100%;
    display: flex;
  }

  .settings-menu :deep(.el-menu-item) {
    flex: 1;
    justify-content: center;
  }
}
</style>
