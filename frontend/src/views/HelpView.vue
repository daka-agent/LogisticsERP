<template>
  <div class="help-view">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span class="page-title">帮助中心</span>
      </template>
    </el-page-header>

    <!-- 搜索框 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索帮助内容..."
        prefix-icon="Search"
        clearable
        size="large"
      />
    </div>

    <div class="help-layout">
      <!-- 左侧目录 -->
      <div class="help-sidebar" :class="{ 'sidebar-hidden': isMobile && !sidebarOpen }">
        <div class="sidebar-toggle" v-if="isMobile" @click="sidebarOpen = !sidebarOpen">
          <el-icon><Menu /></el-icon>
        </div>
        <el-menu
          :default-active="activeSection"
          @select="scrollToSection"
          class="help-menu"
        >
          <el-menu-item v-for="section in filteredSections" :key="section.id" :index="section.id">
            <el-icon><component :is="section.icon" /></el-icon>
            <span>{{ section.title }}</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容 -->
      <div class="help-content" ref="contentRef">
        <div
          v-for="section in filteredSections"
          :key="section.id"
          :id="section.id"
          class="help-section"
        >
          <h2>
            <el-icon><component :is="section.icon" /></el-icon>
            {{ section.title }}
          </h2>
          <div class="section-body" v-html="section.html"></div>
        </div>
        <el-empty v-if="filteredSections.length === 0" description="未找到匹配内容" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  InfoFilled, Key, ShoppingCart, Van, Box, Goods,
  Money, Document, User, Setting, QuestionFilled, Menu
} from '@element-plus/icons-vue'

const searchQuery = ref('')
const activeSection = ref('intro')
const contentRef = ref(null)
const isMobile = ref(false)
const sidebarOpen = ref(false)

