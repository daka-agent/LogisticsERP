import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)

  // 获取通知列表
  async function fetchNotifications(params = {}) {
    loading.value = true
    try {
      const res = await axios.get('/notifications', { params })
      if (res.data.code === 200) {
        notifications.value = res.data.data.items
        unreadCount.value = res.data.data.unread_count
      }
    } catch (error) {
      console.error('获取通知列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取未读数量
  async function fetchUnreadCount() {
    try {
      const res = await axios.get('/notifications/unread-count')
      if (res.data.code === 200) {
        unreadCount.value = res.data.data.count
      }
    } catch (error) {
      console.error('获取未读数量失败:', error)
    }
  }

  // 标记已读
  async function markAsRead(id) {
    try {
      const res = await axios.put(`/notifications/${id}/read`)
      if (res.data.code === 200) {
        const notif = notifications.value.find(n => n.id === id)
        if (notif) notif.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  // 全部已读
  async function markAllRead() {
    try {
      const res = await axios.post('/notifications/read-all')
      if (res.data.code === 200) {
        notifications.value.forEach(n => n.is_read = true)
        unreadCount.value = 0
      }
    } catch (error) {
      console.error('全部已读失败:', error)
    }
  }

  // 删除通知
  async function deleteNotification(id) {
    try {
      const res = await axios.delete(`/notifications/${id}`)
      if (res.data.code === 200) {
        const notif = notifications.value.find(n => n.id === id)
        if (notif && !notif.is_read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
        notifications.value = notifications.value.filter(n => n.id !== id)
      }
    } catch (error) {
      console.error('删除通知失败:', error)
    }
  }

  // 收到新通知（WebSocket 调用）
  function onNewNotification(data) {
    unreadCount.value += 1
    notifications.value.unshift(data)
    // 桌面通知
    if (Notification.permission === 'granted') {
      new Notification('物流教学软件', {
        body: data.title,
        icon: '/vite.svg'
      })
    }
  }

  return {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllRead,
    deleteNotification,
    onNewNotification
  }
})
