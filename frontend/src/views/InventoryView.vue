<template>
  <div>
    <div class="page-header">
      <h2>库存管理</h2>
      <el-button type="success" @click="handleExport">导出数据</el-button>
    </div>

    <!-- 库存汇总卡片 -->
    <el-row :gutter="20" class="summary-cards">
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-number">{{ summary.total_skus }}</div>
            <div class="stat-label">商品种类</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-number">{{ summary.total_qty }}</div>
            <div class="stat-label">库存总量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-number">{{ summary.total_locations }}</div>
            <div class="stat-label">占用货位</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-number">{{ alerts.expired.length + alerts.expiring.length }}</div>
            <div class="stat-label">过期预警</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="仓库">
        <el-select v-model="searchForm.warehouse_id" placeholder="全部仓库" clearable>
          <el-option
            v-for="w in warehouses"
            :key="w.id"
            :label="w.name"
            :value="w.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="商品">
        <el-select v-model="searchForm.goods_id" placeholder="全部商品" clearable filterable>
          <el-option
            v-for="g in goods"
            :key="g.id"
            :label="g.name"
            :value="g.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="正常" value="normal" />
          <el-option label="锁定" value="locked" />
          <el-option label="过期" value="expired" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadData">查询</el-button>
      </el-form-item>
    </el-form>

    <!-- 库存表格 -->
    <el-table :data="tableData" border style="width: 100%">
      <el-table-column prop="goods_name" label="商品名称" width="150" />
      <el-table-column prop="goods_sku" label="SKU" width="120" />
      <el-table-column prop="warehouse_name" label="仓库" width="120" />
      <el-table-column prop="loc_code" label="货位" width="100" />
      <el-table-column prop="batch_no" label="批次号" width="120" />
      <el-table-column prop="quantity" label="总数量" width="90" />
      <el-table-column prop="available_qty" label="可用数量" width="90" />
      <el-table-column prop="reserved_qty" label="预留数量" width="90" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'normal' ? 'success' : scope.row.status === 'locked' ? 'warning' : 'danger'">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="production_date" label="生产日期" width="120" />
      <el-table-column prop="expiry_date" label="有效期至" width="120" />
    </el-table>

    <!-- 页签切换：库存记录 / 移动记录 -->
    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <el-tab-pane label="库存记录" name="inventory" />

      <el-tab-pane label="库存移动记录" name="moves">
        <el-table :data="moveData" border style="width: 100%">
          <el-table-column prop="goods_name" label="商品" width="150" />
          <el-table-column prop="move_type" label="类型" width="100">
            <template #default="scope">
              <el-tag :type="getMoveTypeTag(scope.row.move_type)">
                {{ formatMoveType(scope.row.move_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source_loc_code" label="来源货位" width="120" />
          <el-table-column prop="dest_loc_code" label="目标货位" width="120" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="operator_name" label="操作员" width="100" />
          <el-table-column prop="moved_at" label="操作时间" width="180" />
          <el-table-column prop="remark" label="备注" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { inventoryAPI, stockMoveAPI } from '../api'
import { warehouseAPI, goodsAPI } from '../api'

const tableData = ref([])
const moveData = ref([])
const warehouses = ref([])
const goods = ref([])
const activeTab = ref('inventory')

const summary = ref({
  total_skus: 0,
  total_qty: 0,
  total_locations: 0,
  by_warehouse: []
})

const alerts = ref({
  expiring: [],
  expired: [],
  low_stock: []
})

const searchForm = ref({
  warehouse_id: null,
  goods_id: null,
  status: ''
})
const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const loadData = async () => {
  try {
    const res = await inventoryAPI.list(searchForm.value)
    tableData.value = res.data.data
  } catch (err) {
    ElMessage.error('加载库存失败')
  }
}

const loadSummary = async () => {
  try {
    const res = await inventoryAPI.getSummary(searchForm.value)
    summary.value = res.data.data
  } catch (err) {
    console.error('加载汇总失败', err)
  }
}

const loadAlerts = async () => {
  try {
    const res = await inventoryAPI.getAlerts()
    alerts.value = res.data.data
  } catch (err) {
    console.error('加载预警失败', err)
  }
}

const loadMoves = async () => {
  try {
    const res = await stockMoveAPI.list()
    moveData.value = res.data.data
  } catch (err) {
    console.error('加载移动记录失败', err)
  }
}

const loadWarehouses = async () => {
  try {
    const res = await warehouseAPI.list()
    warehouses.value = res.data.data
  } catch (err) {
    console.error('加载仓库失败', err)
  }
}

const loadGoods = async () => {
  try {
    const res = await goodsAPI.list()
    goods.value = res.data.data
  } catch (err) {
    console.error('加载商品失败', err)
  }
}

const formatStatus = (status) => {
  const map = {
    'normal': '正常',
    'locked': '锁定',
    'expired': '过期'
  }
  return map[status] || status
}

const formatMoveType = (type) => {
  const map = {
    'inbound': '入库',
    'outbound': '出库',
    'transfer': '调拨',
    'adjust': '调整'
  }
  return map[type] || type
}

const getMoveTypeTag = (type) => {
  const map = {
    'inbound': 'success',
    'outbound': 'danger',
    'transfer': 'warning',
    'adjust': 'info'
  }
  return map[type] || 'info'
}

watch(activeTab, (val) => {
  if (val === 'moves') {
    loadMoves()
  }
})

const handleExport = () => {
  window.open('/api/export/inventory?format=excel', '_blank')
}

onMounted(() => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  loadData()
  loadSummary()
  loadAlerts()
  loadWarehouses()
  loadGoods()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 10px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.search-form {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .stat-number {
    font-size: 22px;
  }

  .el-form--inline .el-form-item {
    display: block;
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .el-form--inline .el-form-item__content {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>