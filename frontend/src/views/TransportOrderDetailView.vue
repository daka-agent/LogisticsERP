<template>
  <div v-loading="loading">
    <el-page-header @back="$router.push('/transport/orders')" title="返回列表" style="margin-bottom:20px" />

    <!-- 步骤条 -->
    <el-card style="margin-bottom:20px">
      <el-steps :active="stepIndex" align-center>
        <el-step title="待审核" />
        <el-step title="已审核" />
        <el-step title="已调度" />
        <el-step title="运输中" />
        <el-step title="已到达" />
        <el-step title="已签收" />
        <el-step title="已完成" />
      </el-steps>
    </el-card>

    <!-- 基本信息 -->
    <el-card style="margin-bottom:20px">
      <template #header><span>订单信息</span></template>
      <el-descriptions :column="isMobile ? 1 : 3" border v-if="order">
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ order.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(order.status)">{{ statusLabel(order.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发货地">{{ order.origin }}</el-descriptions-item>
        <el-descriptions-item label="目的地">{{ order.destination }}</el-descriptions-item>
        <el-descriptions-item label="货物">{{ order.goods_name }}</el-descriptions-item>
        <el-descriptions-item label="重量">{{ order.weight }} kg</el-descriptions-item>
        <el-descriptions-item label="体积">{{ order.volume }} m³</el-descriptions-item>
        <el-descriptions-item label="件数">{{ order.quantity }}</el-descriptions-item>
        <el-descriptions-item label="车牌">{{ order.vehicle_plate || '-' }}</el-descriptions-item>
        <el-descriptions-item label="司机">{{ order.driver_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运费">¥{{ order.freight_amount || '待计算' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 操作按钮 -->
    <el-card style="margin-bottom:20px">
      <template #header><span>操作</span></template>
      <el-button v-if="order && order.status === 'dispatched'" type="primary" @click="addRecord('in_transit')">更新：正在运输</el-button>
      <el-button v-if="order && order.status === 'in_transit'" type="success" @click="addRecord('arrived')">更新：已到达</el-button>
      <el-button v-if="order && order.status === 'arrived'" type="warning" @click="showPodDialog = true">POD 签收确认</el-button>
      <el-button v-if="order && order.status === 'signed'" type="success" @click="completeOrder">完成订单</el-button>
      <el-button v-if="order" @click="viewFreight" style="margin-left:10px">查看运费</el-button>
    </el-card>

    <!-- 跟踪时间线 -->
    <el-card>
      <template #header><span>运输跟踪记录</span></template>
      <el-timeline v-if="records.length">
        <el-timeline-item v-for="rec in records" :key="rec.id"
          :timestamp="rec.recorded_at?.substring(0,19)" placement="top" :type="timelineType(rec.status)">
          <el-card shadow="never">
            <h4>{{ statusLabel(rec.status) }}</h4>
            <p>位置：{{ rec.location }}</p>
            <p>描述：{{ rec.description }}</p>
            <p style="color:#909399;font-size:12px">记录人：{{ rec.recorder_name }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无跟踪记录" />
    </el-card>

    <!-- POD 签收确认对话框 -->
    <el-dialog v-model="showPodDialog" title="POD 签收确认" width="500px">
      <el-form :model="podForm" label-width="100px">
        <el-form-item label="签收人姓名" required>
          <el-input v-model="podForm.signee_name" placeholder="请输入签收人姓名" />
        </el-form-item>
        <el-form-item label="签收人电话">
          <el-input v-model="podForm.signee_phone" placeholder="请输入签收人电话" />
        </el-form-item>
        <el-form-item label="POD 图片">
          <el-input v-model="podForm.pod_image" placeholder="模拟上传，输入图片路径" />
          <div style="color:#909399;font-size:12px;margin-top:5px">教学模拟：直接输入图片文件名，如 pod001.jpg</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPodDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmPod">确认签收</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { orderAPI, transportRecordAPI } from '../api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const order = ref(null)
const records = ref([])
const loading = ref(false)
const isMobile = ref(false)
const showPodDialog = ref(false)
const podForm = reactive({ signee_name: '', signee_phone: '', pod_image: '' })
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const statusMap = ['pending','approved','dispatched','in_transit','arrived','signed','completed']
const stepIndex = computed(() => order.value ? statusMap.indexOf(order.value.status) : 0)

const statusType = (s) => ({ pending:'warning', approved:'', dispatched:'', in_transit:'primary', arrived:'success', signed:'', completed:'success', cancelled:'info' }[s]||'info')
const statusLabel = (s) => ({ pending:'待审核', approved:'已审核', dispatched:'已调度', in_transit:'运输中', arrived:'已到达', signed:'已签收', completed:'已完成', cancelled:'已取消' }[s]||s)
const timelineType = (s) => ({ departed:'primary', in_transit:'primary', arrived:'success', signed:'success' }[s]||'info')

const loadData = async () => {
  loading.value = true
  const id = route.params.id
  const [r1, r2] = await Promise.all([
    orderAPI.get(id),
    transportRecordAPI.list({ order_id: id })
  ])
  if (r1.data.code === 200) order.value = r1.data.data
  if (r2.data.code === 200) records.value = r2.data.data
  loading.value = false
}

const addRecord = async (status) => {
  try {
    const { value: location } = await ElMessageBox.prompt('请输入当前位置', '更新状态', { inputPlaceholder: '例如：广深高速K50' })
    const res = await transportRecordAPI.create({
      order_id: route.params.id,
      status,
      location,
      description: statusLabel(status)
    })
    if (res.data.code === 200) { ElMessage.success('更新成功'); loadData() }
    else ElMessage.error(res.data.message)
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

const viewFreight = async () => {
  const res = await orderAPI.getFreight(route.params.id)
  if (res.data.code === 200) {
    const f = res.data.data
    ElMessage.info(`计算运费: ¥${f.calculated_freight}（重量${f.weight}kg x ¥0.005 + 体积${f.volume}m³ x ¥100）`)
  }
}

const confirmPod = async () => {
  if (!podForm.signee_name) { ElMessage.warning('请输入签收人姓名'); return }
  try {
    const res = await orderAPI.confirmPod(route.params.id, podForm)
    if (res.data.code === 200) {
      ElMessage.success('POD签收确认成功')
      showPodDialog.value = false
      loadData()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) { ElMessage.error('操作失败') }
}

const completeOrder = async () => {
  try {
    await ElMessageBox.confirm('确认完成该订单？完成后将生成应收款项。', '完成订单', { type: 'warning' })
    const res = await orderAPI.complete(route.params.id)
    if (res.data.code === 200) {
      ElMessage.success('订单已完成')
      loadData()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

onMounted(() => { checkWidth(); window.addEventListener('resize', checkWidth); loadData() })
onUnmounted(() => { window.removeEventListener('resize', checkWidth) })
</script>