const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const sections = [
  {
    id: 'intro', title: '系统简介', icon: InfoFilled,
    html: `
      <p>大卡@物流系统模拟仿真是一套面向本科物流管理专业的教学软件，模拟了中小型物流企业ERP系统的核心业务流程。</p>
      <h3>核心模块</h3>
      <ul>
        <li><strong>采购管理</strong>：采购申请 → 审批 → 采购订单 → 到货入库</li>
        <li><strong>运输管理</strong>：运输订单 → 审核 → 调度 → 运输 → 签收</li>
        <li><strong>仓储管理</strong>：入库上架 → 出库拣货 → 发货</li>
        <li><strong>库存管理</strong>：库存查询、预警监控、库存盘点</li>
        <li><strong>财务管理</strong>：应付账款、应收账款</li>
        <li><strong>合同管理</strong>：采购合同、运输合同</li>
      </ul>
      <h3>教学模式</h3>
      <ul>
        <li><strong>单人练习</strong>：学生独立完成所有角色的操作</li>
        <li><strong>多人协作</strong>：5-6人分组，分别扮演不同角色协同完成业务流程</li>
      </ul>
    `
  },
  {
    id: 'quickstart', title: '快速开始', icon: Key,
    html: `
      <h3>登录账号</h3>
      <p>系统启动后会自动初始化以下账号，使用对应的用户名和密码登录即可：</p>
      <table class="help-table">
        <tr><th>角色</th><th>用户名</th><th>密码</th><th>说明</th></tr>
        <tr><td>管理员</td><td>admin</td><td>admin123</td><td>拥有所有权限</td></tr>
        <tr><td>教师</td><td>teacher01</td><td>123456</td><td>教学管理后台</td></tr>
        <tr><td>学生</td><td>student01</td><td>123456</td><td>普通学生账号</td></tr>
        <tr><td>采购员</td><td>purchaser01</td><td>123456</td><td>负责采购业务</td></tr>
        <tr><td>客服</td><td>cs01</td><td>123456</td><td>负责客户管理</td></tr>
        <tr><td>调度员</td><td>dispatcher01</td><td>123456</td><td>负责运输调度</td></tr>
        <tr><td>仓管员</td><td>keeper01</td><td>123456</td><td>负责仓储管理</td></tr>
        <tr><td>司机</td><td>driver01</td><td>123456</td><td>负责运输执行</td></tr>
      </table>
      <h3>首次使用建议</h3>
      <ol>
        <li>使用 admin 账号登录，先浏览首页了解系统概况</li>
        <li>按模块顺序依次操作：采购 → 运输 → 仓储 → 库存</li>
        <li>每个页面顶部有蓝色操作提示条，可帮助你了解操作步骤</li>
        <li>如遇问题，可查看本帮助中心的对应章节</li>
      </ol>
    `
  },
  {
    id: 'purchase', title: '采购管理流程', icon: ShoppingCart,
    html: `
      <h3>流程概览</h3>
      <div class="flow-steps">
        <div class="flow-step"><span class="flow-num">1</span>创建采购申请</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">2</span>审批</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">3</span>生成采购订单</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">4</span>确认并完成</div>
      </div>
      <h3>操作详解</h3>
      <h4>第1步：创建采购申请</h4>
      <p>进入「采购管理 → 采购申请」页面，点击「新建申请」：</p>
      <ul>
        <li>选择需要采购的商品（从下拉列表选择）</li>
        <li>填写采购数量（必须大于0）</li>
        <li>填写期望单价（可选，用于预算参考）</li>
        <li>选择紧急程度：普通 / 紧急 / 特急</li>
        <li>填写申请原因（可选）</li>
      </ul>
      <h4>第2步：审批采购申请</h4>
      <p>采购申请创建后状态为「待审批」，需要审批通过后才能生成采购订单：</p>
      <ul>
        <li>点击对应行的「审批」按钮</li>
        <li>输入审批意见（默认"同意"）</li>
        <li>审批通过后，系统自动创建采购订单</li>
        <li>也可以「驳回」申请，需填写驳回原因</li>
      </ul>
      <h4>第3步：管理采购订单</h4>
      <p>进入「采购管理 → 采购订单」页面：</p>
      <ul>
        <li>审批通过后自动生成的订单状态为「待确认」</li>
        <li>需关联供应商，确认订单信息</li>
        <li>订单完成后自动生成应付账款</li>
      </ul>
      <h3>注意事项</h3>
      <ul>
        <li>采购申请必须选择商品和数量才能提交</li>
        <li>未审批的申请不能生成采购订单</li>
        <li>驳回的申请可以重新提交（需新建）</li>
      </ul>
    `
  },
  {
    id: 'transport', title: '运输管理流程', icon: Van,
    html: `
      <h3>流程概览</h3>
      <div class="flow-steps">
        <div class="flow-step"><span class="flow-num">1</span>创建运输订单</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">2</span>审核</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">3</span>调度</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">4</span>运输</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">5</span>签收</div>
      </div>
      <h3>操作详解</h3>
      <h4>第1步：创建运输订单</h4>
      <p>进入「运输管理 → 运输订单」页面，点击「新建订单」：</p>
      <ul>
        <li>填写发货地和收货地</li>
        <li>填写货物信息（重量、体积等）</li>
        <li>选择客户（可选）</li>
      </ul>
      <h4>第2步：审核</h4>
      <ul>
        <li>订单创建后需审核通过</li>
        <li>审核不通过需驳回并说明原因</li>
      </ul>
      <h4>第3步：调度</h4>
      <ul>
        <li>审核通过后进行车辆调度</li>
        <li><strong>只能选择"空闲"状态的车辆</strong></li>
        <li><strong>只能选择"可用"状态的司机</strong></li>
        <li>调度后车辆变为"在途"，司机变为"在途"</li>
      </ul>
      <h4>第4-5步：运输与签收</h4>
      <ul>
        <li>更新运输状态（在途 → 到达）</li>
        <li>到达后进行签收确认</li>
        <li>签收后订单自动完成</li>
        <li>完成时自动计算运费（重量 x 5元/kg + 体积 x 100元/m³）</li>
        <li>完成时自动生成应收账款</li>
        <li>车辆和司机自动释放为空闲/可用状态</li>
      </ul>
      <h3>注意事项</h3>
      <ul>
        <li>运费在订单完成时自动计算，无需手动输入</li>
        <li>应收账款由系统自动生成，在「财务管理 → 应收账款」中查看</li>
        <li>签收后不可撤销，请确认后再操作</li>
      </ul>
    `
  },
  {
    id: 'warehouse', title: '仓储管理流程', icon: Box,
    html: `
      <h3>入库管理</h3>
      <div class="flow-steps">
        <div class="flow-step"><span class="flow-num">1</span>创建入库单</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">2</span>选择货位上架</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">3</span>完成入库</div>
      </div>
      <p>进入「仓储管理 → 入库管理」：</p>
      <ul>
        <li>新建入库单，选择商品和数量</li>
        <li>上架时选择目标仓库 → 库区 → 货位</li>
        <li>确认上架后，库存自动增加</li>
      </ul>
      <h3>出库管理</h3>
      <div class="flow-steps">
        <div class="flow-step"><span class="flow-num">1</span>创建出库单</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">2</span>从货位拣货</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">3</span>确认发货</div>
      </div>
      <p>进入「仓储管理 → 出库管理」：</p>
      <ul>
        <li>新建出库单，选择要出库的商品</li>
        <li>拣货时从指定货位取出商品</li>
        <li>确认发货后，库存自动扣减</li>
      </ul>
      <h3>仓库三级结构</h3>
      <p>仓库管理采用三级结构：仓库 → 库区 → 货位</p>
      <ul>
        <li>必须先创建仓库</li>
        <li>在仓库下创建库区</li>
        <li>在库区下创建货位</li>
        <li>删除上级会级联删除下级，请谨慎操作</li>
      </ul>
    `
  },
  {
    id: 'inventory', title: '库存管理流程', icon: Goods,
    html: `
      <h3>库存查询</h3>
      <p>进入「库存管理 → 库存查询」页面：</p>
      <ul>
        <li>查看所有商品的当前库存数量</li>
        <li>支持按商品名称、SKU等条件筛选</li>
        <li>低于安全库存的商品会显示预警标识</li>
        <li>可导出库存数据（Excel/CSV格式）</li>
      </ul>
      <h3>库存盘点</h3>
      <p>进入「库存管理 → 库存盘点」页面：</p>
      <div class="flow-steps">
        <div class="flow-step"><span class="flow-num">1</span>创建盘点单</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">2</span>录入实际数量</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">3</span>调整差异</div>
      </div>
      <ul>
        <li>创建盘点单，选择要盘点的商品</li>
        <li>逐一录入实际库存数量</li>
        <li>确认差异后系统自动调整库存</li>
        <li><strong>差异调整将直接修改库存数量，请认真核对</strong></li>
      </ul>
      <h3>库存预警</h3>
      <p>系统自动监控以下预警：</p>
      <ul>
        <li>库存数量低于安全库存</li>
        <li>商品临近有效期</li>
      </ul>
    `
  },
  {
    id: 'finance', title: '财务管理流程', icon: Money,
    html: `
      <h3>财务概览</h3>
      <p>进入「财务管理 → 财务概览」页面，查看：</p>
      <ul>
        <li>应付账款和应收账款汇总数据</li>
        <li>各状态账款分布（待付款/部分付款/已付清）</li>
        <li>本月收支趋势图</li>
      </ul>
      <h3>应付账款</h3>
      <p>应付账款由采购订单完成时自动生成：</p>
      <ul>
        <li>在「应付账款」列表查看所有应付记录</li>
        <li>点击记录进入详情页进行付款操作</li>
        <li>支持多次部分付款，直到全部付清</li>
      </ul>
      <h3>应收账款</h3>
      <p>应收账款由运输订单完成时自动生成：</p>
      <ul>
        <li>在「应收账款」列表查看所有应收记录</li>
        <li>点击记录进入详情页进行收款操作</li>
        <li>支持多次部分收款，直到全部收齐</li>
      </ul>
      <h3>注意事项</h3>
      <ul>
        <li>应付/应收账款无需手动创建，系统自动生成</li>
        <li>运费计算公式：重量 x 5元/kg + 体积 x 100元/m³</li>
      </ul>
    `
  },
  {
    id: 'contract', title: '合同管理流程', icon: Document,
    html: `
      <h3>采购合同</h3>
      <p>进入「合同管理 → 采购合同」页面：</p>
      <div class="flow-steps">
        <div class="flow-step"><span class="flow-num">1</span>创建采购合同</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">2</span>提交审批</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step"><span class="flow-num">3</span>审批生效</div>
      </div>
      <ul>
        <li>填写合同基本信息（供应商、金额、有效期等）</li>
        <li>提交后等待审批</li>
        <li>审批通过后合同生效</li>
      </ul>
      <h3>运输合同</h3>
      <p>流程与采购合同类似，关联的是运输相关业务。</p>
      <h3>合同管理</h3>
      <ul>
        <li>生效中的合同可用于业务关联</li>
        <li>可以申请终止合同</li>
        <li>临近到期的合同会在预警中心提示</li>
      </ul>
    `
  },
  {
    id: 'collab', title: '多人协作模式', icon: User,
    html: `
      <h3>协作大厅</h3>
      <p>进入「多人协作 → 协作大厅」页面：</p>
      <ul>
        <li><strong>创建房间</strong>：设置房间名称和小组人数，创建后自动成为房主</li>
        <li><strong>加入房间</strong>：浏览可用房间，选择角色后加入</li>
        <li><strong>角色选择</strong>：采购员、调度员、仓管员、司机等</li>
      </ul>
      <h3>协作流程</h3>
      <ol>
        <li>教师创建协作房间（或由学生创建）</li>
        <li>学生选择房间并加入，分配角色</li>
        <li>各角色按业务流程协同操作</li>
        <li>教师可在后台监控进度、注入突发事件、查看成绩</li>
      </ol>
      <h3>角色职责</h3>
      <table class="help-table">
        <tr><th>角色</th><th>主要职责</th></tr>
        <tr><td>采购员</td><td>创建采购申请、管理采购订单</td></tr>
        <tr><td>调度员</td><td>审核运输订单、调度车辆和司机</td></tr>
        <tr><td>仓管员</td><td>入库上架、出库拣货、库存盘点</td></tr>
        <tr><td>司机</td><td>更新运输状态、签收确认</td></tr>
        <tr><td>客服</td><td>客户管理、处理客户需求</td></tr>
      </table>
      <h3>实时通信</h3>
      <p>协作模式下，操作会通过WebSocket实时同步给所有成员。例如：</p>
      <ul>
        <li>采购申请审批后，通知采购员创建订单</li>
        <li>运输订单调度后，通知司机执行运输</li>
        <li>教师注入突发事件后，全员收到通知</li>
      </ul>
    `
  },
  {
    id: 'teacher', title: '教师后台功能', icon: Setting,
    html: `
      <p>教师后台仅对管理员(admin)和教师(teacher01)角色可见，位于侧边栏「教师后台」菜单下。</p>
      <h3>场景管理</h3>
      <ul>
        <li>创建和管理教学场景</li>
        <li>配置场景的初始数据和业务目标</li>
        <li>系统内置5个预设场景，可直接使用</li>
      </ul>
      <h3>进度监控</h3>
      <ul>
        <li>查看各协作房间的实时进度</li>
        <li>了解各小组的操作完成情况</li>
      </ul>
      <h3>事件注入</h3>
      <ul>
        <li>向指定协作房间注入突发事件</li>
        <li>6种事件类型：库存积压、运输延误、供应商断货等</li>
        <li>事件通过WebSocket实时通知给小组成员</li>
      </ul>
      <h3>成绩统计</h3>
      <ul>
        <li>查看小组和个人评分</li>
        <li>评分维度：操作正确性、流程完整性、操作效率</li>
        <li>支持查看评分详情</li>
      </ul>
      <h3>操作日志</h3>
      <ul>
        <li>查看所有学生的操作记录</li>
        <li>支持按用户、模块、正确性筛选</li>
        <li><strong>「学生操作回放」</strong>功能：选择学生后查看其完整操作时间线、模块覆盖、耗时分析</li>
        <li>点击任意日志条目可查看详细的请求数据和响应数据</li>
      </ul>
    `
  },
  {
    id: 'faq', title: '常见问题', icon: QuestionFilled,
    html: `
      <h3>Q: 登录后页面空白/报错怎么办？</h3>
      <p>A: 请确认后端服务已启动（默认端口5000），前端服务已启动（默认端口5173）。检查浏览器控制台是否有红色错误信息。</p>

      <h3>Q: 忘记密码怎么办？</h3>
      <p>A: 目前需要联系教师或管理员重置密码。也可以直接操作数据库重新设置。</p>

      <h3>Q: 调度时看不到可选的车辆/司机？</h3>
      <p>A: 只有状态为"空闲"的车辆和"可用"的司机才会出现在调度列表中。如果有车辆/司机正在执行运输任务，需要等任务完成后才会释放。</p>

      <h3>Q: 运费是怎么计算的？</h3>
      <p>A: 运费在运输订单完成时自动计算，公式为：重量 x 5元/kg + 体积 x 100元/m³。</p>

      <h3>Q: 应付/应收账款什么时候生成？</h3>
      <p>A: 应付账款在采购订单完成时自动生成，应收账款在运输订单完成时自动生成。</p>

      <h3>Q: 库存盘点调整后能撤销吗？</h3>
      <p>A: 目前盘点调整后不可撤销，请在确认前仔细核对数据。</p>

      <h3>Q: 时间显示不准确？</h3>
      <p>A: 系统统一使用北京时间（UTC+8），已修复旧版UTC时间问题。如仍有疑问请联系管理员。</p>

      <h3>Q: 如何重置所有数据？</h3>
      <p>A: 在后端目录执行 <code>python reset_db.py</code>，将清除所有数据并重新初始化。</p>
    `
  },
]

