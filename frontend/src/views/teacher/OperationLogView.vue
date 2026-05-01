<template>
  <div class="log-view">
    <div class="toolbar">
      <h3 style="margin: 0">操作日志</h3>
    </div>

    <!-- 筛选条件 -->
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form :inline="true" :model="filters">
        <el-form-item label="用户">
          <el-select v-model="filters.user_id" placeholder="全部用户" clearable style="width: 150px">
            <el-option v-for="u in users" :key="u.id" :label="u.real_name" :value="u.id" />
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
      <el-col :span="6">
        <el-statistic title="总操作数" :value="logStats.total" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="正确操作" :value="logStats.correct" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="错误率" :value="logStats.error_rate" suffix="%" />
      </el-col>
      <el-col :span="6">
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
          <el-card shadow="never" class="log-item">
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
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-empty v-if="logs.length === 0" description="暂无操作日志" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { logAPI, roomAPI } from '../../api'

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

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
  { value: 'event_injection', label: '事件注入' }
]

function moduleLabel(m) {
  return moduleOptions.find(o => o.value === m)?.label || m
}

async function loadLogs() {
  const params = {
    page: pagination.value.page,
    per_page: pagination.value.per_page,
    ...filters.value
  }
  // 清除空值
  Object.keys(params).forEach(k => !params[k] && k !== 'page' && k !== 'per_page' && delete params[k])

  const [logRes, statsRes] = await Promise.all([
    logAPI.list(params),
    logAPI.getStats(filters.value)
  ])
  logs.value = logRes.data.data.items || []
  pagination.value.total = logRes.data.data.total || 0
  logStats.value = statsRes.data.data || {}
}

function resetFilters() {
  filters.value = { user_id: null, module: '', is_correct: '' }
  pagination.value.page = 1
  loadLogs()
}

onMounted(async () => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  // 加载用户列表（从房间成员获取）
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
.toolbar { margin-bottom: 16px; }
.log-item { margin-bottom: 4px; }
.log-header { display: flex; align-items: center; gap: 6px; }
.log-user { font-weight: bold; color: #409EFF; }
.log-desc { margin-top: 4px; font-size: 13px; color: #606266; }
.log-target { margin-top: 2px; font-size: 12px; color: #909399; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
