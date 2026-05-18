<template>
  <div class="log-view">
    <div class="toolbar">
      <h3 style="margin: 0">操作日志</h3>
      <el-tag>教学辅助</el-tag>
    </div>

    <!-- 标签页切换 -->
    <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
      <!-- Tab 1: 日志列表（原有功能） -->
      <el-tab-pane label="日志列表" name="list">
        <!-- 筛选条件 -->
        <el-card shadow="never" style="margin-bottom: 16px">
          <el-form :inline="true" :model="filters">
            <el-form-item label="用户">
              <el-select v-model="filters.user_id" placeholder="全部用户" clearable style="width: 150px">
                <el-option v-for="u in users" :key="u.id" :label="u.real_name || u.username" :value="u.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="模块">
              <el-select v-model="filters.module" placeholder="全部模块" clearable style="width: 150px">
                <el-option v-for="m in moduleOptions" :key="m.value" :label="m.label" :value="m.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="正确">
              <el-select v-model="filters.is_correct" placeholder="全部" clearable style="width: 100px">
                <el-option label="正确" value="true" />
                <el-option label="错误" value="false" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadLogs">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 统计概览 -->
        <el-row :gutter="16" style="margin-bottom: 16px">
          <el-col :xs="12" :sm="6">
            <el-statistic title="总操作数" :value="logStats.total" />
          </el-col>
          <el-col :xs="12" :sm="6">
            <el-statistic title="正确操作" :value="logStats.correct" />
          </el-col>
          <el-col :xs="12" :sm="6">
            <el-statistic title="错误率" :value="logStats.error_rate" suffix="%" />
          </el-col>
          <el-col :xs="12" :sm="6">
            <el-statistic title="涉及模块" :value="logStats.module_stats?.length || 0" suffix="个" />
          </el-col>
        </el-row>

        <!-- 日志时间线 -->
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>操作记录 ({{ pagination.total }} 条)</span>
              <el-pagination
                v-model:current-page="pagination.page"
                :page-size="pagination.per_page"
                :total="pagination.total"
                layout="prev, pager, next"
                small
                @current-change="loadLogs"
              />
            </div>
          </template>

          <el-timeline>
            <el-timeline-item
              v-for="log in logs"
              :key="log.id"
              :type="log.is_correct ? 'primary' : 'danger'"
              :timestamp="log.created_at"
              placement="top"
            >
              <el-card shadow="never" class="log-item clickable" @click="showLogDetail(log)">
                <div class="log-header">
                  <el-tag :type="log.is_correct ? 'success' : 'danger'" size="small">
                    {{ log.is_correct ? '正确' : '错误' }}
                  </el-tag>
                  <span class="log-user">{{ log.user_name || log.username }}</span>
                  <el-tag size="small" style="margin-left: 4px">{{ moduleLabel(log.module) }}</el-tag>
                  <strong>{{ log.action }}</strong>
                </div>
                <div v-if="log.description" class="log-desc">{{ log.description }}</div>
                <div v-if="log.target_type" class="log-target">
                  目标: {{ log.target_type }} #{{ log.target_id }}
                </div>
                <div class="log-hint">点击查看详情</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>

          <el-empty v-if="logs.length === 0" description="暂无操作日志" />
        </el-card>
      </el-tab-pane>

      <!-- Tab 2: 学生操作回放 -->
      <el-tab-pane label="学生操作回放" name="replay">
        <!-- 学生选择 -->
        <el-card shadow="never" style="margin-bottom: 16px">
          <el-form :inline="true">
            <el-form-item label="选择学生">
              <el-select
                v-model="replayUserId"
                placeholder="请选择学生"
                filterable
                style="width: 200px"
                @change="loadReplayData"
              >
                <el-option v-for="u in users" :key="u.id" :label="u.real_name || u.username" :value="u.id" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="replayUserId">
              <el-button type="primary" @click="loadReplayData">刷新</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-empty v-if="!replayUserId" description="请先选择一个学生查看操作回放" />

        <template v-else>
          <!-- 回放统计概览 -->
          <el-row :gutter="16" style="margin-bottom: 16px">
            <el-col :xs="12" :sm="6">
              <el-statistic title="总操作数" :value="replayData.total" />
            </el-col>
            <el-col :xs="12" :sm="6">
              <el-statistic title="正确率" :value="replayData.accuracy_rate" suffix="%" />
            </el-col>
            <el-col :xs="12" :sm="6">
              <el-statistic title="覆盖模块" :value="replayData.module_coverage?.filter(m => m.covered).length || 0" />
            </el-col>
            <el-col :xs="12" :sm="6">
              <el-statistic title="操作时长" :value="replayData.time_span?.duration_minutes || 0" suffix="分钟" />
            </el-col>
          </el-row>

          <!-- 模块覆盖进度 -->
          <el-card shadow="never" style="margin-bottom: 16px">
            <template #header>
              <span>模块覆盖情况</span>
              <el-tag style="margin-left: 8px" type="info" size="small">
                {{ replayData.module_coverage?.filter(m => m.covered).length || 0 }} / {{ replayData.module_coverage?.length || 0 }}
              </el-tag>
            </template>
            <el-row :gutter="12">
              <el-col :xs="12" :sm="8" :md="4" v-for="mod in replayData.module_coverage" :key="mod.module">
                <div class="module-coverage-item" :class="{ covered: mod.covered }">
                  <el-icon :size="20" :color="mod.covered ? '#67C23A' : '#C0C4CC'">
                    <CircleCheckFilled v-if="mod.covered" />
                    <CircleClose v-else />
                  </el-icon>
                  <span>{{ mod.label }}</span>
                  <el-tag size="small" :type="mod.covered ? 'success' : 'info'">{{ mod.operation_count }}次</el-tag>
                </div>
              </el-col>
            </el-row>
          </el-card>

          <!-- 操作时间线 -->
          <el-card shadow="hover">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>操作时间线 ({{ replayData.timeline?.length || 0 }} 步)</span>
              </div>
            </template>

            <el-timeline v-if="replayData.timeline?.length">
              <el-timeline-item
                v-for="(log, index) in replayData.timeline"
                :key="log.id"
                :type="log.is_correct ? 'primary' : 'danger'"
                :timestamp="log.created_at"
                placement="top"
              >
                <el-card shadow="never" class="log-item clickable" @click="showLogDetail(log)">
                  <div class="log-header">
                    <span class="step-badge">第{{ index + 1 }}步</span>
                    <el-tag :type="log.is_correct ? 'success' : 'danger'" size="small">
                      {{ log.is_correct ? '正确' : '错误' }}
                    </el-tag>
                    <el-tag size="small">{{ moduleLabel(log.module) }}</el-tag>
                    <strong>{{ log.action }}</strong>
                    <span v-if="log.duration_ms" class="log-duration">{{ log.duration_ms }}ms</span>
                  </div>
                  <div v-if="log.description" class="log-desc">{{ log.description }}</div>
                  <div v-if="log.target_type" class="log-target">
                    目标: {{ log.target_type }} #{{ log.target_id }}
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>

            <el-empty v-else description="该学生暂无操作记录" />
          </el-card>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 操作详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="操作详情"
      direction="rtl"
      size="500px"
    >
      <template v-if="selectedLog">
        <!-- 基本信息 -->
        <el-descriptions :column="1" border size="small" style="margin-bottom: 20px">
          <el-descriptions-item label="操作人">{{ selectedLog.user_name || selectedLog.username }}</el-descriptions-item>
          <el-descriptions-item label="模块">{{ moduleLabel(selectedLog.module) }}</el-descriptions-item>
          <el-descriptions-item label="操作类型">{{ selectedLog.action }}</el-descriptions-item>
          <el-descriptions-item label="是否正确">
            <el-tag :type="selectedLog.is_correct ? 'success' : 'danger'" size="small">
              {{ selectedLog.is_correct ? '正确' : '错误' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="操作时间">{{ selectedLog.created_at }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedLog.description" label="描述">{{ selectedLog.description }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedLog.target_type" label="目标">
            {{ selectedLog.target_type }} #{{ selectedLog.target_id }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedLog.duration_ms" label="耗时">{{ selectedLog.duration_ms }} ms</el-descriptions-item>
        </el-descriptions>

        <!-- 请求数据 -->
        <div class="data-section" v-if="selectedLog.request_data">
          <div class="data-label">请求数据 (request_data)</div>
          <pre class="json-block">{{ JSON.stringify(selectedLog.request_data, null, 2) }}</pre>
        </div>

        <!-- 响应数据 -->
        <div class="data-section" v-if="selectedLog.response_data">
          <div class="data-label">响应数据 (response_data)</div>
          <pre class="json-block">{{ JSON.stringify(selectedLog.response_data, null, 2) }}</pre>
        </div>

        <el-empty v-if="!selectedLog.request_data && !selectedLog.response_data" description="无详细数据" />
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { logAPI, roomAPI } from '../../api'
import { CircleCheckFilled, CircleClose } from '@element-plus/icons-vue'

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const activeTab = ref('list')

// ===== 日志列表 =====
const logs = ref([])
const logStats = ref({ total: 0, correct: 0, error_rate: 0, module_stats: [] })
const pagination = ref({ page: 1, per_page: 15, total: 0 })
const users = ref([])
const filters = ref({ user_id: null, module: '', is_correct: '' })

const moduleOptions = [
  { value: 'purchase_request', label: '采购申请' },
  { value: 'purchase_order', label: '采购订单' },
  { value: 'transport_order', label: '运输订单' },
  { value: 'inbound_order', label: '入库管理' },
  { value: 'outbound_order', label: '出库管理' },
  { value: 'stock_count', label: '库存盘点' },
  { value: 'finance', label: '财务管理' },
  { value: 'contract', label: '合同管理' },
  { value: 'customer', label: '客户管理' },
  { value: 'event_injection', label: '事件注入' },
  { value: 'transport_exception', label: '运输异常' },
]

function moduleLabel(m) {
  return moduleOptions.find(o => o.value === m)?.label || m
}

// ===== 操作回放 =====
const replayUserId = ref(null)
const replayData = ref({
  total: 0, correct_count: 0, error_count: 0, accuracy_rate: 0,
  module_coverage: [], module_stats: [], timeline: [],
  time_span: { first: null, last: null, duration_minutes: 0 },
  time_analysis: []
})

// ===== 详情抽屉 =====
const detailDrawerVisible = ref(false)
const selectedLog = ref(null)

function showLogDetail(log) {
  selectedLog.value = log
  detailDrawerVisible.value = true
}

// ===== 数据加载 =====
async function loadLogs() {
  const params = {
    page: pagination.value.page,
    per_page: pagination.value.per_page,
    ...filters.value
  }
  Object.keys(params).forEach(k => !params[k] && k !== 'page' && k !== 'per_page' && delete params[k])

  const [logRes, statsRes] = await Promise.all([
    logAPI.list(params),
    logAPI.getStats(filters.value)
  ])
  logs.value = logRes.data.data.items || []
  pagination.value.total = logRes.data.data.total || 0
  logStats.value = statsRes.data.data || {}
}

async function loadReplayData() {
  if (!replayUserId.value) return
  try {
    const res = await logAPI.replay({ user_id: replayUserId.value })
    if (res.data.code === 200) {
      replayData.value = res.data.data
    }
  } catch (e) {
    console.error('加载回放数据失败:', e)
  }
}

function resetFilters() {
  filters.value = { user_id: null, module: '', is_correct: '' }
  pagination.value.page = 1
  loadLogs()
}

function handleTabChange(tab) {
  if (tab === 'replay' && replayUserId.value) {
    loadReplayData()
  }
}

onMounted(async () => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  // 加载用户列表
  try {
    const roomRes = await roomAPI.list()
    const allUsers = new Map()
    ;(roomRes.data.data || []).forEach(r => {
      ;(r.members || []).forEach(m => allUsers.set(m.id, m))
    })
    users.value = Array.from(allUsers.values())
  } catch (e) { /* ignore */ }

  await loadLogs()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.log-view { padding: 20px; }
.toolbar { margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.log-item { margin-bottom: 4px; }
.log-item.clickable { cursor: pointer; transition: box-shadow 0.2s; }
.log-item.clickable:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
.log-header { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.log-user { font-weight: bold; color: #409EFF; }
.log-desc { margin-top: 4px; font-size: 13px; color: #606266; }
.log-target { margin-top: 2px; font-size: 12px; color: #909399; }
.log-hint { margin-top: 4px; font-size: 11px; color: #C0C4CC; }
.log-duration { font-size: 12px; color: #909399; margin-left: auto; }

.step-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 50px; height: 22px; border-radius: 11px;
  background: #ECF5FF; color: #409EFF; font-size: 12px; font-weight: 600;
}

/* 模块覆盖 */
.module-coverage-item {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 12px; border-radius: 6px;
  border: 1px solid #EBEEF5; margin-bottom: 8px;
  font-size: 13px; color: #909399;
  transition: all 0.2s;
}
.module-coverage-item.covered {
  border-color: #E1F3D8; color: #606266; background: #F0F9EB;
}

/* 详情抽屉 */
.data-section { margin-bottom: 16px; }
.data-label {
  font-size: 13px; font-weight: 600; color: #303133;
  margin-bottom: 6px;
}
.json-block {
  background: #F5F7FA; border: 1px solid #EBEEF5;
  border-radius: 6px; padding: 12px; font-size: 12px;
  overflow-x: auto; max-height: 300px; overflow-y: auto;
  margin: 0; white-space: pre-wrap; word-break: break-all;
}

@media (max-width: 768px) {
  .log-view { padding: 10px; }
  .log-header { gap: 4px; }
  .step-badge { min-width: 40px; font-size: 11px; }
}
</style>
