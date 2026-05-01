<template>
  <div>
    <div class="page-header">
      <h2>库存盘点</h2>
      <el-button type="primary" @click="showCreateDialog = true">新建盘点单</el-button>
    </div>

    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="草稿" value="draft" />
          <el-option label="盘点中" value="counting" />
          <el-option label="已完成" value="completed" />
        </el-select>
      </el-form-item>
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
      <el-form-item>
        <el-button type="primary" @click="loadData">查询</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格 -->
    <el-table :data="tableData" border style="width: 100%">
      <el-table-column prop="count_no" label="盘点单号" width="200" />
      <el-table-column prop="warehouse_name" label="仓库" width="120" />
      <el-table-column prop="count_type" label="盘点类型" width="100">
        <template #default="scope">
          {{ formatCountType(scope.row.count_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="operator_name" label="操作员" width="100" />
      <el-table-column prop="counted_at" label="盘点时间" width="180" />
      <el-table-column prop="completed_at" label="完成时间" width="180" />
      <el-table-column prop="remark" label="备注" />
      <el-table-column label="操作" width="280">
        <template #default="scope">
          <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
          <el-button
            v-if="scope.row.status === 'draft'"
            size="small"
            type="warning"
            @click="handleCount(scope.row)"
          >
            执行盘点
          </el-button>
          <el-button
            v-if="scope.row.status === 'counting'"
            size="small"
            type="success"
            @click="handleReconcile(scope.row)"
          >
            调整库存
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建盘点单" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="仓库" required>
          <el-select v-model="createForm.warehouse_id" placeholder="请选择仓库">
            <el-option
              v-for="w in warehouses"
              :key="w.id"
              :label="w.name"
              :value="w.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="盘点类型" required>
          <el-select v-model="createForm.count_type" placeholder="请选择盘点类型">
            <el-option label="全盘" value="full" />
            <el-option label="部分盘点" value="partial" />
            <el-option label="循环盘点" value="cycle" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remark" type="textarea" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- 盘点对话框 -->
    <el-dialog v-model="showCountDialog" title="执行盘点" width="700px">
      <el-alert
        title="请输入每个商品的实际盘点数量"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 15px"
      />

      <el-table :data="countForm.items" border>
        <el-table-column prop="goods_name" label="商品" width="120" />
        <el-table-column prop="loc_code" label="货位" width="100" />
        <el-table-column prop="batch_no" label="批次号" width="100" />
        <el-table-column prop="book_qty" label="账面数量" width="100" />
        <el-table-column label="实盘数量" width="120">
          <template #default="scope">
            <el-input-number
              v-model="scope.row.actual_qty"
              :min="0"
              size="small"
            />
          </template>
        </el-table-column>
        <el-table-column label="差异" width="100">
          <template #default="scope">
            <span :class="scope.row.actual_qty - scope.row.book_qty > 0 ? 'positive' : scope.row.actual_qty - scope.row.book_qty < 0 ? 'negative' : ''">
              {{ scope.row.actual_qty - scope.row.book_qty }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="showCountDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCountSubmit">提交盘点</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="盘点详情" width="700px">
      <el-descriptions :column="isMobile ? 1 : 2" border>
        <el-descriptions-item label="盘点单号">{{ detailData.count_no }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ detailData.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="盘点类型">{{ formatCountType(detailData.count_type) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(detailData.status)">{{ formatStatus(detailData.status) }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-table :data="detailData.items" border style="margin-top: 15px">
        <el-table-column prop="goods_name" label="商品" width="120" />
        <el-table-column prop="loc_code" label="货位" width="100" />
        <el-table-column prop="book_qty" label="账面数量" width="100" />
        <el-table-column prop="actual_qty" label="实盘数量" width="100" />
        <el-table-column prop="variance" label="差异" width="80">
          <template #default="scope">
            <span :class="scope.row.variance > 0 ? 'positive' : scope.row.variance < 0 ? 'negative' : ''">
              {{ scope.row.variance > 0 ? '+' : '' }}{{ scope.row.variance }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'reconciled' ? 'success' : 'info'" size="small">
              {{ scope.row.status === 'reconciled' ? '已调整' : scope.row.status === 'counted' ? '已盘点' : '待盘点' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { stockCountAPI } from '../api'
import { warehouseAPI } from '../api'

const tableData = ref([])
const warehouses = ref([])
const showCreateDialog = ref(false)
const showCountDialog = ref(false)
const showDetailDialog = ref(false)
const detailData = ref({})

const searchForm = ref({
  status: '',
  warehouse_id: null
})
const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const createForm = ref({
  warehouse_id: null,
  count_type: 'full',
  remark: ''
})

const countForm = ref({
  orderId: null,
  items: []
})

const loadData = async () => {
  try {
    const res = await stockCountAPI.list(searchForm.value)
    tableData.value = res.data.data
  } catch (err) {
    ElMessage.error('加载失败')
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

const handleCreate = async () => {
  if (!createForm.value.warehouse_id) {
    ElMessage.warning('请选择仓库')
    return
  }

  try {
    const res = await stockCountAPI.create(createForm.value)
    ElMessage.success('盘点单创建成功')
    showCreateDialog.value = false

    // 创建成功后直接进入盘点
    const newCount = res.data.data
    if (newCount.items && newCount.items.length > 0) {
      countForm.value.orderId = newCount.id
      countForm.value.items = newCount.items.map(item => ({
        id: item.id,
        goods_name: item.goods_name,
        loc_code: item.loc_code,
        batch_no: item.batch_no,
        book_qty: item.book_qty,
        actual_qty: item.book_qty
      }))
      showCountDialog.value = true
    } else {
      ElMessage.info('该仓库暂无库存记录，无需盘点')
    }

    createForm.value = { warehouse_id: null, count_type: 'full', remark: '' }
    loadData()
  } catch (err) {
    ElMessage.error('创建失败')
  }
}

const handleCount = async (row) => {
  try {
    const res = await stockCountAPI.get(row.id)
    const detail = res.data.data

    countForm.value.orderId = row.id
    countForm.value.items = detail.items.map(item => ({
      id: item.id,
      goods_name: item.goods_name,
      loc_code: item.loc_code,
      batch_no: item.batch_no,
      book_qty: item.book_qty,
      actual_qty: item.book_qty
    }))

    showCountDialog.value = true
  } catch (err) {
    ElMessage.error('加载数据失败')
  }
}

const handleCountSubmit = async () => {
  try {
    await stockCountAPI.count(countForm.value.orderId, { items: countForm.value.items })
    ElMessage.success('盘点提交成功')
    showCountDialog.value = false
    loadData()
  } catch (err) {
    ElMessage.error('盘点提交失败')
  }
}

const handleReconcile = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确认根据盘点结果调整库存？此操作不可撤销！',
      '确认调整',
      {
        confirmButtonText: '确定调整',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await stockCountAPI.reconcile(row.id)
    ElMessage.success('库存调整完成')
    loadData()
  } catch {
    // 用户取消
  }
}

const viewDetail = async (row) => {
  try {
    const res = await stockCountAPI.get(row.id)
    detailData.value = res.data.data
    showDetailDialog.value = true
  } catch (err) {
    ElMessage.error('加载详情失败')
  }
}

const formatStatus = (status) => {
  const map = {
    'draft': '草稿',
    'counting': '盘点中',
    'reconciled': '已调整',
    'completed': '已完成'
  }
  return map[status] || status
}

const formatCountType = (type) => {
  const map = {
    'full': '全盘',
    'partial': '部分盘点',
    'cycle': '循环盘点'
  }
  return map[type] || type
}

const getStatusType = (status) => {
  const map = {
    'draft': 'info',
    'counting': 'warning',
    'reconciled': 'warning',
    'completed': 'success'
  }
  return map[status] || 'info'
}

onMounted(() => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  loadData()
  loadWarehouses()
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

.search-form {
  margin-bottom: 20px;
}

.positive {
  color: #67C23A;
  font-weight: bold;
}

.negative {
  color: #F56C6C;
  font-weight: bold;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>