<template>
  <el-container style="height: 100vh">
    <!-- 移动端遮罩 -->
    <div
      v-if="isMobile && sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    ></div>

    <!-- 侧边栏 -->
    <el-aside
      :width="isMobile ? '200px' : (isCollapse ? '64px' : '200px')"
      :class="{ 'aside-mobile': isMobile, 'aside-open': isMobile && sidebarOpen }"
    >
      <el-menu
        :default-active="activeMenu"
        :collapse="!isMobile && isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        @select="onMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <el-sub-menu v-if="menu.suppliers" index="base-data">
          <template #title><el-icon><Folder /></el-icon><span>基础数据</span></template>
          <el-menu-item v-if="menu.suppliers" index="/suppliers">供应商管理</el-menu-item>
          <el-menu-item v-if="menu.customers" index="/customers">客户管理</el-menu-item>
          <el-menu-item v-if="menu.goods" index="/goods">商品管理</el-menu-item>
          <el-menu-item v-if="menu.warehouses" index="/warehouses">仓库管理</el-menu-item>
          <el-menu-item v-if="menu.vehicles" index="/vehicles">车辆管理</el-menu-item>
          <el-menu-item v-if="menu.drivers" index="/drivers">司机管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.purchase" index="purchase">
          <template #title><el-icon><ShoppingCart /></el-icon><span>采购管理</span></template>
          <el-menu-item index="/purchase/requests">采购申请</el-menu-item>
          <el-menu-item index="/purchase/orders">采购订单</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.transport" index="transport">
          <template #title><el-icon><Van /></el-icon><span>运输管理</span></template>
          <el-menu-item index="/transport/orders">运输订单</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.warehouse" index="warehouse">
          <template #title><el-icon><Box /></el-icon><span>仓储管理</span></template>
          <el-menu-item index="/warehouse/inbound">入库管理</el-menu-item>
          <el-menu-item index="/warehouse/outbound">出库管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.inventory" index="inventory">
          <template #title><el-icon><Goods /></el-icon><span>库存管理</span></template>
          <el-menu-item index="/inventory">库存查询</el-menu-item>
          <el-menu-item index="/inventory/stock-count">库存盘点</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.reports" index="reports">
          <template #title><el-icon><DataAnalysis /></el-icon><span>数据报表</span></template>
          <el-menu-item index="/reports">可视化报表</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.contracts" index="contract">
          <template #title><el-icon><Document /></el-icon><span>合同管理</span></template>
          <el-menu-item index="/contract/purchase">采购合同</el-menu-item>
          <el-menu-item index="/contract/transport">运输合同</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.finance" index="finance">
          <template #title><el-icon><Money /></el-icon><span>财务管理</span></template>
          <el-menu-item index="/finance/overview">财务概览</el-menu-item>
          <el-menu-item index="/finance/payable">应付账款</el-menu-item>
          <el-menu-item index="/finance/receivable">应收账款</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.collab" index="collab">
          <template #title><el-icon><User /></el-icon><span>多人协作</span></template>
          <el-menu-item index="/collab/hall">协作大厅</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="menu.teacher" index="teacher">
          <template #title><el-icon><Setting /></el-icon><span>教师后台</span></template>
          <el-menu-item index="/teacher/scenes">场景管理</el-menu-item>
          <el-menu-item index="/teacher/progress">进度监控</el-menu-item>
          <el-menu-item index="/teacher/events">事件注入</el-menu-item>
          <el-menu-item index="/teacher/scores">成绩统计</el-menu-item>
          <el-menu-item index="/teacher/logs">操作日志</el-menu-item>
        </el-sub-menu>

        <el-menu-item v-if="menu.users" index="/users">
          <el-icon><Avatar /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/alerts">
          <el-icon><Bell /></el-icon>
          <template #title>预警中心</template>
        </el-menu-item>

        <el-menu-item index="/notifications">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>站内通知</template>
        </el-menu-item>

        <el-menu-item index="/help">
          <el-icon><QuestionFilled /></el-icon>
          <template #title>帮助中心</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-left">
          <!-- 桌面端折叠按钮 -->
          <el-icon
            v-if="!isMobile"
            class="collapse-btn"
            @click="isCollapse = !isCollapse"
          >
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <!-- 移动端汉堡菜单 -->
          <el-icon
            v-if="isMobile"
            class="collapse-btn"
            @click="sidebarOpen = !sidebarOpen"
          >
            <Menu />
          </el-icon>
          <h3>物流教学软件</h3>
        </div>
        <div class="header-right">
          <el-popover placement="bottom-end" :width="360" trigger="click" @show="onBellPopoverShow">
            <template #reference>
              <el-badge :value="notificationStore.unreadCount" :hidden="notificationStore.unreadCount === 0" :max="99">
                <el-icon class="bell-btn">
                  <Bell />
                </el-icon>
              </el-badge>
            </template>
            <div class="notification-popover">
              <div class="popover-header">
                <span class="popover-title">通知消息</span>
                <el-button link type="primary" size="small" @click="handleMarkAllRead"
                  :disabled="notificationStore.unreadCount === 0">全部已读</el-button>
              </div>
              <div v-if="recentNotifications.length === 0" class="popover-empty">
                暂无通知
              </div>
              <div v-else class="popover-list">
                <div
                  v-for="item in recentNotifications"
                  :key="item.id"
                  class="popover-item"
                  :class="{ unread: !item.is_read }"
                  @click="handleNotifClick(item)"
                >
                  <div class="popover-item-title">
                    <span class="dot" v-if="!item.is_read"></span>
                    {{ item.title }}
                  </div>
                  <div class="popover-item-time">{{ formatNotifTime(item.created_at) }}</div>
                </div>
              </div>
              <div class="popover-footer">
                <el-button link type="primary" @click="goToNotifications">查看全部通知</el-button>
              </div>
            </div>
          </el-popover>
          <el-tag size="small" v-if="!isMobile && authStore.user?.role_name" type="info">
            {{ authStore.user.role_name }}
          </el-tag>
          <span v-if="!isMobile">{{ authStore.user?.real_name }}</span>
          <el-button link @click="handleLogout">
            {{ isMobile ? '退出' : '退出登录' }}
          </el-button>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'
