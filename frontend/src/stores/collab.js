import { defineStore } from 'pinia'
import { ref } from 'vue'
import { roomAPI, sceneAPI, eventAPI } from '../api'
import { useSocket, connect, disconnect, joinGroup, leaveGroup, joinScene } from '../utils/websocket'

export const useCollabStore = defineStore('collab', () => {
  const rooms = ref([])
  const currentRoom = ref(null)
  const scenes = ref([])
  const eventTypes = ref([])
  const isWsConnected = ref(false)
  const activeEvents = ref([])  // 当前活跃的突发事件

  // 加载房间列表
  async function loadRooms(sceneId = null) {
    try {
      const res = await roomAPI.list(sceneId ? { scene_id: sceneId } : {})
      rooms.value = res.data.data || []
    } catch (e) {
      console.error('加载房间失败', e)
    }
  }

  // 加载场景列表
  async function loadScenes() {
    try {
      const res = await sceneAPI.list()
      scenes.value = res.data.data || []
    } catch (e) {
      console.error('加载场景失败', e)
    }
  }

  // 加载事件类型
  async function loadEventTypes() {
    try {
      const res = await eventAPI.getTypes()
      eventTypes.value = res.data.data || []
    } catch (e) {
      console.error('加载事件类型失败', e)
    }
  }

  // 创建房间
  async function createRoom(data) {
    const res = await roomAPI.create(data)
    if (res.data.code === 200) {
      await loadRooms()
      return { success: true, data: res.data.data }
    }
    return { success: false, message: res.data.message }
  }

  // 加入房间
  async function joinRoom(roomId, roleId = null) {
    const res = await roomAPI.join(roomId, { role_id: roleId })
    if (res.data.code === 200) {
      currentRoom.value = res.data.data
      // WebSocket 加入房间
      joinGroup(roomId)
      return { success: true, data: res.data.data }
    }
    return { success: false, message: res.data.message }
  }

  // 离开房间
  async function leaveCurrentRoom() {
    if (!currentRoom.value) return
    const roomId = currentRoom.value.id
    leaveGroup(roomId)
    try {
      await roomAPI.leave(roomId)
    } catch (e) {
      console.error('离开房间失败', e)
    }
    currentRoom.value = null
  }

  // 关闭房间
  async function closeRoom(roomId) {
    const res = await roomAPI.close(roomId)
    if (res.data.code === 200) {
      await loadRooms()
      return { success: true }
    }
    return { success: false, message: res.data.message }
  }

  // 注入事件
  async function injectEvent(data) {
    const res = await eventAPI.inject(data)
    if (res.data.code === 200) {
      activeEvents.value.push(res.data.data)
      return { success: true, data: res.data.data }
    }
    return { success: false, message: res.data.message }
  }

  // 初始化 WebSocket 连接
  function initSocket() {
    connect()
    // 监听突发事件
    const { on } = useSocket()
    on('event_injected', (data) => {
      activeEvents.value.push(data)
    })
  }

  // 断开 WebSocket
  function destroySocket() {
    disconnect()
    activeEvents.value = []
  }

  return {
    rooms, currentRoom, scenes, eventTypes, isWsConnected, activeEvents,
    loadRooms, loadScenes, loadEventTypes,
    createRoom, joinRoom, leaveCurrentRoom, closeRoom,
    injectEvent, initSocket, destroySocket
  }
})
