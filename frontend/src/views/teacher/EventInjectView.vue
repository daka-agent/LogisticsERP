<template>
  <div class="event-panel">
    <div class="toolbar">
      <h3 style="margin: 0">突发事件注入</h3>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：事件注入表单 -->
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span>注入新事件</span></template>
          <el-form :model="form" label-width="80px">
            <el-form-item label="目标小组" required>
              <el-select v-model="form.group_id" placeholder="选择小组" style="width: 100%">
                <el-option v-for="r in rooms" :key="r.id" :label="r.group_name" :value="r.id">
                  <span>{{ r.group_name }}</span>
                  <span style="color: #909399; margin-left: 8px">({{ r.member_count }}人)</span>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="事件类型" required>
              <el-select v-model="form.event_type" placeholder="选择事件类型" style="width: 100%">
                <el-option v-for="et in eventTypes" :key="et.type" :label="et.name" :value="et.type">
                  <div>
                    <strong>{{ et.name }}</strong>
                    <div style="font-size: 12px; color: #909399">{{ et.description }}</div>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="事件描述">
              <el-input v-model="form.description" type="textarea" :rows="3" placeholder="自定义事件描述（可选）" />
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="handleInject" :loading="injecting">
                注入事件
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 可用事件类型参考 -->
        <el-card shadow="hover" style="margin-top: 16px">
          <template #header><span>可用事件类型</span></template>
          <div v-for="et in eventTypes" :key="et.type" class="event-type-item">
            <div class="event-type-name">
              <strong>{{ et.name }}</strong>
              <el-tag size="small" type="info" style="margin-left: 4px">{{ et.type }}</el-tag>
            </div>
            <div class="event-type-desc">{{ et.description }}</div>
            <div class="event-type-roles">
              影响角色：<el-tag v-for="r in et.affected_roles" :key="r" size="small" style="margin: 2px">{{ r }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：已注入事件历史 -->
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header><span>已注入事件</span></template>
          <el-timeline>
            <el-timeline-item
              v-for="(evt, idx) in activeEvents"
              :key="idx"
              type="warning"
              :timestamp="evt.timestamp"
              placement="top"
            >
              <div class="injected-event">
                <div class="event-header">
                  <el-tag type="warning" size="small">{{ evt.event_type }}</el-tag>
                  <span class="injector">由 {{ evt.injected_by }} 注入</span>
                </div>
                <div class="event-body">{{ evt.description }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="activeEvents.length === 0" description="暂无已注入事件" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { roomAPI, eventAPI } from '../../api'
import { useCollabStore } from '../../stores/collab'
import { ElMessage } from 'element-plus'
import { useSocket } from '../../utils/websocket'

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const collabStore = useCollabStore()
const { on } = useSocket()

const rooms = ref([])
const eventTypes = ref([])
const injecting = ref(false)
const form = ref({ group_id: null, event_type: '', description: '' })
const activeEvents = ref([])

async function loadData() {
  const [roomRes, eventRes] = await Promise.all([
    roomAPI.list(),
    eventAPI.getTypes()
  ])
  rooms.value = (roomRes.data.data || []).filter(r => r.status === 'active')
  eventTypes.value = eventRes.data.data || []
}

async function handleInject() {
  if (!form.value.group_id) { ElMessage.warning('请选择目标小组'); return }
  if (!form.value.event_type) { ElMessage.warning('请选择事件类型'); return }

  const selectedEvent = eventTypes.value.find(e => e.type === form.value.event_type)
  const data = {
    group_id: form.value.group_id,
    event_type: form.value.event_type,
    description: form.value.description || selectedEvent?.description || ''
  }

  injecting.value = true
  try {
    await collabStore.injectEvent(data)
    ElMessage.success('事件已成功注入！')
    form.value.description = ''
  } catch (e) {
    ElMessage.error('注入失败')
  } finally {
    injecting.value = false
  }
}

// 监听WebSocket事件
on('event_injected', (data) => {
  activeEvents.value.unshift(data)
  if (activeEvents.value.length > 50) activeEvents.value.pop()
})

onMounted(() => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.event-panel { padding: 20px; }
.toolbar { margin-bottom: 20px; }
.event-type-item { margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0; }
.event-type-item:last-child { border-bottom: none; }
.event-type-name { margin-bottom: 4px; }
.event-type-desc { font-size: 13px; color: #606266; margin-bottom: 4px; }
.event-type-roles { font-size: 12px; color: #909399; }
.injected-event .event-header { display: flex; align-items: center; margin-bottom: 4px; }
.injected-event .injector { margin-left: 8px; font-size: 13px; color: #909399; }
.injected-event .event-body { font-size: 14px; color: #606266; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