// 搜索过滤
const filteredSections = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return sections
  return sections.filter(s =>
    s.title.toLowerCase().includes(q) ||
    s.html.toLowerCase().includes(q)
  )
})

// 滚动到指定章节
function scrollToSection(id) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
  if (isMobile.value) sidebarOpen.value = false
}

onMounted(() => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.help-view { padding: 20px; max-width: 1200px; margin: 0 auto; }

.page-title { font-size: 18px; font-weight: 600; }

.search-bar { margin: 16px 0; }

.help-layout { display: flex; gap: 20px; }

/* 左侧目录 */
.help-sidebar {
  width: 200px; flex-shrink: 0; position: sticky; top: 80px;
  max-height: calc(100vh - 160px); overflow-y: auto;
}

.sidebar-toggle {
  display: none; padding: 10px; text-align: center;
  background: #f5f7fa; border-radius: 6px; cursor: pointer;
  margin-bottom: 10px;
}

.help-menu {
  border-right: none;
}

.help-menu .el-menu-item {
  font-size: 14px; height: 40px; line-height: 40px;
}

.help-menu .el-menu-item .el-icon {
  margin-right: 6px;
}

/* 右侧内容 */
.help-content {
  flex: 1; min-width: 0;
}

.help-section {
  margin-bottom: 32px; scroll-margin-top: 80px;
}

.help-section h2 {
  display: flex; align-items: center; gap: 8px;
  font-size: 20px; color: #303133; margin-bottom: 16px;
  padding-bottom: 8px; border-bottom: 2px solid #409EFF;
}

.help-section h3 {
  font-size: 16px; color: #303133; margin: 16px 0 8px;
}

.help-section h4 {
  font-size: 14px; color: #606266; margin: 12px 0 6px;
}

.help-section p {
  font-size: 14px; color: #606266; line-height: 1.8;
}

.help-section ul, .help-section ol {
  padding-left: 20px; font-size: 14px; color: #606266; line-height: 2;
}

.help-section code {
  background: #F5F7FA; padding: 2px 6px; border-radius: 3px;
  font-size: 13px; color: #E6A23C;
}

/* 流程步骤 */
:deep(.flow-steps) {
  display: flex; align-items: center; flex-wrap: wrap;
  gap: 8px; margin: 12px 0;
}

:deep(.flow-step) {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px; background: #ECF5FF; border-radius: 6px;
  font-size: 13px; color: #409EFF; white-space: nowrap;
}

:deep(.flow-num) {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  background: #409EFF; color: white; font-size: 12px; font-weight: bold;
}

:deep(.flow-arrow) {
  color: #C0C4CC; font-size: 16px;
}

/* 表格 */
:deep(.help-table) {
  width: 100%; border-collapse: collapse; margin: 10px 0;
  font-size: 13px;
}

:deep(.help-table th),
:deep(.help-table td) {
  border: 1px solid #EBEEF5; padding: 8px 12px; text-align: left;
}

:deep(.help-table th) {
  background: #F5F7FA; font-weight: 600; color: #303133;
}

:deep(.help-table td) {
  color: #606266;
}

/* 移动端 */
@media (max-width: 768px) {
  .help-view { padding: 10px; }

  .help-sidebar {
    position: fixed; left: -220px; top: 0;
    height: 100vh; z-index: 2000;
    background: white; box-shadow: 2px 0 8px rgba(0,0,0,0.1);
    transition: left 0.3s;
    padding-top: 50px;
  }

  .help-sidebar.sidebar-hidden { left: -220px; }

  .sidebar-toggle { display: block; }

  .help-section h2 { font-size: 17px; }
}
</style>
