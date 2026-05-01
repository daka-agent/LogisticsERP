<template>
  <div class="room-hall">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>创建房间
      </el-button>
      <el-select v-model="filterScene" placeholder="筛选场景" clearable style="width: 200px; margin-left: 12px" @change="loadRooms">
        <el-option v-for="s in scenes" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <div class="ws-status">
        <el-tag :type="isWsConnected ? 'success' : 'danger'" size="small">
          {{ isWsConnected ? 'WebSocket 已连接' : 'WebSocket 未连接' }}
        </el-tag>
      </div>
    </div>

    <!-- 房间卡片列表 -->
    <div class="room-grid">
      <el-card v-for="room in rooms" :key="room.id" class="room-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="room-name">{{ room.group_name }}</span>
            <el-tag :type="room.status === 'active' ? 'success' : 'info'" size="small">
              {{ room.status === 'active' ? '进行中' : '已结束' }}
            </el-tag>
          </div>
        </template>

        <div class="card-body">
          <div v-if="room.scene" class="info-row">
            <span class="label">场景：</span>
            <span>{{ room.scene.name }}</span>
            <el-tag size="small" :type="difficultyType(room.scene.difficulty)">{{ difficultyLabel(room.scene.difficulty) }}</el-tag>
          </div>
          <div class="info-row">
            <span class="label">成员：</span>
            <span>{{ room.member_count }} / 6 人</span>
          </div>
          <div v-if="room.members && room.members.length" class="member-list">
            <el-tag v-for="m in room.members" :key="m.id" size="small" style="margin: 2px">
              {{ m.real_name }} ({{ m.role_name }})
            </el-tag>
          </div>
        </div>

        <div class="card-footer">
          <el-button
            v-if="room.status === 'active' && room.member_count < 6 && !isInRoom(room)"
            type="primary" size="small"
            @click="handleJoin(room)"
          >
            加入房间
          </el-button>
          <el-button
            v-if="isInRoom(room)"
            type="danger" size="small"
            @click="handleLeave(room)"
          >
            离开房间
          </el-button>
          <el-button
            v-if="isAdmin && room.status === 'active'"
            type="warning" size="small"
            @click="handleClose(room)"
          >
            关闭房间
          </el-button>
        </div>
      </el-card>

      <!-- 空状态 -->
      <el-empty v-if="rooms.length === 0" description="暂无协作房间" />
    </div>

    <!-- 创建房间对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建协作房间" width="480px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="房间名称" required>
          <el-input v-model="createForm.group_name" placeholder="如：第1组" />
        </el-form-item>
        <el-form-item label="教学场景">
          <el-select v-model="createForm.scene_id" placeholder="选择场景" clearable style="width: 100%">
            <el-option v-for="s in scenes" :key="s.id" :label="`${s.name} (${difficultyLabel(s.difficulty)})`" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 加入房间角色选择对话框 -->
    <el-dialog v-model="showJoinDialog" title="选择角色" width="480px">
      <el-form label-width="80px">
        <el-form-item label="房间">
          {{ joiningRoom?.group_name }}
        </el-form-item>
        <el-form-item label="选择角色">
          <el-select v-model="selectedRoleId" placeholder="选择角色" style="width: 100%">
            <el-option
              v-for="r in availableRoles" :key="r.id"
              :label="r.name" :value="r.id"
              :disabled="isRoleTaken(r.code, joiningRoom)"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showJoinDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmJoin">确认加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useCollabStore } from '../stores/collab'
import { useAuthStore } from '../stores/auth'
import { roleAPI } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useSocket } from '../utils/websocket'

const collabStore = useCollabStore()
const authStore = useAuthStore()
const { isConnected } = useSocket()

const isAdmin = computed(() => ['admin', 'teacher'].includes(authStore.user?.role_code))
const isWsConnected = computed(() => isConnected.value)

const filterScene = ref(null)
const showCreateDialog = ref(false)
const showJoinDialog = ref(false)
const createForm = ref({ group_name: '', scene_id: null })
const joiningRoom = ref(null)
const selectedRoleId = ref(null)
const roles = ref([])

const rooms = computed(() => collabStore.rooms)
const scenes = computed(() => collabStore.scenes)

// 移动端检测
const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

function difficultyType(d) {
  return { easy: 'success', normal: '', hard: 'danger' }[d] || ''
}
function difficultyLabel(d) {
  return { easy: '简单', normal: '普通', hard: '困难' }[d] || d
}

function isInRoom(room) {
  return authStore.user && room.members?.some(m => m.id === authStore.user.id)
}

function availableRoles() {
  return roles.value.filter(r => !['admin', 'teacher'].includes(r.code))
}

function isRoleTaken(roleCode, room) {
  return room.members?.some(m => m.role_code === roleCode)
}

async function loadRooms() {
  await collabStore.loadRooms(filterScene.value)
}

async function loadRoles() {
  try {
    const res = await roleAPI.list()
    roles.value = res.data.data || []
  } catch (e) {
    console.error('加载角色失败', e)
  }
}

async function handleCreate() {
  if (!createForm.value.group_name) {
    ElMessage.warning('请输入房间名称')
    return
  }
  const result = await collabStore.createRoom(createForm.value)
  if (result.success) {
    ElMessage.success('房间创建成功')
    showCreateDialog.value = false
    createForm.value = { group_name: '', scene_id: null }
  } else {
    ElMessage.error(result.message)
  }
}

function handleJoin(room) {
  joiningRoom.value = room
  selectedRoleId.value = null
  showJoinDialog.value = true
}

async function confirmJoin() {
  const result = await collabStore.joinRoom(joiningRoom.value.id, selectedRoleId.value)
  if (result.success) {
    ElMessage.success('加入成功')
    showJoinDialog.value = false
    await loadRooms()
  } else {
    ElMessage.error(result.message)
  }
}

async function handleLeave(room) {
  await ElMessageBox.confirm('确定要离开此房间吗？', '提示', { type: 'warning' })
  await collabStore.leaveCurrentRoom()
  ElMessage.success('已离开房间')
  await loadRooms()
}

async function handleClose(room) {
  await ElMessageBox.confirm('确定要关闭此房间吗？关闭后无法恢复。', '警告', { type: 'warning' })
  const result = await collabStore.closeRoom(room.id)
  if (result.success) {
    ElMessage.success('房间已关闭')
  } else {
    ElMessage.error(result.message)
  }
}

onMounted(async () => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  collabStore.initSocket()
  await Promise.all([loadRooms(), collabStore.loadScenes(), loadRoles()])
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
  collabStore.destroySocket()
})
</script>

<style scoped>
.room-hall { padding: 20px; }
.toolbar { display: flex; align-items: center; margin-bottom: 20px; }
.ws-status { margin-left: auto; }
.room-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }
.room-card .card-header { display: flex; justify-content: space-between; align-items: center; }
.room-card .room-name { font-weight: bold; font-size: 16px; }
.info-row { margin-bottom: 8px; }
.info-row .label { color: #909399; margin-right: 8px; }
.member-list { margin-top: 8px; }
.card-footer { margin-top: 12px; text-align: right; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
