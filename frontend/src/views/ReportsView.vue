<template>
  <div class="reports-container">
    <h2>数据可视化报表</h2>

    <!-- 总览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="item in overviewData" :key="item.label">
        <el-card shadow="hover" class="overview-card">
          <div class="card-content">
            <div class="card-value">{{ item.value }}</div>
            <div class="card-label">{{ item.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 库存周转率折线图 -->
      <el-col :xs="24" :sm="24" :md="12">
        <el-card>
          <template #header>
            <span>库存周转率趋势</span>
          </template>
          <div ref="turnoverChart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <!-- 采购成本对比柱状图 -->
      <el-col :xs="24" :sm="24" :md="12">
        <el-card>
          <template #header>
            <span>采购成本对比</span>
          </template>
          <div ref="costChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <!-- 运输准时率饼图 -->
      <el-col :xs="24" :sm="24" :md="12">
        <el-card>
          <template #header>
            <span>运输准时率</span>
          </template>
          <div ref="ontimeChart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <!-- 仓库利用率雷达图 -->
      <el-col :xs="24" :sm="24" :md="12">
        <el-card>
          <template #header>
            <span>仓库利用率</span>
          </template>
          <div ref="utilizationChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

// 图表引用
const turnoverChart = ref(null)
const costChart = ref(null)
const ontimeChart = ref(null)
const utilizationChart = ref(null)

// 总览数据
const overviewData = ref([
  { label: '采购订单', value: 0 },
  { label: '运输订单', value: 0 },
  { label: '入库订单', value: 0 },
  { label: '出库订单', value: 0 },
  { label: '库存预警', value: 0 }
])

// 图表实例（用于resize）
const chartInstances = {}

// 移动端检测
const isMobile = ref(false)
const checkWidth = () => {
  isMobile.value = window.innerWidth < 768
  // ECharts响应式重绘
  Object.values(chartInstances).forEach(chart => {
    if (chart) chart.resize()
  })
}

// 获取总览数据
const fetchOverview = async () => {
  try {
    const response = await axios.get('/api/reports/overview')
    if (response.data.code === 200) {
      const data = response.data.data
      overviewData.value = [
        { label: '采购订单', value: data.purchase_orders },
        { label: '运输订单', value: data.transport_orders },
        { label: '入库订单', value: data.inbound_orders },
        { label: '出库订单', value: data.outbound_orders },
        { label: '库存预警', value: data.low_stock_alerts }
      ]
    }
  } catch (error) {
    console.error('获取总览数据失败:', error)
  }
}

// 初始化库存周转率折线图
const initTurnoverChart = async () => {
  try {
    const response = await axios.get('/api/reports/inventory-turnover')
    if (response.data.code === 200) {
      const { months, turnover_rates } = response.data.data

      const chart = echarts.init(turnoverChart.value)
      const option = {
        title: {
          text: '近6个月库存周转率',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        xAxis: {
          type: 'category',
          data: months
        },
        yAxis: {
          type: 'value',
          name: '周转率(%)'
        },
        series: [
          {
            data: turnover_rates,
            type: 'line',
            smooth: true,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(58,77,233,0.8)' },
                { offset: 1, color: 'rgba(58,77,233,0.1)' }
              ])
            },
            itemStyle: {
              color: '#3a4de9'
            }
          }
        ],
        tooltip: {
          trigger: 'axis'
        }
      }
      chart.setOption(option)
      chartInstances.turnover = chart
    }
  } catch (error) {
    console.error('获取库存周转率数据失败:', error)
  }
}

// 初始化采购成本对比柱状图
const initCostChart = async () => {
  try {
    const response = await axios.get('/api/reports/procurement-cost')
    if (response.data.code === 200) {
      const { suppliers, costs } = response.data.data

      const chart = echarts.init(costChart.value)
      const option = {
        title: {
          text: '供应商采购成本对比',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        xAxis: {
          type: 'category',
          data: suppliers,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '成本(元)'
        },
        series: [
          {
            data: costs,
            type: 'bar',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#188df0' }
              ])
            }
          }
        ],
        tooltip: {
          trigger: 'axis'
        }
      }
      chart.setOption(option)
      chartInstances.cost = chart
    }
  } catch (error) {
    console.error('获取采购成本数据失败:', error)
  }
}

// 初始化运输准时率饼图
const initOntimeChart = async () => {
  try {
    const response = await axios.get('/api/reports/transport-ontime')
    if (response.data.code === 200) {
      const { ontime_rate, delayed_rate } = response.data.data

      const chart = echarts.init(ontimeChart.value)
      const option = {
        title: {
          text: '运输准时率统计',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        series: [
          {
            type: 'pie',
            radius: '50%',
            data: [
              { value: ontime_rate, name: '准时', itemStyle: { color: '#67c23a' } },
              { value: delayed_rate, name: '延误', itemStyle: { color: '#f56c6c' } }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ],
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        }
      }
      chart.setOption(option)
      chartInstances.ontime = chart
    }
  } catch (error) {
    console.error('获取运输准时率数据失败:', error)
  }
}

// 初始化仓库利用率雷达图
const initUtilizationChart = async () => {
  try {
    const response = await axios.get('/api/reports/warehouse-utilization')
    if (response.data.code === 200) {
      const { warehouses, utilization_rates } = response.data.data

      const chart = echarts.init(utilizationChart.value)
      const option = {
        title: {
          text: '各仓库利用率',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        radar: {
          indicator: warehouses.map(name => ({ name, max: 100 }))
        },
        series: [
          {
            type: 'radar',
            data: [
              {
                value: utilization_rates,
                name: '仓库利用率(%)',
                areaStyle: {
                  color: 'rgba(64, 158, 255, 0.4)'
                },
                lineStyle: {
                  color: '#409eff'
                },
                itemStyle: {
                  color: '#409eff'
                }
              }
            ]
          }
        ],
        tooltip: {
          trigger: 'item'
        }
      }
      chart.setOption(option)
      chartInstances.utilization = chart
    }
  } catch (error) {
    console.error('获取仓库利用率数据失败:', error)
  }
}

onMounted(async () => {
  await nextTick()
  checkWidth()
  window.addEventListener('resize', checkWidth)
  fetchOverview()
  initTurnoverChart()
  initCostChart()
  initOntimeChart()
  initUtilizationChart()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.reports-container {
  padding: 20px;
}

.overview-cards {
  margin-bottom: 20px;
}

.overview-card {
  text-align: center;
}

.card-content {
  padding: 10px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.card-label {
  font-size: 14px;
  color: #606266;
}

.charts-row {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .card-value {
    font-size: 22px;
  }

  .reports-container h2 {
    font-size: 18px;
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
