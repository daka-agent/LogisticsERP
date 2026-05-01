<template>
  <div class="progress-monitor">
    <div class="toolbar">
      <h3 style="margin: 0">小组进度监控</h3>
      <el-tag :type="isWsConnected ? 'success' : 'danger'">
        {{ isWsConnected ? '实时连接' : '未连接' }}
      </el-tag>
    </div>

    <!-- 小组概览卡片 -->
    <div class="group-cards">
      <el-card v-for="room in rooms" :key="room.id" class="group-card" shadow="hover" @click="selectRoom(room)">
        <div class="group-header">
          <span class="group-name">{{ room.group_name }}</span>
          <el-tag :type="room.status === 'active' ? 'success' : 'info'" size="small">
            {{ room.status === 'active' ? '进行中' : '已结束' }}
          </el-tag>
        </div>
        <div class="group-info">
          <div v-if="room.scene" class="scene-info">场景：{{ room.scene.name }}</div>
          <div>成员：{{ room.member_count }} 人</div>
        </div>
      </el-card>
      <el-empty v-if="rooms.length === 0" description="暂无活跃小组" />
    </div>

    <!-- 选中小组的详细进度 -->
    <div v-if="selectedRoom" class="detail-panel">
      <el-divider>{{ selectedRoom.group_name }} - 详细进度</el-divider>

      <el-tabs v-model="activeTab">
        <!-- 成员操作统计 -->
        <el-tab-pane label="成员操作" name="members">
          <el-table :data="progressData.member_stats" border>
            <el-table-column prop="real_name" label="成员" width="120" />
            <el-table-column prop="operation_count" label="操作次数" width="120" />
            <el-table-column label="占比">
              <template #default="{ row }">
                <el-progress
                  :percentage="progressData.total_operations ? Math.round(row.operation_count / progressData.total_operations * 100) : 0"
                  :stroke-width="16"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 模块进度 -->
        <el-tab-pane label="模块进度" name="modules">
          <el-row :gutter="16">
            <el-col :span="8" v-for="(stat, module) in progressData.module_stats" :key="module">
              <el-card shadow="hover" class="module-card">
                <div class="module-name">{{ moduleLabel(module) }}</div>
                <div class="module-stats">
                  <span>操作 <strong>{{ stat.total }}</strong> 次</span>
                  <span style="margin-left: 12px">正确 <strong>{{ stat.correct }}</strong> 次</span>
                </div>
                <el-progress
                  :percentage="stat.total ? Math.round(stat.correct / stat.total * 100) : 0"
                  :stroke-width="12"
                  :color="stat.total && stat.correct / stat.total > 0.8 ? '#67C23A' : '#E6A23C'"
                />
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 实时操作日志 -->
        <el-tab-pane label="实时操作" name="operations">
          <el-timeline>
            <el-timeline-item
              v-for="(op, idx) in progressData.recent_operations"
              :key="idx"
              :type="op.is_correct ? 'primary' : 'danger'"
              :timestamp="op.created_at"
              placement="top"
            >
              <div class="op-item">
                <span class="op-user">{{ op.user_name || '未知' }}</span>
                <el-tag size="small" style="margin: 0 4px">{{ moduleLabel(op.module) }}</el-tag>
                <span class="op-action">{{ op.action }}</span>
                <span class="op-desc" v-if="op.description"> - {{ op.description }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="!progressData.recent_operations?.length" description="暂无操作记录" />
        </el-tab-pane>

        <!-- 小组评分 -->
        <el-tab-pane label="评分" name="scores">
          <ScorePanel :group-id="selectedRoom.id" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useCollabStore } from '../../stores/collab'
import { roomAPI } from '../../api'
import { useSocket } from '../../utils/websocket'
import ScorePanel from './ScorePanel.vue'

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const collabStore = useCollabStore()
const { isConnected } = useSocket()
const isWsConnected = computed(() => isConnected.value)

const rooms = ref([])
const selectedRoom = ref(null)
const progressData = ref({ member_stats: [], module_stats: {}, recent_operations: [], total_operations: 0 })
const activeTab = ref('members')

function moduleLabel(m) {
  const labels = {
    purchase_request: '采购申请', purchase_order: '采购订单', transport_order: '运输订单',
    inbound_order: '入库管理', outbound_order: '出库管理', stock_count: '库存盘点',
    event_injection: '事件注入'
  }
  return labels[m] || m
}

async function loadRooms() {
  const res = await roomAPI.list()
  rooms.value = (res.data.data || []).filter(r => r.status === 'active')
}

async function selectRoom(room) {
  selectedRoom.value = room
  await loadProgress(room.id)
}

async function loadProgress(roomId) {
  try {
    const res = await roomAPI.getProgress(roomId)
    progressData.value = res.data.data
  } catch (e) {
    console.error('加载进度失败', e)
  }
}

// 定时刷新进度
let timer = null
onMounted(async () => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  collabStore.initSocket()
  await loadRooms()
  timer = setInterval(() => {
    if (selectedRoom.value) {
      loadProgress(selectedRoom.value.id)
    }
  }, 5000)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.progress-monitor { padding: 20px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.group-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px; }
.group-card { cursor: pointer; }
.group-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.group-name { font-weight: bold; font-size: 16px; }
.group-info { color: #909399; font-size: 14px; }
.detail-panel { margin-top: 20px; }
.module-card { margin-bottom: 12px; text-align: center; }
.module-name { font-weight: bold; margin-bottom: 8px; font-size: 14px; }
.module-stats { font-size: 13px; margin-bottom: 8px; color: #606266; }
.op-item { font-size: 14px; }
.op-user { font-weight: bold; color: #409EFF; }
.op-action { color: #606266; }
.op-desc { color: #909399; font-size: 13px; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
