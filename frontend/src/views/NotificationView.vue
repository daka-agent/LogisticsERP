<template>
  <div class="notification-page">
    <PageGuide module="notification" />

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-radio-group v-model="currentType" @change="handleFilterChange">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="approval">审批通知</el-radio-button>
          <el-radio-button label="todo">待办任务</el-radio-button>
          <el-radio-button label="system">系统通知</el-radio-button>
          <el-radio-button label="alert">预警提醒</el-radio-button>
          <el-radio-button label="event">突发事件</el-radio-button>
        </el-radio-group>
        <el-switch
          v-model="unreadOnly"
          active-text="仅未读"
          @change="handleFilterChange"
          style="margin-left: 16px"
        />
      </div>
      <div class="toolbar-right">
        <el-button @click="handleMarkAllRead" :disabled="notificationStore.unreadCount === 0">
          全部已读
        </el-button>
        <el-button @click="handleRefresh" :icon="Refresh">刷新</el-button>
      </div>
    </div>

    <!-- 通知列表 -->
    <el-table
      :data="notificationStore.notifications"
      v-loading="notificationStore.loading"
      @row-click="handleRowClick"
      style="width: 100%"
      stripe
    >
      <el-table-column label="" width="50">
        <template #default="{ row }">
          <el-icon v-if="!row.is_read" color="#409EFF" :size="18"><Bell /></el-icon>
          <el-icon v-else color="#C0C4CC" :size="18"><Bell /></el-icon>
        </template>
      </el-table-column>

      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="typeTagMap[row.type]?.tagType || 'info'" size="small">
            {{ typeTagMap[row.type]?.label || row.type }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="标题" min-width="200">
        <template #default="{ row }">
          <span :class="{ 'unread-text': !row.is_read }">{{ row.title }}</span>
        </template>
      </el-table-column>

      <el-table-column label="内容" min-width="250" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="content-text">{{ row.content }}</span>
        </template>
      </el-table-column>

      <el-table-column label="发送人" width="100">
        <template #default="{ row }">
          {{ row.sender_name || '系统' }}
        </template>
      </el-table-column>

      <el-table-column label="时间" width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="!row.is_read"
            link
            type="primary"
            size="small"
            @click.stop="handleMarkRead(row)"
          >已读</el-button>
          <el-button
            link
            type="danger"
            size="small"
            @click.stop="handleDelete(row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @size-change="handleFilterChange"
        @current-change="handleFilterChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notification'
import { Bell, Refresh } from '@element-plus/icons-vue'
import PageGuide from '../components/PageGuide.vue'

const router = useRouter()
const notificationStore = useNotificationStore()

const currentType = ref('')
const unreadOnly = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const typeTagMap = {
  approval: { label: '审批', tagType: 'warning' },
  todo: { label: '待办', tagType: '' },
  system: { label: '系统', tagType: 'info' },
  alert: { label: '预警', tagType: 'danger' },
  event: { label: '事件', tagType: 'danger' },
  message: { label: '消息', tagType: 'success' }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const handleFilterChange = () => {
  notificationStore.fetchNotifications({
    page: currentPage.value,
    per_page: pageSize.value,
    type: currentType.value || undefined,
    unread_only: unreadOnly.value || undefined
  }).then(() => {
    // 更新 total（如果有数据的话可以从 store 中取，这里简化处理）
    // list 接口返回的 data 中有 total
  })
}

const handleMarkRead = (row) => {
  notificationStore.markAsRead(row.id)
}

const handleMarkAllRead = () => {
  notificationStore.markAllRead()
}

const handleDelete = (row) => {
  notificationStore.deleteNotification(row.id)
}

const handleRefresh = () => {
  handleFilterChange()
}

// 通知类型到路由的映射
const routeMap = {
  purchase_request: '/purchase/requests',
  transport_order: '/transport/orders',
  purchase_contract: '/contract/purchase',
  transport_contract: '/contract/transport',
}

const handleRowClick = (row) => {
  // 标记已读
  if (!row.is_read) {
    notificationStore.markAsRead(row.id)
  }
  // 如果有关联对象，跳转到对应页面
  if (row.reference_type && row.reference_id && routeMap[row.reference_type]) {
    router.push(routeMap[row.reference_type])
  }
}

onMounted(() => {
  handleFilterChange()
})
</script>

<style scoped>
.notification-page {
  padding: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.unread-text {
  font-weight: 600;
  color: #303133;
}

.content-text {
  color: #606266;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-left {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
