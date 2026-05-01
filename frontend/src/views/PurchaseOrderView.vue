<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购订单管理</span>
          <div>
            <el-button type="success" @click="handleExport" style="margin-right: 10px">导出数据</el-button>
            <el-button type="primary" @click="showCreateDialog">新建订单</el-button>
          </div>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column prop="po_no" label="订单号" width="160" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="total_amount" label="总金额" width="110">
          <template #default="{row}">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="expected_date" label="期望到货" width="110" />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{row}">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{row}">{{ row.created_at?.substring(0,19) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button v-if="row.status==='pending'" size="small" type="success" @click="handleConfirm(row)">确认</el-button>
            <el-button v-if="row.status==='confirmed'" size="small" type="warning" @click="handleReceipt(row)">验收</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建订单弹窗 -->
    <el-dialog v-model="dialogVisible" title="新建采购订单" width="600px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="采购申请" required>
          <el-select v-model="form.request_id" placeholder="选择已审批的申请" style="width:100%">
            <el-option v-for="r in approvedRequests" :key="r.id"
              :label="r.req_no + ' - ' + r.goods_name + ' x' + r.quantity"
              :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商" required>
          <el-select v-model="form.supplier_id" placeholder="选择供应商" filterable style="width:100%">
            <el-option v-for="s in supplierList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="期望到货">
          <el-date-picker v-model="form.expected_date" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="商品明细">
          <div v-if="selectedRequest" style="margin-bottom:10px;color:#606266">
            {{ selectedRequest.goods_name }} ({{ selectedRequest.goods_sku }})
            数量: {{ selectedRequest.quantity }}
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">创建</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="采购订单详情" width="650px">
      <template v-if="detail">
        <el-descriptions :column="isMobile ? 1 : 2" border>
          <el-descriptions-item label="订单号">{{ detail.po_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ detail.supplier_name }}</el-descriptions-item>
          <el-descriptions-item label="总金额">¥{{ detail.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detail.status)">{{ statusLabel(detail.status) }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <h4 style="margin:15px 0 10px">订单明细</h4>
        <el-table :data="detail.items" size="small">
          <el-table-column prop="goods_name" label="商品" />
          <el-table-column prop="goods_sku" label="SKU" width="100" />
          <el-table-column prop="ordered_qty" label="订购数量" width="100" />
          <el-table-column prop="unit_price" label="单价" width="100">
            <template #default="{row}">¥{{ row.unit_price }}</template>
          </el-table-column>
          <el-table-column prop="subtotal" label="小计" width="100">
            <template #default="{row}">¥{{ row.subtotal }}</template>
          </el-table-column>
          <el-table-column prop="received_qty" label="已收货" width="80" />
        </el-table>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { purchaseOrderAPI, purchaseRequestAPI, purchaseReceiptAPI, supplierAPI } from '../api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const approvedRequests = ref([])
const supplierList = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const detail = ref(null)
const form = ref({ request_id: null, supplier_id: null, expected_date: '' })
const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const statusType = (s) => ({ pending:'warning', confirmed:'success', shipped:'', partial_received:'warning', completed:'success', cancelled:'info' }[s] || 'info')
const statusLabel = (s) => ({ pending:'待确认', confirmed:'已确认', shipped:'已发货', partial_received:'部分到货', completed:'已完成', cancelled:'已取消' }[s] || s)

const selectedRequest = computed(() => approvedRequests.value.find(r => r.id === form.value.request_id))

const loadData = async () => {
  loading.value = true
  try {
    const res = await purchaseOrderAPI.list()
    if (res.data.code === 200) list.value = res.data.data
  } catch (e) { ElMessage.error('加载失败') }
  loading.value = false
}

const loadOptions = async () => {
  const [r1, r2] = await Promise.all([
    purchaseRequestAPI.list({ status: 'approved' }),
    supplierAPI.list()
  ])
  if (r1.data.code === 200) approvedRequests.value = r1.data.data.filter(r => !r.has_order)
  if (r2.data.code === 200) supplierList.value = r2.data.data
}

const showCreateDialog = () => { form.value = { request_id:null, supplier_id:null, expected_date:'' }; dialogVisible.value = true }

const handleCreate = async () => {
  if (!form.value.request_id || !form.value.supplier_id) return ElMessage.warning('请选择采购申请和供应商')
  const req = selectedRequest.value
  submitting.value = true
  try {
    const res = await purchaseOrderAPI.create({
      request_id: form.value.request_id,
      supplier_id: form.value.supplier_id,
      items: [{ goods_id: req.goods_id, quantity: req.quantity, unit_price: req.est_unit_price || 0 }],
      expected_date: form.value.expected_date || undefined
    })
    if (res.data.code === 200) { ElMessage.success('创建成功'); dialogVisible.value = false; loadData() }
    else ElMessage.error(res.data.message)
  } catch (e) { ElMessage.error('创建失败') }
  submitting.value = false
}

const handleConfirm = async (row) => {
  const res = await purchaseOrderAPI.confirm(row.id)
  if (res.data.code === 200) { ElMessage.success('已确认'); loadData() }
}

const handleReceipt = async (row) => {
  try {
    await ElMessageBox.confirm('确认验收该采购订单？验收通过后将自动生成入库单', '到货验收', { type: 'warning' })
    const res = await purchaseReceiptAPI.create({ po_id: row.id })
    if (res.data.code === 200) {
      ElMessage.success('验收完成')
      if (res.data.data.inbound_order) ElMessage.info(`入库单号: ${res.data.data.inbound_order.order_no}`)
      loadData()
    } else ElMessage.error(res.data.message)
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

const viewDetail = async (row) => {
  const res = await purchaseOrderAPI.get(row.id)
  if (res.data.code === 200) { detail.value = res.data.data; detailVisible.value = true }
}

const handleExport = () => {
  window.open('/api/export/purchase-orders?format=excel', '_blank')
}

onMounted(() => { checkWidth(); window.addEventListener('resize', checkWidth); loadData(); loadOptions() })
onUnmounted(() => { window.removeEventListener('resize', checkWidth) })
</script>

<style scoped>
.card-header { display:flex; justify-content:space-between; align-items:center; }
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
