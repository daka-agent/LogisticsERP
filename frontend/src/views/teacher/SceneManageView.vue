<template>
  <div class="scene-manage">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>新建场景
      </el-button>
    </div>

    <el-table :data="scenes" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="场景名称" width="180" />
      <el-table-column prop="description" label="描述" min-width="260" show-overflow-tooltip />
      <el-table-column prop="difficulty" label="难度" width="100">
        <template #default="{ row }">
          <el-tag :type="difficultyType(row.difficulty)" size="small">{{ difficultyLabel(row.difficulty) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="突发事件" width="100">
        <template #default="{ row }">
          {{ row.events_config?.length || 0 }} 个
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑场景' : '新建场景'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="场景名称" required>
          <el-input v-model="form.name" placeholder="如：基础流程" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="难度">
          <el-radio-group v-model="form.difficulty">
            <el-radio value="easy">简单</el-radio>
            <el-radio value="normal">普通</el-radio>
            <el-radio value="hard">困难</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 突发事件配置 -->
        <el-divider content-position="left">突发事件配置</el-divider>
        <div v-for="(evt, idx) in form.events_config" :key="idx" class="event-row">
          <el-input v-model="evt.type" placeholder="事件类型" style="width: 140px" />
          <el-input v-model="evt.description" placeholder="事件描述" style="flex: 1; margin-left: 8px" />
          <el-select v-model="evt.trigger" style="width: 120px; margin-left: 8px">
            <el-option label="手动触发" value="manual" />
            <el-option label="自动触发" value="auto" />
          </el-select>
          <el-button type="danger" size="small" circle style="margin-left: 8px" @click="form.events_config.splice(idx, 1)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <el-button size="small" style="margin-top: 8px" @click="form.events_config.push({ type: '', description: '', trigger: 'manual' })">
          添加事件
        </el-button>

        <!-- 评分规则 -->
        <el-divider content-position="left">评分规则</el-divider>
        <el-form-item label="时间限制(分)">
          <el-input-number v-model="form.scoring_rules.time_limit_minutes" :min="10" :max="300" />
        </el-form-item>
        <el-form-item label="满分">
          <el-input-number v-model="form.scoring_rules.full_score" :min="50" :max="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editingId ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { sceneAPI } from '../../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const scenes = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const defaultForm = () => ({
  name: '',
  description: '',
  difficulty: 'normal',
  events_config: [],
  scoring_rules: { time_limit_minutes: 60, full_score: 100 }
})
const form = ref(defaultForm())

function difficultyType(d) { return { easy: 'success', normal: '', hard: 'danger' }[d] || '' }
function difficultyLabel(d) { return { easy: '简单', normal: '普通', hard: '困难' }[d] || d }

async function loadScenes() {
  const res = await sceneAPI.list()
  scenes.value = res.data.data || []
}

function handleCreate() {
  editingId.value = null
  form.value = defaultForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    description: row.description || '',
    difficulty: row.difficulty || 'normal',
    events_config: row.events_config ? JSON.parse(JSON.stringify(row.events_config)) : [],
    scoring_rules: row.scoring_rules || { time_limit_minutes: 60, full_score: 100 }
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name) { ElMessage.warning('请输入场景名称'); return }
  try {
    if (editingId.value) {
      await sceneAPI.update(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await sceneAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadScenes()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除场景"${row.name}"吗？`, '警告', { type: 'warning' })
  try {
    await sceneAPI.delete(row.id)
    ElMessage.success('删除成功')
    await loadScenes()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '删除失败')
  }
}

onMounted(() => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  loadScenes()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.scene-manage { padding: 20px; }
.toolbar { margin-bottom: 16px; }
.event-row { display: flex; align-items: center; margin-bottom: 8px; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