import { useSocket, connect, on, off } from '../utils/websocket'
import { ElMessageBox } from 'element-plus'
import {
  HomeFilled, Folder, ShoppingCart, Van, Box, Goods,
  User, Setting, DataAnalysis, Fold, Expand, Menu,
  Money, Document, Bell, QuestionFilled, Avatar, ChatDotRound
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const { isConnected } = useSocket()

const activeMenu = computed(() => route.path)

// 菜单权限（从 auth store 获取）
const menu = computed(() => authStore.menuPermissions || {
  suppliers: true, customers: true, goods: true, warehouses: true,
  vehicles: true, drivers: true, purchase: true, transport: true,
  warehouse: true, inventory: true, reports: true, contracts: true,
  finance: true, collab: true, teacher: true, alerts: true,
  help: true, users: true,
})

// 响应式：检测屏幕宽度
const isMobile = ref(false)
const isCollapse = ref(false)
const sidebarOpen = ref(false)

const checkScreenWidth = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}

// 移动端选择菜单后自动关闭侧边栏
const onMenuSelect = () => {
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}

// 通知相关
const recentNotifications = computed(() => notificationStore.notifications.slice(0, 5))

const onBellPopoverShow = () => {
  notificationStore.fetchNotifications({ page: 1, per_page: 5 })
}

const handleMarkAllRead = () => {
  notificationStore.markAllRead()
}

const goToNotifications = () => {
  router.push('/notifications')
}

const goToAlerts = () => {
  router.push('/alerts')
}

const handleNotifClick = (item) => {
  if (!item.is_read) {
    notificationStore.markAsRead(item.id)
  }
  // 跳转到通知中心
  router.push('/notifications')
}

const formatNotifTime = (timeStr) => {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  const pad = n => String(n).padStart(2, '0')
  return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// WebSocket 监听新通知
const onNewNotification = (data) => {
  notificationStore.onNewNotification(data)
}

onMounted(() => {
  checkScreenWidth()
  window.addEventListener('resize', checkScreenWidth)
  // 获取未读数量
  notificationStore.fetchUnreadCount()
  // 连接 WebSocket 并监听通知
  connect()
  on('new_notification', onNewNotification)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenWidth)
  off('new_notification', onNewNotification)
})

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    authStore.logout()
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h3 {
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}

.collapse-btn:hover {
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  white-space: nowrap;
}

.bell-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}

.bell-btn:hover {
  color: #409EFF;
}

.notification-popover {
  margin: -12px;
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #EBEEF5;
}

.popover-title {
  font-weight: 600;
  font-size: 15px;
}

.popover-empty {
  padding: 24px 16px;
  text-align: center;
  color: #909399;
}

.popover-list {
  max-height: 300px;
  overflow-y: auto;
}

.popover-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f5f7fa;
  transition: background 0.2s;
}

.popover-item:hover {
  background-color: #f5f7fa;
}

.popover-item.unread {
  background-color: #ecf5ff;
}

.popover-item-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.popover-item.unread .popover-item-title {
  font-weight: 600;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #409EFF;
  flex-shrink: 0;
}

.popover-item-time {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  margin-left: 12px;
}

.popover-footer {
  padding: 8px 16px;
  text-align: center;
  border-top: 1px solid #EBEEF5;
}

.el-aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
}

.el-menu {
  border-right: none;
}

/* 移动端侧边栏：默认隐藏在左侧 */
.aside-mobile {
  position: fixed;
  left: -200px;
  top: 0;
  height: 100vh;
  z-index: 2001;
  transition: left 0.3s;
}

.aside-mobile.aside-open {
  left: 0;
}

/* 移动端遮罩 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 2000;
}

@media (max-width: 768px) {
  .el-header {
    padding: 0 12px;
  }

  .header-right {
    gap: 8px;
  }

  .header-right span {
    display: none;
  }
}
</style>
