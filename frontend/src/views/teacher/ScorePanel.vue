<template>
  <div class="score-panel">
    <el-row :gutter="16" class="score-summary">
      <el-col :xs="12" :sm="6" :md="6">
        <el-statistic title="总分" :value="scoreData.total" />
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-statistic title="操作得分" :value="scoreData.operation_score" />
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-statistic title="完整性" :value="scoreData.completeness_score" suffix="分" />
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-statistic title="效率" :value="scoreData.efficiency_score" suffix="分" />
      </el-col>
    </el-row>

    <el-divider />

    <div class="score-stats">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-item">
            <span class="stat-value">{{ scoreData.member_count }}</span>
            <span class="stat-label">参与成员</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-item">
            <span class="stat-value">{{ scoreData.operation_count }}</span>
            <span class="stat-label">总操作数</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-item">
            <span class="stat-value error">{{ scoreData.error_count }}</span>
            <span class="stat-label">错误次数</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-item">
            <span class="stat-value">{{ scoreData.operation_count ? Math.round((1 - scoreData.error_count / scoreData.operation_count) * 100) : 0 }}%</span>
            <span class="stat-label">正确率</span>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 评分明细 -->
    <el-table :data="scoreData.details" border stripe max-height="300" style="margin-top: 16px">
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column label="模块" width="140">
        <template #default="{ row }">{{ moduleLabel(row.module) }}</template>
      </el-table-column>
      <el-table-column prop="action" label="操作" width="120" />
      <el-table-column label="得分" width="100">
        <template #default="{ row }">
          <span :class="{ 'score-positive': row.points > 0, 'score-negative': row.points < 0 }">
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { scoreAPI } from '../../api'

const props = defineProps({
  groupId: { type: Number, required: true }
})

const scoreData = ref({
  total: 0, operation_score: 0, completeness_score: 0, efficiency_score: 0,
  member_count: 0, operation_count: 0, error_count: 0, details: []
})
const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

function moduleLabel(m) {
  const labels = {
    purchase_request: '采购申请', purchase_order: '采购订单', transport_order: '运输订单',
    inbound_order: '入库管理', outbound_order: '出库管理', stock_count: '库存盘点',
    event_injection: '事件注入'
  }
  return labels[m] || m
}

async function loadScore() {
  if (!props.groupId) return
  try {
    const res = await scoreAPI.getGroupScore(props.groupId)
    scoreData.value = res.data.data
  } catch (e) {
    console.error('加载评分失败', e)
  }
}

onMounted(() => { checkWidth(); window.addEventListener('resize', checkWidth); loadScore() })
onUnmounted(() => { window.removeEventListener('resize', checkWidth) })
watch(() => props.groupId, loadScore)
</script>

<style scoped>
.score-panel { padding: 8px 0; }
.score-summary { margin-bottom: 16px; }
.score-stats .stat-item { text-align: center; }
.stat-value { display: block; font-size: 24px; font-weight: bold; color: #409EFF; }
.stat-value.error { color: #F56C6C; }
.stat-label { font-size: 13px; color: #909399; }
.score-positive { color: #67C23A; font-weight: bold; }
.score-negative { color: #F56C6C; font-weight: bold; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
