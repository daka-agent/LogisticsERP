<template>
  <div>
    <div class="page-header">
      <h2>入库管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">新建入库单</el-button>
    </div>

    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="待处理" value="pending" />
          <el-option label="检验中" value="inspecting" />
          <el-option label="上架中" value="shelving" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadData">查询</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格 -->
    <el-table :data="tableData" border style="width: 100%">
      <el-table-column prop="order_no" label="入库单号" width="180" />
      <el-table-column prop="warehouse_name" label="仓库" width="120" />
      <el-table-column prop="source_type" label="来源类型" width="100">
        <template #default="scope">
          {{ formatSourceType(scope.row.source_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_items" label="商品种类" width="90" />
      <el-table-column prop="operator_name" label="操作员" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
          <el-button
            v-if="scope.row.status === 'pending' || scope.row.status === 'inspecting'"
            size="small"
            type="success"
            @click="handleShelve(scope.row)"
          >
            上架
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建入库单" width="600px">
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
        <el-form-item label="来源类型" required>
          <el-select v-model="createForm.source_type" placeholder="请选择来源类型">
            <el-option label="采购入库" value="purchase" />
            <el-option label="退货入库" value="return" />
            <el-option label="调拨入库" value="transfer" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源单号">
          <el-input v-model="createForm.source_id" placeholder="可选" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remark" type="textarea" />
        </el-form-item>

        <el-divider>入库明细</el-divider>

        <div v-for="(item, index) in createForm.items" :key="index" class="item-row">
          <el-form-item :label="'商品' + (index + 1)" required>
            <el-select v-model="item.goods_id" placeholder="选择商品" style="width: 200px">
              <el-option
                v-for="g in goods"
                :key="g.id"
                :label="g.name"
                :value="g.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="计划数量" required>
            <el-input-number v-model="item.planned_qty" :min="1" />
          </el-form-item>
          <el-form-item label="批次号">
            <el-input v-model="item.batch_no" />
          </el-form-item>
          <el-button type="danger" size="small" @click="removeItem(index)">删除</el-button>
        </div>
        <el-button type="primary" link @click="addItem">添加商品</el-button>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上架对话框 -->
    <el-dialog v-model="showShelveDialog" title="入库上架" width="600px">
      <el-form :model="shelveForm" label-width="100px">
        <div v-for="(item, index) in shelveForm.items" :key="index" class="item-row">
          <p><strong>商品：</strong>{{ item.goods_name }} (计划数量：{{ item.planned_qty }})</p>
          <el-form-item label="实际数量">
            <el-input-number v-model="item.actual_qty" :min="0" :max="item.planned_qty" />
          </el-form-item>
          <el-form-item label="货位" required>
            <el-select v-model="item.location_id" placeholder="选择货位">
              <el-option
                v-for="loc in locations"
                :key="loc.id"
                :label="loc.loc_code"
                :value="loc.id"
              />
            </el-select>
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showShelveDialog = false">取消</el-button>
        <el-button type="primary" @click="handleShelveSubmit">确定上架</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { inboundAPI } from '../api'
import { warehouseAPI } from '../api'
import { goodsAPI } from '../api'

const tableData = ref([])
const warehouses = ref([])
const goods = ref([])
const locations = ref([])
const showCreateDialog = ref(false)
const showShelveDialog = ref(false)

const searchForm = ref({
  status: ''
})

const createForm = ref({
  warehouse_id: null,
  source_type: 'purchase',
  source_id: '',
  remark: '',
  items: []
})

const shelveForm = ref({
  orderId: null,
  items: []
})

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const loadData = async () => {
  try {
    const res = await inboundAPI.list(searchForm.value)
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

const loadGoods = async () => {
  try {
    const res = await goodsAPI.list()
    goods.value = res.data.data
  } catch (err) {
    console.error('加载商品失败', err)
  }
}

const loadLocations = async (warehouseId) => {
  try {
    // 获取仓库下的所有库区，再获取所有货位
    const zonesRes = await warehouseAPI.getZones(warehouseId)
    const zones = zonesRes.data.data

    locations.value = []
    for (const zone of zones) {
      const locRes = await warehouseAPI.getLocations(zone.id)
      locations.value = locations.value.concat(locRes.data.data)
    }
  } catch (err) {
    console.error('加载货位失败', err)
  }
}

const addItem = () => {
  createForm.value.items.push({
    goods_id: null,
    planned_qty: 1,
    batch_no: ''
  })
}

const removeItem = (index) => {
  createForm.value.items.splice(index, 1)
}

const handleCreate = async () => {
  if (!createForm.value.warehouse_id || !createForm.value.source_type) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (createForm.value.items.length === 0) {
    ElMessage.warning('请至少添加一个商品')
    return
  }

  try {
    await inboundAPI.create(createForm.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    createForm.value = {
      warehouse_id: null,
      source_type: 'purchase',
      source_id: '',
      remark: '',
      items: []
    }
    loadData()
  } catch (err) {
    ElMessage.error('创建失败')
  }
}

const viewDetail = async (row) => {
  try {
    const res = await inboundAPI.get(row.id)
    const detail = res.data.data
    ElMessage.info(`入库单详情：${detail.order_no}，共 ${detail.items?.length || 0} 个商品`)
  } catch (err) {
    ElMessage.error('加载详情失败')
  }
}

const handleShelve = async (row) => {
  try {
    const res = await inboundAPI.get(row.id)
    const detail = res.data.data

    shelveForm.value.orderId = row.id
    shelveForm.value.items = detail.items.map(item => ({
      id: item.id,
      goods_name: item.goods_name,
      planned_qty: item.planned_qty,
      actual_qty: item.planned_qty,
      location_id: null
    }))

    // 加载货位
    await loadLocations(row.warehouse_id)

    showShelveDialog.value = true
  } catch (err) {
    ElMessage.error('加载数据失败')
  }
}

const handleShelveSubmit = async () => {
  try {
    await inboundAPI.shelve(shelveForm.value.orderId, { items: shelveForm.value.items })
    ElMessage.success('上架完成')
    showShelveDialog.value = false
    loadData()
  } catch (err) {
    ElMessage.error('上架失败')
  }
}

const formatStatus = (status) => {
  const map = {
    'pending': '待处理',
    'inspecting': '检验中',
    'shelving': '上架中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return map[status] || status
}

const formatSourceType = (type) => {
  const map = {
    'purchase': '采购',
    'return': '退货',
    'transfer': '调拨'
  }
  return map[type] || type
}

const getStatusType = (status) => {
  const map = {
    'pending': 'info',
    'inspecting': 'warning',
    'shelving': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return map[status] || 'info'
}

onMounted(() => {
  checkWidth();
  window.addEventListener('resize', checkWidth);
  loadData()
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

.search-form {
  margin-bottom: 20px;
}

.item-row {
  border: 1px solid #e6e6e6;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
