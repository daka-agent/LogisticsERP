<template>
  <div class="receivable-detail" v-loading="loading">
    <el-page-header @back="$router.push('/finance/receivable')" title="返回列表">
      <template #content>
        <span>应收账款详情</span>
      </template>
    </el-page-header>

    <el-card style="margin-top: 16px" v-if="detail">
      <template #header>
        <div class="card-header">
          <span>{{ detail.receivable_no }}</span>
          <el-tag :type="statusTagType(detail.status)" size="large">
            {{ statusLabel(detail.status) }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="应收编号">{{ detail.receivable_no }}</el-descriptions-item>
        <el-descriptions-item label="运输订单">{{ detail.order_no }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ detail.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="制单人">{{ detail.operator_name }}</el-descriptions-item>
        <el-descriptions-item label="应收金额">
          <span style="font-weight: bold; font-size: 16px">{{ formatMoney(detail.total_amount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="收款期限">{{ detail.due_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="已收金额">
          <span style="color: #67C23A; font-weight: bold">{{ formatMoney(detail.received_amount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="剩余应收">
          <span style="color: #E6A23C; font-weight: bold">{{ formatMoney(detail.remaining_amount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detail.updated_at }}</el-descriptions-item>
      </el-descriptions>

      <!-- 收款进度 -->
      <div style="margin-top: 20px">
        <h4>收款进度</h4>
        <el-progress
          :percentage="receivePercent"
          :stroke-width="20"
          :color="receivePercent >= 100 ? '#67C23A' : '#E6A23C'"
          style="max-width: 500px"
        >
          <span>{{ receivePercent }}%</span>
        </el-progress>
      </div>
    </el-card>

    <!-- 收款记录 -->
    <el-card style="margin-top: 16px" v-if="detail">
      <template #header>
        <div class="card-header">
          <span>收款记录</span>
          <el-button
            v-if="detail.status !== 'received' && detail.status !== 'cancelled'"
            type="success" size="small"
            @click="showReceiveDialog = true"
          >
            记录收款
          </el-button>
        </div>
      </template>

      <el-table :data="detail.payments || []" stripe>
        <el-table-column prop="payment_amount" label="收款金额" width="130" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.payment_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="收款方式" width="110">
          <template #default="{ row }">
            {{ methodLabel(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="收款日期" width="120" />
        <el-table-column prop="operator_name" label="操作人" width="100" />
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column prop="created_at" label="记录时间" width="170" />
      </el-table>

      <el-empty v-if="!detail.payments || detail.payments.length === 0" description="暂无收款记录" />
    </el-card>

    <!-- 收款弹窗 -->
    <el-dialog v-model="showReceiveDialog" title="记录收款" width="450px">
      <el-form :model="receiveForm" label-width="80px">
        <el-form-item label="收款金额" required>
          <el-input-number v-model="receiveForm.payment_amount" :min="0.01" :max="Number(detail?.remaining_amount)" :precision="2" style="width: 100%" />
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { financeAPI } from '../../api/finance'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(false)
const detail = ref(null)
const showReceiveDialog = ref(false)
const receiving = ref(false)
const receiveForm = ref({ payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' })

const formatMoney = (val) => '\u00A5' + Number(val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const statusTagType = (s) => ({ pending: 'warning', partial_received: 'info', received: 'success', cancelled: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待收款', partial_received: '部分收款', received: '已收齐', cancelled: '已取消' }[s] || s)
const methodLabel = (m) => ({ bank_transfer: '银行转账', cash: '现金', check: '支票', other: '其他' }[m] || m)

const receivePercent = computed(() => {
  if (!detail.value || detail.value.total_amount === 0) return 0
  return Math.min(100, Math.round(Number(detail.value.received_amount) / Number(detail.value.total_amount) * 100))
})

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await financeAPI.getReceivableDetail(route.params.id)
    if (res.data.code === 200) detail.value = res.data.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const recordReceipt = async () => {
  if (!receiveForm.value.payment_amount || receiveForm.value.payment_amount <= 0) {
    ElMessage.warning('请输入有效的收款金额')
    return
  }
  receiving.value = true
  try {
    const res = await financeAPI.recordReceipt(route.params.id, receiveForm.value)
    if (res.data.code === 200) {
      ElMessage.success('收款记录成功')
      showReceiveDialog.value = false
      receiveForm.value = { payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' }
      loadDetail()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    receiving.value = false
  }
}

onMounted(loadDetail)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
