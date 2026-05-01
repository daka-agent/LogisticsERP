<template>
  <div class="payable-detail" v-loading="loading">
    <el-page-header @back="$router.push('/finance/payable')" title="返回列表">
      <template #content>
        <span>应付账款详情</span>
      </template>
    </el-page-header>

    <el-card style="margin-top: 16px" v-if="detail">
      <template #header>
        <div class="card-header">
          <span>{{ detail.payable_no }}</span>
          <el-tag :type="statusTagType(detail.status)" size="large">
            {{ statusLabel(detail.status) }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="应付编号">{{ detail.payable_no }}</el-descriptions-item>
        <el-descriptions-item label="采购订单">{{ detail.po_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ detail.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="制单人">{{ detail.operator_name }}</el-descriptions-item>
        <el-descriptions-item label="应付金额">
          <span style="font-weight: bold; font-size: 16px">{{ formatMoney(detail.total_amount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="付款期限">{{ detail.due_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="已付金额">
          <span style="color: #67C23A; font-weight: bold">{{ formatMoney(detail.paid_amount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="剩余应付">
          <span style="color: #F56C6C; font-weight: bold">{{ formatMoney(detail.remaining_amount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detail.updated_at }}</el-descriptions-item>
      </el-descriptions>

      <!-- 付款进度 -->
      <div style="margin-top: 20px">
        <h4>付款进度</h4>
        <el-progress
          :percentage="payPercent"
          :stroke-width="20"
          :color="payPercent >= 100 ? '#67C23A' : '#409EFF'"
          style="max-width: 500px"
        >
          <span>{{ payPercent }}%</span>
        </el-progress>
      </div>
    </el-card>

    <!-- 付款记录 -->
    <el-card style="margin-top: 16px" v-if="detail">
      <template #header>
        <div class="card-header">
          <span>付款记录</span>
          <el-button
            v-if="detail.status !== 'paid' && detail.status !== 'cancelled'"
            type="success" size="small"
            @click="showPayDialog = true"
          >
            记录付款
          </el-button>
        </div>
      </template>

      <el-table :data="detail.payments || []" stripe>
        <el-table-column prop="payment_amount" label="付款金额" width="130" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.payment_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="付款方式" width="110">
          <template #default="{ row }">
            {{ methodLabel(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="付款日期" width="120" />
        <el-table-column prop="operator_name" label="操作人" width="100" />
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column prop="created_at" label="记录时间" width="170" />
      </el-table>

      <el-empty v-if="!detail.payments || detail.payments.length === 0" description="暂无付款记录" />
    </el-card>

    <!-- 付款弹窗 -->
    <el-dialog v-model="showPayDialog" title="记录付款" width="450px">
      <el-form :model="payForm" label-width="80px">
        <el-form-item label="付款金额" required>
          <el-input-number v-model="payForm.payment_amount" :min="0.01" :max="Number(detail?.remaining_amount)" :precision="2" style="width: 100%" />
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { financeAPI } from '../../api/finance'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(false)
const detail = ref(null)
const showPayDialog = ref(false)
const paying = ref(false)
const payForm = ref({ payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' })

const formatMoney = (val) => '\u00A5' + Number(val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const statusTagType = (s) => ({ pending: 'warning', partial_paid: 'info', paid: 'success', cancelled: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待付款', partial_paid: '部分付款', paid: '已付清', cancelled: '已取消' }[s] || s)
const methodLabel = (m) => ({ bank_transfer: '银行转账', cash: '现金', check: '支票', other: '其他' }[m] || m)

const payPercent = computed(() => {
  if (!detail.value || detail.value.total_amount === 0) return 0
  return Math.min(100, Math.round(Number(detail.value.paid_amount) / Number(detail.value.total_amount) * 100))
})

const loadDetail = async () => {
  loading.value = true
  try {
    const res = await financeAPI.getPayableDetail(route.params.id)
    if (res.data.code === 200) detail.value = res.data.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const recordPayment = async () => {
  if (!payForm.value.payment_amount || payForm.value.payment_amount <= 0) {
    ElMessage.warning('请输入有效的付款金额')
    return
  }
  paying.value = true
  try {
    const res = await financeAPI.recordPayment(route.params.id, payForm.value)
    if (res.data.code === 200) {
      ElMessage.success('付款记录成功')
      showPayDialog.value = false
      payForm.value = { payment_amount: 0, payment_method: 'bank_transfer', payment_date: '', remark: '' }
      loadDetail()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    paying.value = false
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
