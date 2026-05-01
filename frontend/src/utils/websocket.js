import { io } from 'socket.io-client'
import { useAuthStore } from '../stores/auth'

// WebSocket 连接管理
let socket = null
const eventHandlers = new Map()

// 连接状态
const isConnected = ref(false)
const connectedUsers = ref([])

function connect() {
  if (socket && socket.connected) return

  socket = io('http://localhost:5000', {
    transports: ['websocket', 'polling'],
    withCredentials: true,
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 10
  })

  socket.on('connect', () => {
    isConnected.value = true
    console.log('WebSocket 已连接')
  })

  socket.on('disconnect', () => {
    isConnected.value = false
    console.log('WebSocket 已断开')
  })

  socket.on('connected', (data) => {
    console.log('服务器确认连接:', data)
  })

  // 订单状态变更
  socket.on('order_status_changed', (data) => {
    console.log('订单状态变更:', data)
    emit('order_status_changed', data)
  })

  // 待办通知
  socket.on('todo_notification', (data) => {
    console.log('待办通知:', data)
    emit('todo_notification', data)
    // 弹出桌面通知
    if (Notification.permission === 'granted') {
      new Notification('物流教学软件', {
        body: data.message,
        icon: '/vite.svg'
      })
    }
  })

  // 突发事件
  socket.on('event_injected', (data) => {
    console.log('突发事件:', data)
    emit('event_injected', data)
  })

  // 用户加入房间
  socket.on('user_joined', (data) => {
    console.log('用户加入:', data)
    emit('user_joined', data)
  })

  // 用户离开房间
  socket.on('user_left', (data) => {
    console.log('用户离开:', data)
    emit('user_left', data)
  })

  // 小组进度更新
  socket.on('group_progress', (data) => {
    console.log('进度更新:', data)
    emit('group_progress', data)
  })
}

function disconnect() {
  if (socket) {
    socket.disconnect()
    socket = null
    isConnected.value = false
  }
}

// 加入小组房间
function joinGroup(groupId) {
  if (socket && socket.connected) {
    socket.emit('join_group', { group_id: groupId })
  }
}

// 离开小组房间
function leaveGroup(groupId) {
  if (socket && socket.connected) {
    socket.emit('leave_group', { group_id: groupId })
  }
}

// 加入场景监控
function joinScene(sceneId) {
  if (socket && socket.connected) {
    socket.emit('join_scene', { scene_id: sceneId })
  }
}

// 事件监听
function on(event, callback) {
  if (!eventHandlers.has(event)) {
    eventHandlers.set(event, new Set())
  }
  eventHandlers.get(event).add(callback)
}

function off(event, callback) {
  if (eventHandlers.has(event)) {
    eventHandlers.get(event).delete(callback)
  }
}

// 内部事件分发
function emit(event, data) {
  if (eventHandlers.has(event)) {
    eventHandlers.get(event).forEach(callback => callback(data))
  }
}

// Vue composable 导出
function useSocket() {
  return {
    socket,
    isConnected,
    connect,
    disconnect,
    joinGroup,
    leaveGroup,
    joinScene,
    on,
    off
  }
}

export { useSocket, connect, disconnect, joinGroup, leaveGroup, joinScene, on, off, isConnected }

// ref 需要从 vue 导入
import { ref } from 'vue'
