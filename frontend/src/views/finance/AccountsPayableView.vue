<template>
  <div class="accounts-payable">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>应付账款管理</span>
          <el-button type="primary" @click="showCreateDialog = true">生成应付账款</el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable @change="loadList">
            <el-option label="待付款" value="pending" />
            <el-option label="部分付款" value="partial_paid" />
            <el-option label="已付清" value="paid" />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="payable_no" label="应付编号" width="160" />
        <el-table-column prop="po_no" label="采购订单" width="160" />
        <el-table-column prop="supplier_name" label="供应商" min-width="120" />
        <el-table-column prop="total_amount" label="应付金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="已付金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.paid_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="remaining_amount" label="剩余应付" width="120" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.remaining_amount > 0 }">
              {{ formatMoney(row.remaining_amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="付款期限" width="110" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="$router.push(`/finance/payable/${row.id}`)">
              详情
            </el-button>
            <el-button
              v-if="row.status !== 'paid' && row.status !== 'cancelled'"
              type="success" link size="small"
              @click="openPayDialog(row)"
            >
              付款
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 生成应付账款弹窗 -->
    <el-dialog v-model="showCreateDialog" title="生成应付账款" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="采购订单" required>
          <el-select
            v-model="createForm.po_id"
            placeholder="选择已完成的采购订单"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="po in completedPOs"
              :key="po.id"
              :label="`${po.po_no} - ${po.supplier_name} (¥${po.total_amount})`"
              :value="po.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="付款期限">
          <el-date-picker v-model="createForm.due_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createPayable" :loading="creating">生成</el-button>
      </template>
    </el-dialog>

    <!-- 付款弹窗 -->
    <el-dialog v-model="showPayDialog" title="记录付款" width="450px">
      <el-descriptions :column="1" border size="small" style="margin-bottom: 16px">
        <el-descriptions-item label="应付编号">{{ currentRow?.payable_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentRow?.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="剩余应付">
          <span style="color: #F56C6C; font-weight: bold">{{ formatMoney(currentRow?.remaining_amount) }}</span>
        </el-descriptions-item>
      </el-descriptions>
      <el-form :model="payForm" label-width="80px">
        <el-form-item label="付款金额" required>
          <el-input-number v-model="payForm.payment_amount" :min="0.01" :max="Number(currentRow?.remaining_amount)" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="payForm.payment_method" style="width: 100%">
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="现金" value="cash" />
            <el-option label="支票" value="check" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款日期">
          <el-date-picker v-model="payForm.payment_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="payForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPayDialog = false">取消</el-button>
        <el-button type="primary" @click="recordPayment" :loading="paying">确认付款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { financeAPI } from '../../api/finance'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const list = ref([])
const filterStatus = ref('')

// 生成弹窗
const showCreateDialog = ref(false)
const creating = ref(false)
const completedPOs = ref([])
const createForm = ref({ po_id: null, due_date: '' })

// 付款弹窗
const showPayDialog = ref(false)
const paying = ref(false)
const currentRow = ref(null)
const payForm = ref({ payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' })

const formatMoney = (val) => '\u00A5' + Number(val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const statusTagType = (s) => ({ pending: 'warning', partial_paid: 'info', paid: 'success', cancelled: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待付款', partial_paid: '部分付款', paid: '已付清', cancelled: '已取消' }[s] || s)

const loadList = async () => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const res = await financeAPI.getPayableList(params)
    if (res.data.code === 200) list.value = res.data.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadCompletedPOs = async () => {
  try {
    const res = await axios.get('/purchase-orders?status=completed')
    if (res.data.code === 200) completedPOs.value = res.data.data
  } catch (e) {
    console.error(e)
  }
}

const createPayable = async () => {
  if (!createForm.value.po_id) {
    ElMessage.warning('请选择采购订单')
    return
  }
  creating.value = true
  try {
    const res = await financeAPI.createPayable(createForm.value)
    if (res.data.code === 200) {
      ElMessage.success('应付账款生成成功')
      showCreateDialog.value = false
      createForm.value = { po_id: null, due_date: '' }
      loadList()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    creating.value = false
  }
}

const openPayDialog = (row) => {
  currentRow.value = row
  payForm.value = { payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' }
  showPayDialog.value = true
}

const recordPayment = async () => {
  if (!payForm.value.payment_amount || payForm.value.payment_amount <= 0) {
    ElMessage.warning('请输入有效的付款金额')
    return
  }
  paying.value = true
  try {
    const res = await financeAPI.recordPayment(currentRow.value.id, payForm.value)
    if (res.data.code === 200) {
      ElMessage.success('付款记录成功')
      showPayDialog.value = false
      loadList()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    paying.value = false
  }
}

onMounted(() => {
  loadList()
  loadCompletedPOs()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-form {
  margin-bottom: 16px;
}

.text-danger {
  color: #F56C6C;
  font-weight: bold;
}
</style>
