<template>
  <div class="finance-overview">
    <el-row :gutter="20" class="stat-row">
      <!-- 应付账款统计 -->
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-red">
          <div class="stat-value">{{ formatMoney(overview.payable?.total || 0) }}</div>
          <div class="stat-label">应付总额</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-green">
          <div class="stat-value">{{ formatMoney(overview.payable?.paid || 0) }}</div>
          <div class="stat-label">已付金额</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-orange">
          <div class="stat-value">{{ formatMoney(overview.payable?.remaining || 0) }}</div>
          <div class="stat-label">应付余额</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-blue">
          <div class="stat-value">{{ overview.payable?.pending_count || 0 }}</div>
          <div class="stat-label">待付单据</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stat-row">
      <!-- 应收账款统计 -->
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-blue">
          <div class="stat-value">{{ formatMoney(overview.receivable?.total || 0) }}</div>
          <div class="stat-label">应收总额</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-green">
          <div class="stat-value">{{ formatMoney(overview.receivable?.received || 0) }}</div>
          <div class="stat-label">已收金额</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-orange">
          <div class="stat-value">{{ formatMoney(overview.receivable?.remaining || 0) }}</div>
          <div class="stat-label">应收余额</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-purple">
          <div class="stat-value">{{ overview.receivable?.pending_count || 0 }}</div>
          <div class="stat-label">待收单据</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <span>应付账款状态分布</span>
          </template>
          <div class="status-bar-group">
            <div class="status-bar-item">
              <el-tag type="warning">待付款</el-tag>
              <el-progress :percentage="payablePercent('pending')" :stroke-width="18" color="#E6A23C" />
              <span class="status-count">{{ overview.payable?.pending_count || 0 }} 笔</span>
            </div>
            <div class="status-bar-item">
              <el-tag type="info">部分付款</el-tag>
              <el-progress :percentage="payablePercent('partial')" :stroke-width="18" color="#909399" />
              <span class="status-count">{{ overview.payable?.partial_count || 0 }} 笔</span>
            </div>
            <div class="status-bar-item">
              <el-tag type="success">已付清</el-tag>
              <el-progress :percentage="payablePercent('paid')" :stroke-width="18" color="#67C23A" />
              <span class="status-count">{{ overview.payable?.paid_count || 0 }} 笔</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <span>应收账款状态分布</span>
          </template>
          <div class="status-bar-group">
            <div class="status-bar-item">
              <el-tag type="warning">待收款</el-tag>
              <el-progress :percentage="receivablePercent('pending')" :stroke-width="18" color="#E6A23C" />
              <span class="status-count">{{ overview.receivable?.pending_count || 0 }} 笔</span>
            </div>
            <div class="status-bar-item">
              <el-tag type="info">部分收款</el-tag>
              <el-progress :percentage="receivablePercent('partial')" :stroke-width="18" color="#909399" />
              <span class="status-count">{{ overview.receivable?.partial_count || 0 }} 笔</span>
            </div>
            <div class="status-bar-item">
              <el-tag type="success">已收齐</el-tag>
              <el-progress :percentage="receivablePercent('received')" :stroke-width="18" color="#67C23A" />
              <span class="status-count">{{ overview.receivable?.received_count || 0 }} 笔</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <el-button type="primary" @click="$router.push('/finance/payable')">
            管理应付账款
          </el-button>
          <el-button type="success" @click="$router.push('/finance/receivable')">
            管理应收账款
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { financeAPI } from '../../api/finance'

const overview = ref({
  payable: { total: 0, paid: 0, remaining: 0, pending_count: 0, partial_count: 0, paid_count: 0 },
  receivable: { total: 0, received: 0, remaining: 0, pending_count: 0, partial_count: 0, received_count: 0 }
})

const formatMoney = (val) => {
  return '\u00A5' + Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const payableTotalCount = computed(() => {
  const p = overview.value.payable
  return (p.pending_count || 0) + (p.partial_count || 0) + (p.paid_count || 0)
})

const receivableTotalCount = computed(() => {
  const r = overview.value.receivable
  return (r.pending_count || 0) + (r.partial_count || 0) + (r.received_count || 0)
})

const payablePercent = (type) => {
  const total = payableTotalCount.value
  if (total === 0) return 0
  const p = overview.value.payable
  if (type === 'pending') return Math.round((p.pending_count || 0) / total * 100)
  if (type === 'partial') return Math.round((p.partial_count || 0) / total * 100)
  if (type === 'paid') return Math.round((p.paid_count || 0) / total * 100)
  return 0
}

const receivablePercent = (type) => {
  const total = receivableTotalCount.value
  if (total === 0) return 0
  const r = overview.value.receivable
  if (type === 'pending') return Math.round((r.pending_count || 0) / total * 100)
  if (type === 'partial') return Math.round((r.partial_count || 0) / total * 100)
  if (type === 'received') return Math.round((r.received_count || 0) / total * 100)
  return 0
}

const loadOverview = async () => {
  try {
    const res = await financeAPI.getOverview()
    if (res.data.code === 200) {
      overview.value = res.data.data
    }
  } catch (e) {
    console.error('加载财务概览失败', e)
  }
}

onMounted(loadOverview)
</script>

<style scoped>
.finance-overview {
  padding: 0;
}

.stat-row {
  margin-bottom: 0;
}

.stat-card {
  text-align: center;
  margin-bottom: 20px;
}

.stat-card :deep(.el-card__body) {
  padding: 20px 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-red .stat-value { color: #F56C6C; }
.stat-green .stat-value { color: #67C23A; }
.stat-orange .stat-value { color: #E6A23C; }
.stat-blue .stat-value { color: #409EFF; }
.stat-purple .stat-value { color: #9B59B6; }

.status-bar-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-bar-item .el-tag {
  min-width: 72px;
  text-align: center;
}

.status-bar-item .el-progress {
  flex: 1;
}

.status-count {
  min-width: 50px;
  text-align: right;
  font-size: 13px;
  color: #606266;
}

@media (max-width: 768px) {
  .stat-value {
    font-size: 18px;
  }

  .status-bar-item {
    flex-wrap: wrap;
  }

  .status-bar-item .el-progress {
    width: 100%;
    order: 3;
  }
}
</style>
