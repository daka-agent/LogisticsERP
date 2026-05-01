import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Home', component: () => import('../views/HomeView.vue') },
      // 基础数据
      { path: 'suppliers', name: 'Suppliers', component: () => import('../views/SupplierView.vue') },
      { path: 'customers', name: 'Customers', component: () => import('../views/CustomerView.vue') },
      { path: 'goods', name: 'Goods', component: () => import('../views/GoodsView.vue') },
      { path: 'warehouses', name: 'Warehouses', component: () => import('../views/WarehouseView.vue') },
      { path: 'vehicles', name: 'Vehicles', component: () => import('../views/VehicleView.vue') },
      { path: 'drivers', name: 'Drivers', component: () => import('../views/DriverView.vue') },
      // 采购管理
      { path: 'purchase/requests', name: 'PurchaseRequests', component: () => import('../views/PurchaseRequestView.vue') },
      { path: 'purchase/orders', name: 'PurchaseOrders', component: () => import('../views/PurchaseOrderView.vue') },
      // 运输管理
      { path: 'transport/orders', name: 'TransportOrders', component: () => import('../views/TransportOrderView.vue') },
      { path: 'transport/orders/:id', name: 'TransportOrderDetail', component: () => import('../views/TransportOrderDetailView.vue') },
      // 仓储管理
      { path: 'warehouse/inbound', name: 'InboundOrders', component: () => import('../views/InboundOrderView.vue') },
      { path: 'warehouse/outbound', name: 'OutboundOrders', component: () => import('../views/OutboundOrderView.vue') },
      // 库存管理
      { path: 'inventory', name: 'Inventory', component: () => import('../views/InventoryView.vue') },
      { path: 'inventory/stock-count', name: 'StockCount', component: () => import('../views/StockCountView.vue') },
      // 数据报表
      { path: 'reports', name: 'Reports', component: () => import('../views/ReportsView.vue') },
      // 财务管理
      { path: 'finance/overview', name: 'FinanceOverview', component: () => import('../views/finance/FinanceOverview.vue') },
      { path: 'finance/payable', name: 'AccountsPayable', component: () => import('../views/finance/AccountsPayableView.vue') },
      { path: 'finance/payable/:id', name: 'PayableDetail', component: () => import('../views/finance/PayableDetailView.vue') },
      { path: 'finance/receivable', name: 'AccountsReceivable', component: () => import('../views/finance/AccountsReceivableView.vue') },
      { path: 'finance/receivable/:id', name: 'ReceivableDetail', component: () => import('../views/finance/ReceivableDetailView.vue') },
      // 合同管理
      { path: 'contract/purchase', name: 'PurchaseContract', component: () => import('../views/contract/PurchaseContractView.vue') },
      { path: 'contract/transport', name: 'TransportContract', component: () => import('../views/contract/TransportContractView.vue') },
      { path: 'contract/detail/:type/:id', name: 'ContractDetail', component: () => import('../views/contract/ContractDetailView.vue') },
      // 多人协作
      { path: 'collab/hall', name: 'RoomHall', component: () => import('../views/RoomHallView.vue') },
      // 教师后台
      { path: 'teacher/scenes', name: 'SceneManage', component: () => import('../views/teacher/SceneManageView.vue') },
      { path: 'teacher/progress', name: 'ProgressMonitor', component: () => import('../views/teacher/ProgressMonitorView.vue') },
      { path: 'teacher/events', name: 'EventInject', component: () => import('../views/teacher/EventInjectView.vue') },
      { path: 'teacher/scores', name: 'ScoreManage', component: () => import('../views/teacher/ScoreManageView.vue') },
      { path: 'teacher/logs', name: 'OperationLog', component: () => import('../views/teacher/OperationLogView.vue') },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 防止并发重复调用 checkAuth
let authCheckPromise = null

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 不需要认证的页面直接放行
  if (!to.meta.requiresAuth) {
    next()
    return
  }

  // 已经登录，直接放行
  if (authStore.isLoggedIn) {
    next()
    return
  }

  // 未登录，调用 checkAuth 验证 session
  if (!authCheckPromise) {
    authCheckPromise = authStore.checkAuth().finally(() => {
      authCheckPromise = null
    })
  }
  await authCheckPromise

  if (authStore.isLoggedIn) {
    next()
  } else {
    next('/login')
  }
})

export default router
