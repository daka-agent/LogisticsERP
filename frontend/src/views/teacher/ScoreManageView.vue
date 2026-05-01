<template>
  <div class="score-manage">
    <div class="toolbar">
      <h3 style="margin: 0">成绩统计</h3>
      <el-select v-model="selectedGroupId" placeholder="选择小组" clearable style="width: 200px; margin-left: 12px" @change="loadData">
        <el-option v-for="r in rooms" :key="r.id" :label="r.group_name" :value="r.id" />
      </el-select>
      <el-button type="primary" style="margin-left: 12px" @click="exportCSV">
        <el-icon><Download /></el-icon>导出CSV
      </el-button>
    </div>

    <el-tabs v-model="activeTab">
      <!-- 小组排行 -->
      <el-tab-pane label="小组排行" name="group">
        <el-table :data="groupRanking" border stripe>
          <el-table-column label="排名" width="80">
            <template #default="{ $index }">
              <el-tag :type="$index === 0 ? 'danger' : $index === 1 ? 'warning' : $index === 2 ? '' : 'info'" round>
                {{ $index + 1 }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="group_name" label="小组" />
          <el-table-column prop="total_score" label="总分" width="120">
            <template #default="{ row }">
              <strong>{{ row.total_score }}</strong>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 个人排行 -->
      <el-tab-pane label="个人排行" name="user">
        <el-table :data="userRanking" border stripe>
          <el-table-column label="排名" width="80">
            <template #default="{ $index }">
              <el-tag :type="$index === 0 ? 'danger' : $index === 1 ? 'warning' : $index === 2 ? '' : 'info'" round>
                {{ $index + 1 }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="real_name" label="姓名" />
          <el-table-column prop="role_name" label="角色" width="120">
            <template #default="{ row }">
              <el-tag size="small">{{ row.role_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_score" label="总分" width="120">
            <template #default="{ row }">
              <strong>{{ row.total_score }}</strong>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 评分明细 -->
      <el-tab-pane label="评分明细" name="details">
        <el-table :data="scoreDetails" border stripe max-height="500">
          <el-table-column prop="created_at" label="时间" width="180" />
          <el-table-column prop="user_name" label="用户" width="120" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column label="模块" width="140">
            <template #default="{ row }">{{ moduleLabel(row.module) }}</template>
          </el-table-column>
          <el-table-column prop="action" label="操作" width="120" />
          <el-table-column label="得分" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.points > 0 ? '#67C23A' : row.points < 0 ? '#F56C6C' : '#909399', fontWeight: 'bold' }">
                {{ row.points > 0 ? '+' : '' }}{{ row.points }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="正确" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_correct ? 'success' : 'danger'" size="small">
                {{ row.is_correct ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 16px; text-align: center">
          <el-pagination
            v-model:current-page="page"
            :page-size="per_page"
            :total="total"
            layout="prev, pager, next"
            @current-change="loadScoreDetails"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { scoreAPI, roomAPI } from '../../api'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const rooms = ref([])
const selectedGroupId = ref(null)
const activeTab = ref('group')
const groupRanking = ref([])
const userRanking = ref([])
const scoreDetails = ref([])
const page = ref(1)
const per_page = 20
const total = ref(0)

function moduleLabel(m) {
  const labels = {
    purchase_request: '采购申请', purchase_order: '采购订单', transport_order: '运输订单',
    inbound_order: '入库管理', outbound_order: '出库管理', stock_count: '库存盘点',
    event_injection: '事件注入'
  }
  return labels[m] || m
}

async function loadData() {
  const params = selectedGroupId.value ? { group_id: selectedGroupId.value } : {}
  const [grRes, urRes] = await Promise.all([
    scoreAPI.getGroupRanking(),
    scoreAPI.getRanking(params)
  ])
  groupRanking.value = grRes.data.data || []
  userRanking.value = urRes.data.data || []
  loadScoreDetails()
}

async function loadScoreDetails() {
  const params = { page: page.value, per_page }
  if (selectedGroupId.value) params.group_id = selectedGroupId.value
  const res = await scoreAPI.getAll(params)
  scoreDetails.value = res.data.data.items || []
  total.value = res.data.data.total || 0
}

function exportCSV() {
  if (!scoreDetails.value.length) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  const headers = ['时间', '用户', '用户名', '模块', '操作', '得分', '正确']
  const rows = scoreDetails.value.map(r => [
    r.created_at, r.user_name, r.username, moduleLabel(r.module), r.action, r.points, r.is_correct ? '是' : '否'
  ])
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
  const bom = '\uFEFF'
  const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `成绩统计_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  ElMessage.success('导出成功')
}

onMounted(async () => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  const roomRes = await roomAPI.list()
  rooms.value = roomRes.data.data || []
  await loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.score-manage { padding: 20px; }
.toolbar { display: flex; align-items: center; margin-bottom: 20px; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
