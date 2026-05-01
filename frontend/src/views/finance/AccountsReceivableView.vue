<template>
  <div class="accounts-receivable">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>应收账款管理</span>
          <el-button type="primary" @click="showCreateDialog = true">生成应收账款</el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable @change="loadList">
            <el-option label="待收款" value="pending" />
            <el-option label="部分收款" value="partial_received" />
            <el-option label="已收齐" value="received" />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="receivable_no" label="应收编号" width="160" />
        <el-table-column prop="order_no" label="运输订单" width="160" />
        <el-table-column prop="customer_name" label="客户" min-width="120" />
        <el-table-column prop="total_amount" label="应收金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="received_amount" label="已收金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.received_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="remaining_amount" label="剩余应收" width="120" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.remaining_amount > 0 }">
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
        <el-table-column prop="due_date" label="收款期限" width="110" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="$router.push(`/finance/receivable/${row.id}`)">
              详情
            </el-button>
            <el-button
              v-if="row.status !== 'received' && row.status !== 'cancelled'"
              type="success" link size="small"
              @click="openReceiveDialog(row)"
            >
              收款
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 生成应收账款弹窗 -->
    <el-dialog v-model="showCreateDialog" title="生成应收账款" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="运输订单" required>
          <el-select
            v-model="createForm.order_id"
            placeholder="选择已完成的运输订单"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="order in completedOrders"
              :key="order.id"
              :label="`${order.order_no} - ${order.customer_name} (¥${order.freight_amount || 0})`"
              :value="order.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="收款期限">
          <el-date-picker v-model="createForm.due_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createReceivable" :loading="creating">生成</el-button>
      </template>
    </el-dialog>

    <!-- 收款弹窗 -->
    <el-dialog v-model="showReceiveDialog" title="记录收款" width="450px">
      <el-descriptions :column="1" border size="small" style="margin-bottom: 16px">
        <el-descriptions-item label="应收编号">{{ currentRow?.receivable_no }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ currentRow?.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="剩余应收">
          <span style="color: #E6A23C; font-weight: bold">{{ formatMoney(currentRow?.remaining_amount) }}</span>
        </el-descriptions-item>
      </el-descriptions>
      <el-form :model="receiveForm" label-width="80px">
        <el-form-item label="收款金额" required>
          <el-input-number v-model="receiveForm.payment_amount" :min="0.01" :max="Number(currentRow?.remaining_amount)" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="收款方式">
          <el-select v-model="receiveForm.payment_method" style="width: 100%">
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="现金" value="cash" />
            <el-option label="支票" value="check" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="收款日期">
          <el-date-picker v-model="receiveForm.payment_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="receiveForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReceiveDialog = false">取消</el-button>
        <el-button type="primary" @click="recordReceipt" :loading="receiving">确认收款</el-button>
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
const completedOrders = ref([])
const createForm = ref({ order_id: null, due_date: '' })

// 收款弹窗
const showReceiveDialog = ref(false)
const receiving = ref(false)
const currentRow = ref(null)
const receiveForm = ref({ payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' })

const formatMoney = (val) => '\u00A5' + Number(val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const statusTagType = (s) => ({ pending: 'warning', partial_received: 'info', received: 'success', cancelled: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待收款', partial_received: '部分收款', received: '已收齐', cancelled: '已取消' }[s] || s)

const loadList = async () => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const res = await financeAPI.getReceivableList(params)
    if (res.data.code === 200) list.value = res.data.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadCompletedOrders = async () => {
  try {
    const res = await axios.get('/orders?status=completed')
    if (res.data.code === 200) {
      // 过滤掉没有运费的订单
      completedOrders.value = res.data.data.filter(o => o.freight_amount && o.freight_amount > 0)
    }
  } catch (e) {
    console.error(e)
  }
}

const createReceivable = async () => {
  if (!createForm.value.order_id) {
    ElMessage.warning('请选择运输订单')
    return
  }
  creating.value = true
  try {
    const res = await financeAPI.createReceivable(createForm.value)
    if (res.data.code === 200) {
      ElMessage.success('应收账款生成成功')
      showCreateDialog.value = false
      createForm.value = { order_id: null, due_date: '' }
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

const openReceiveDialog = (row) => {
  currentRow.value = row
  receiveForm.value = { payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' }
  showReceiveDialog.value = true
}

const recordReceipt = async () => {
  if (!receiveForm.value.payment_amount || receiveForm.value.payment_amount <= 0) {
    ElMessage.warning('请输入有效的收款金额')
    return
  }
  receiving.value = true
  try {
    const res = await financeAPI.recordReceipt(currentRow.value.id, receiveForm.value)
    if (res.data.code === 200) {
      ElMessage.success('收款记录成功')
      showReceiveDialog.value = false
      loadList()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    receiving.value = false
  }
}

onMounted(() => {
  loadList()
  loadCompletedOrders()
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

.text-warning {
  color: #E6A23C;
  font-weight: bold;
}
</style>
