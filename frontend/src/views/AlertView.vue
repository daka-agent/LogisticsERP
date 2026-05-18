<template>
  <div class="alert-view">
    <PageGuide v-bind="guideConfig" />
<el-card>
      <template #header>
        <div class="card-header">
          <h2>⚠️ 预警中心</h2>
          <el-button type="primary" plain @click="loadAlerts" :loading="loading">
            刷新
          </el-button>
        </div>
      </template>

      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stat-cards">
        <el-col :span="4" v-for="stat in statCards" :key="stat.type">
          <el-card shadow="hover" class="stat-card" @click="scrollTo(stat.type)">
            <div class="stat-num" :style="{ color: stat.color }">{{ stat.count }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 库存预警 -->
      <div v-if="alerts.inventory && alerts.inventory.length" :ref="(el) => setSectionRef('inventory', el)">
        <h3 class="section-title">📦 库存预警</h3>
        <el-table :data="alerts.inventory" stripe border size="small">
          <el-table-column prop="goods_name" label="商品" />
          <el-table-column prop="warehouse_name" label="仓库" />
          <el-table-column prop="message" label="预警信息" />
          <el-table-column label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'high' ? 'danger' : 'warning'" size="small">
                {{ row.severity === 'high' ? '高' : '中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="goTo(row.link)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 过期预警 -->
      <div v-if="alerts.expiry && alerts.expiry.length" :ref="(el) => setSectionRef('expiry', el)">
        <h3 class="section-title">⏰ 有效期预警</h3>
        <el-table :data="alerts.expiry" stripe border size="small">
          <el-table-column prop="goods_name" label="商品" />
          <el-table-column prop="warehouse_name" label="仓库" />
          <el-table-column prop="message" label="预警信息" />
          <el-table-column label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'high' ? 'danger' : 'warning'" size="small">
                {{ row.severity === 'high' ? '高' : '中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="goTo(row.link)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 应付预警 -->
      <div v-if="alerts.payable && alerts.payable.length" :ref="(el) => setSectionRef('payable', el)">
        <h3 class="section-title">💰 应付账款预警</h3>
        <el-table :data="alerts.payable" stripe border size="small">
          <el-table-column prop="payable_no" label="应付单号" />
          <el-table-column prop="supplier_name" label="供应商" />
          <el-table-column prop="message" label="预警信息" />
          <el-table-column label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'high' ? 'danger' : 'warning'" size="small">
                {{ row.severity === 'high' ? '高' : '中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="goTo(row.link)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 应收预警 -->
      <div v-if="alerts.receivable && alerts.receivable.length" :ref="(el) => setSectionRef('receivable', el)">
        <h3 class="section-title">💵 应收账款预警</h3>
        <el-table :data="alerts.receivable" stripe border size="small">
          <el-table-column prop="receivable_no" label="应收单号" />
          <el-table-column prop="customer_name" label="客户" />
          <el-table-column prop="message" label="预警信息" />
          <el-table-column label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'high' ? 'danger' : 'warning'" size="small">
                {{ row.severity === 'high' ? '高' : '中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="goTo(row.link)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 运输预警 -->
      <div v-if="alerts.transport && alerts.transport.length" :ref="(el) => setSectionRef('transport', el)">
        <h3 class="section-title">🚚 运输超时预警</h3>
        <el-table :data="alerts.transport" stripe border size="small">
          <el-table-column prop="order_no" label="订单号" />
          <el-table-column prop="customer_name" label="客户" />
          <el-table-column prop="message" label="预警信息" />
          <el-table-column label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'high' ? 'danger' : 'warning'" size="small">
                {{ row.severity === 'high' ? '高' : '中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="goTo(row.link)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 合同预警 -->
      <div v-if="alerts.contract && alerts.contract.length" :ref="(el) => setSectionRef('contract', el)">
        <h3 class="section-title">📝 合同到期预警</h3>
        <el-table :data="alerts.contract" stripe border size="small">
          <el-table-column prop="contract_no" label="合同编号" />
          <el-table-column prop="message" label="预警信息" />
          <el-table-column label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'high' ? 'danger' : 'warning'" size="small">
                {{ row.severity === 'high' ? '高' : '中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="goTo(row.link)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 无预警 -->
      <el-empty v-if="total === 0 && !loading" description="暂无预警信息" />
    </el-card>
  </div>
</template>

<script setup>
import PageGuide from '../components/PageGuide.vue'

const guideConfig = { title: '预警中心操作指引', steps: [
        "查看各类预警信息",
        "按类型筛选预警",
        "及时处理预警事项"
    ], tips: [
        "六类预警：库存、有效期、应付、应收、运输超时、合同到期",
        "预警数据实时更新"
    ] }
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { alertAPI } from '../api/alert'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const alerts = ref({})
const total = ref(0)
const sectionRefs = ref({})

const statCards = computed(() => [
  { type: 'inventory', label: '库存预警', count: (alerts.value.inventory || []).length, color: '#F56C6C' },
  { type: 'expiry', label: '有效期预警', count: (alerts.value.expiry || []).length, color: '#E6A23C' },
  { type: 'payable', label: '应付账款', count: (alerts.value.payable || []).length, color: '#F56C6C' },
  { type: 'receivable', label: '应收账款', count: (alerts.value.receivable || []).length, color: '#F56C6C' },
  { type: 'transport', label: '运输超时', count: (alerts.value.transport || []).length, color: '#F56C6C' },
  { type: 'contract', label: '合同到期', count: (alerts.value.contract || []).length, color: '#E6A23C' },
])

const loadAlerts = async () => {
  loading.value = true
  try {
    const res = await alertAPI.list()
    if (res.data.code === 200) {
      alerts.value = res.data.data || {}
      total.value = res.data.total || 0
    }
  } catch (err) {
    ElMessage.error('加载预警失败')
  } finally {
    loading.value = false
  }
}

const setSectionRef = (type, el) => {
  if (el) sectionRefs.value[type] = el
}

const scrollTo = (type) => {
  const el = sectionRefs.value[type]
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const goTo = (link) => {
  if (link) router.push(link)
}

onMounted(() => {
  loadAlerts()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header h2 {
  margin: 0;
}
.stat-cards {
  margin-bottom: 24px;
}
.stat-card {
  cursor: pointer;
  text-align: center;
  transition: box-shadow 0.2s;
}
.stat-num {
  font-size: 28px;
  font-weight: bold;
}
.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
.section-title {
  margin: 24px 0 12px;
  font-size: 16px;
  color: #303133;
}
</style>
