<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购申请管理</span>
          <div>
            <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:140px;margin-right:10px">
              <el-option label="待审批" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已驳回" value="rejected" />
            </el-select>
            <el-button type="primary" @click="showCreateDialog">新建申请</el-button>
          </div>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" style="width:100%">
        <el-table-column prop="req_no" label="申请单号" width="160" />
        <el-table-column prop="goods_name" label="商品名称" />
        <el-table-column prop="goods_sku" label="SKU" width="100" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="est_unit_price" label="期望单价" width="100">
          <template #default="{row}">{{ row.est_unit_price ? '¥' + row.est_unit_price : '-' }}</template>
        </el-table-column>
        <el-table-column prop="est_total_price" label="期望总价" width="110">
          <template #default="{row}">{{ row.est_total_price ? '¥' + row.est_total_price : '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applicant_name" label="申请人" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button v-if="row.status==='pending' && !row.has_order" size="small" type="success" @click="handleApprove(row)">审批</el-button>
            <el-button v-if="row.status==='pending'" size="small" type="danger" @click="handleReject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建申请弹窗 -->
    <el-dialog v-model="dialogVisible" title="新建采购申请" width="500px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="商品" required>
          <el-select v-model="form.goods_id" placeholder="选择商品" filterable style="width:100%">
            <el-option v-for="g in goodsList" :key="g.id" :label="g.name + '(' + g.sku + ')'" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" required>
          <el-input-number v-model="form.quantity" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="期望单价">
          <el-input-number v-model="form.est_unit_price" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="紧急程度">
          <el-radio-group v-model="form.urgency">
            <el-radio value="normal">普通</el-radio>
            <el-radio value="urgent">紧急</el-radio>
            <el-radio value="critical">特急</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="申请原因">
          <el-input v-model="form.reason" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { purchaseRequestAPI, goodsAPI } from '../api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const goodsList = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const filterStatus = ref('')
const form = ref({ goods_id: null, quantity: 100, est_unit_price: null, urgency: 'normal', reason: '' })
const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const statusType = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger', cancelled: 'info' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待审批', approved: '已通过', rejected: '已驳回', cancelled: '已取消' }[s] || s)

const loadData = async () => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const res = await purchaseRequestAPI.list(params)
    if (res.data.code === 200) list.value = res.data.data
  } catch (e) { ElMessage.error('加载失败') }
  loading.value = false
}

const loadGoods = async () => {
  const res = await goodsAPI.list()
  if (res.data.code === 200) goodsList.value = res.data.data
}

watch(filterStatus, loadData)

const showCreateDialog = () => {
  form.value = { goods_id: null, quantity: 100, est_unit_price: null, urgency: 'normal', reason: '' }
  dialogVisible.value = true
}

const handleCreate = async () => {
  if (!form.value.goods_id || !form.value.quantity) return ElMessage.warning('请填写商品和数量')
  submitting.value = true
  try {
    const res = await purchaseRequestAPI.create(form.value)
    if (res.data.code === 200) {
      ElMessage.success('提交成功')
      dialogVisible.value = false
      loadData()
    } else { ElMessage.error(res.data.message) }
  } catch (e) { ElMessage.error('提交失败') }
  submitting.value = false
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.prompt('请输入审批意见', '审批通过', { confirmButtonText: '通过', inputPlaceholder: '同意' })
    const res = await purchaseRequestAPI.approve(row.id, '同意')
    if (res.data.code === 200) { ElMessage.success('审批通过'); loadData() }
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

const handleReject = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回', { confirmButtonText: '驳回', inputPlaceholder: '驳回' })
    const res = await purchaseRequestAPI.reject(row.id, value)
    if (res.data.code === 200) { ElMessage.success('已驳回'); loadData() }
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

onMounted(() => { checkWidth(); window.addEventListener('resize', checkWidth); loadData(); loadGoods() })

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
