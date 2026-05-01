<template>
  <div class="home">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h2>{{ greeting }}好，{{ authStore.user?.real_name }} 👋</h2>
        <p class="subtitle">{{ currentDate }} · {{ authStore.user?.role_name }}</p>
      </div>
      <div class="welcome-actions" v-if="!isMobile">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon> 刷新数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="isMobile ? 10 : 16" class="stats-row">
      <el-col :xs="12" :sm="12" :md="6" :lg="4" v-for="card in statCards" :key="card.title">
        <div class="stat-card" :style="{ borderLeftColor: card.color }">
          <div class="stat-icon" :style="{ backgroundColor: card.bgColor }">
            <el-icon :size="24" :color="card.color"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-title">{{ card.title }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 + 待办事项 -->
    <el-row :gutter="isMobile ? 10 : 20" class="content-row">
      <!-- 快捷操作 -->
      <el-col :xs="24" :sm="24" :md="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>⚡ 快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div
              v-for="action in quickActions"
              :key="action.name"
              class="action-item"
              @click="router.push(action.path)"
            >
              <el-icon :size="28" :color="action.color"><component :is="action.icon" /></el-icon>
              <span>{{ action.name }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 我的待办 -->
      <el-col :xs="24" :sm="24" :md="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>📋 我的待办</span>
              <el-tag v-if="myTasks.length" size="small" type="danger">{{ myTasks.length }}</el-tag>
            </div>
          </template>
          <el-empty v-if="myTasks.length === 0" description="暂无待办事项" :image-size="60" />
          <div v-else class="task-list">
            <div v-for="task in myTasks" :key="task.id" class="task-item" @click="goTask(task)">
              <el-icon :color="getTaskColor(task.status)"><Clock /></el-icon>
              <span class="task-title">{{ task.title }}</span>
              <span class="task-time">{{ task.created_at }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 近期动态 -->
    <el-row :gutter="isMobile ? 10 : 20" class="content-row">
      <el-col :xs="24">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>📊 近期动态</span>
              <el-button text size="small" @click="router.push('/teacher/logs')" v-if="authStore.isTeacher">查看全部</el-button>
            </div>
          </template>
          <el-empty v-if="recentActivities.length === 0" description="暂无操作记录" :image-size="60" />
          <el-timeline v-else class="activity-timeline">
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="activity.created_at"
              placement="top"
              :type="getActivityType(activity.module)"
            >
              <div class="activity-content">
                <strong>{{ activity.user_name }}</strong>
                <span class="activity-action">{{ getActionText(activity.action) }}</span>
                <span class="activity-target">{{ activity.target }}</span>
              </div>
              <div class="activity-detail" v-if="activity.detail">{{ activity.detail }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 模块状态概览 -->
    <el-row :gutter="isMobile ? 10 : 20" class="content-row">
      <el-col :xs="24">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>📦 模块状态概览</span>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col :xs="12" :sm="8" :md="4" v-for="mod in moduleStatus" :key="mod.name">
              <div class="module-card" @click="router.push(mod.path)">
                <div class="module-icon" :style="{ backgroundColor: mod.bgColor }">
                  <el-icon :size="28" :color="mod.color"><component :is="mod.icon" /></el-icon>
                </div>
                <div class="module-name">{{ mod.name }}</div>
                <div class="module-count">{{ mod.count }} <small>项</small></div>
                <div class="module-status">
                  <el-tag :type="mod.statusType" size="small">{{ mod.statusText }}</el-tag>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import {
  ShoppingCart, Van, House, Box, DataLine,
  User, Clock, Refresh,
  Document, OfficeBuilding, Finished
} from '@element-plus/icons-vue'
import axios from 'axios'

const authStore = useAuthStore()
const router = useRouter()
const isMobile = ref(false)

// 问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨'
  if (hour < 9) return '早上'
  if (hour < 12) return '上午'
  if (hour < 14) return '中午'
  if (hour < 18) return '下午'
  return '晚上'
})

const currentDate = computed(() => {
  const now = new Date()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日 星期${weekdays[now.getDay()]}`
})

// 统计数据
const stats = ref({
  purchase: { request_total: 0, request_pending: 0, order_total: 0 },
  transport: { order_total: 0, order_in_transit: 0 },
  warehouse: { inbound_pending: 0, outbound_pending: 0 },
  inventory: { item_total: 0, item_low_stock: 0 },
  collab: { active_rooms: 0 },
  today_ops: 0,
})

// 统计卡片配置
const statCards = computed(() => [
  {
    title: '采购申请',
    value: stats.value.purchase.request_pending,
    suffix: `/${stats.value.purchase.request_total}`,
    icon: ShoppingCart,
    color: '#409EFF',
    bgColor: '#ECF5FF',
  },
  {
    title: '运输订单',
    value: stats.value.transport.order_in_transit,
    suffix: `/${stats.value.transport.order_total}`,
    icon: Van,
    color: '#67C23A',
    bgColor: '#F0F9EB',
  },
  {
    title: '待入库',
    value: stats.value.warehouse.inbound_pending,
    icon: OfficeBuilding,
    color: '#E6A23C',
    bgColor: '#FDF6EC',
  },
  {
    title: '库存物品',
    value: stats.value.inventory.item_total,
    suffix: stats.value.inventory.item_low_stock ? ` · ${stats.value.inventory.item_low_stock}预警` : '',
    icon: Box,
    color: '#F56C6C',
    bgColor: '#FEF0F0',
  },
  {
    title: '协作房间',
    value: stats.value.collab.active_rooms,
    icon: User,
    color: '#909399',
    bgColor: '#F4F4F5',
  },
  {
    title: '今日操作',
    value: stats.value.today_ops,
    icon: DataLine,
    color: '#409EFF',
    bgColor: '#ECF5FF',
  },
])

// 快捷操作
const quickActions = [
  { name: '采购申请', icon: Document, color: '#409EFF', path: '/purchase/requests' },
  { name: '运输订单', icon: Van, color: '#67C23A', path: '/transport/orders' },
  { name: '入库操作', icon: OfficeBuilding, color: '#E6A23C', path: '/warehouse/inbound' },
  { name: '出库操作', icon: Finished, color: '#F56C6C', path: '/warehouse/outbound' },
  { name: '库存查询', icon: Box, color: '#909399', path: '/inventory' },
  { name: '协作大厅', icon: User, color: '#409EFF', path: '/collab/hall' },
]

// 我的待办
const myTasks = ref([])

// 近期动态
const recentActivities = ref([])

// 模块状态
const moduleStatus = computed(() => [
  {
    name: '采购管理',
    count: stats.value.purchase.request_pending,
    statusText: stats.value.purchase.request_pending > 0 ? '有待审批' : '运行正常',
    statusType: stats.value.purchase.request_pending > 0 ? 'warning' : 'success',
    icon: ShoppingCart,
    color: '#409EFF',
    bgColor: '#ECF5FF',
    path: '/purchase/requests',
  },
  {
    name: '运输管理',
    count: stats.value.transport.order_in_transit,
    statusText: stats.value.transport.order_pending > 0 ? '有待调度' : '运行正常',
    statusType: stats.value.transport.order_pending > 0 ? 'warning' : 'success',
    icon: Van,
    color: '#67C23A',
    bgColor: '#F0F9EB',
    path: '/transport/orders',
  },
  {
    name: '仓储管理',
    count: stats.value.warehouse.inbound_pending + stats.value.warehouse.outbound_pending,
    statusText: (stats.value.warehouse.inbound_pending + stats.value.warehouse.outbound_pending) > 0 ? '有待处理' : '运行正常',
    statusType: (stats.value.warehouse.inbound_pending + stats.value.warehouse.outbound_pending) > 0 ? 'warning' : 'success',
    icon: House,
    color: '#E6A23C',
    bgColor: '#FDF6EC',
    path: '/warehouse/inbound',
  },
  {
    name: '库存管理',
    count: stats.value.inventory.item_low_stock,
    statusText: stats.value.inventory.item_low_stock > 0 ? '库存预警' : '库存充足',
    statusType: stats.value.inventory.item_low_stock > 0 ? 'danger' : 'success',
    icon: Box,
    color: '#F56C6C',
    bgColor: '#FEF0F0',
    path: '/inventory',
  },
  {
    name: '数据报表',
    count: 4,
    statusText: '可用',
    statusType: 'success',
    icon: DataLine,
    color: '#909399',
    bgColor: '#F4F4F5',
    path: '/reports',
  },
  {
    name: '协作模式',
    count: stats.value.collab.active_rooms,
    statusText: stats.value.collab.active_rooms > 0 ? '进行中' : '暂无',
    statusType: stats.value.collab.active_rooms > 0 ? 'primary' : 'info',
    icon: User,
    color: '#409EFF',
    bgColor: '#ECF5FF',
    path: '/collab/hall',
  },
])

// 获取数据
const fetchStats = async () => {
  try {
    const res = await axios.get('/api/dashboard/stats')
    if (res.data.code === 200) {
      stats.value = res.data.data
    }
  } catch (err) {
    console.error('获取统计数据失败:', err)
  }
}

const fetchMyTasks = async () => {
  try {
    const res = await axios.get('/api/dashboard/my-tasks')
    if (res.data.code === 200) {
      myTasks.value = res.data.data
    }
  } catch (err) {
    console.error('获取待办事项失败:', err)
  }
}

const fetchRecentActivities = async () => {
  try {
    const res = await axios.get('/api/dashboard/recent-activities?limit=8')
    if (res.data.code === 200) {
      recentActivities.value = res.data.data
    }
  } catch (err) {
    console.error('获取近期动态失败:', err)
  }
}

const refreshData = async () => {
  await Promise.all([fetchStats(), fetchMyTasks(), fetchRecentActivities()])
  ElMessage.success('数据已刷新')
}

// 工具函数
const getTaskColor = (status) => {
  const colors = { pending: '#E6A23C', approved: '#409EFF', completed: '#67C23A' }
  return colors[status] || '#909399'
}

const getActivityType = (module) => {
  const types = {
    purchase: 'primary',
    transport: 'success',
    warehouse: 'warning',
    inventory: 'danger',
    collab: 'info',
  }
  return types[module] || 'info'
}

const getActionText = (action) => {
  const texts = {
    create: '创建了',
    approve: '审批了',
    reject: '驳回了',
    dispatch: '调度了',
    deliver: '发货了',
    receive: '签收了',
    inbound: '入库了',
    outbound: '出库了',
    adjust: '调整了',
    count: '盘点了',
  }
  return texts[action] || action
}

const goTask = (task) => {
  const pathMap = {
    purchase_request: '/purchase/requests',
    transport_order: '/transport/orders',
    inbound_order: '/warehouse/inbound',
    outbound_order: '/warehouse/outbound',
  }
  router.push(pathMap[task.type] || '/')
}

// 响应式处理
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }
onMounted(() => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  refreshData()
})
onUnmounted(() => { window.removeEventListener('resize', checkWidth) })
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}
.welcome-section h2 {
  font-size: 24px;
  margin-bottom: 8px;
}
.welcome-section .subtitle {
  font-size: 14px;
  opacity: 0.85;
}
.welcome-actions .el-button {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
}
.welcome-actions .el-button:hover {
  background: rgba(255,255,255,0.3);
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 12px;
  transition: transform 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 22px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}
.stat-value small {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}
.stat-title {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* 内容区域 */
.content-row {
  margin-bottom: 20px;
}
.section-card {
  height: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

/* 快捷操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #EBEEF5;
}
.action-item:hover {
  background: #F5F7FA;
  border-color: #409EFF;
  transform: translateY(-2px);
}
.action-item span {
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}

/* 待办事项 */
.task-list {
  max-height: 300px;
  overflow-y: auto;
}
.task-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #EBEEF5;
  cursor: pointer;
  transition: background 0.2s;
}
.task-item:last-child {
  border-bottom: none;
}
.task-item:hover {
  background: #F5F7FA;
  margin: 0 -20px;
  padding: 10px 20px;
}
.task-title {
  flex: 1;
  margin-left: 8px;
  font-size: 14px;
  color: #303133;
}
.task-time {
  font-size: 12px;
  color: #909399;
}

/* 近期动态 */
.activity-timeline {
  max-height: 400px;
  overflow-y: auto;
  padding-left: 10px;
}
.activity-content {
  font-size: 14px;
}
.activity-content strong {
  color: #409EFF;
}
.activity-action {
  margin: 0 4px;
  color: #606266;
}
.activity-target {
  color: #303133;
}
.activity-detail {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 模块状态 */
.module-card {
  text-align: center;
  padding: 16px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #EBEEF5;
  height: 100%;
}
.module-card:hover {
  border-color: #409EFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.module-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}
.module-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 4px;
}
.module-count {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}
.module-count small {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .home {
    padding: 10px;
  }
  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
    padding: 16px;
  }
  .welcome-section h2 {
    font-size: 18px;
  }
  .welcome-actions {
    margin-top: 12px;
    width: 100%;
  }
  .stat-card {
    padding: 12px;
  }
  .stat-icon {
    width: 36px;
    height: 36px;
  }
  .stat-value {
    font-size: 18px;
  }
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  .action-item {
    padding: 12px 4px;
  }
  .module-card {
    padding: 12px 4px;
  }
  .module-icon {
    width: 36px;
    height: 36px;
  }
  .module-count {
    font-size: 16px;
  }
}
</style>
