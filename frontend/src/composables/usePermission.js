/**
 * usePermission composable
 * 提供 JS 逻辑中的权限判断方法
 *
 * 用法：
 *   import { usePermission } from '../composables/usePermission'
 *   const { hasPermission, isSuperRole } = usePermission()
 *   if (hasPermission('admin', 'purchaser')) { ... }
 */

import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const SUPER_ROLES = ['admin', 'teacher']

export function usePermission() {
  const authStore = useAuthStore()

  const isSuperRole = computed(() => {
    const code = authStore.user?.role_code
    return code ? SUPER_ROLES.includes(code) : false
  })

  const currentRoleCode = computed(() => {
    return authStore.user?.role_code || null
  })

  /**
   * 检查当前用户是否拥有指定角色中的任一角色
   * @param {...string} roles - 允许的角色列表
   * @returns {boolean}
   */
  function hasPermission(...roles) {
    const code = currentRoleCode.value
    if (!code) return false
    if (SUPER_ROLES.includes(code)) return true
    return roles.includes(code)
  }

  /**
   * 获取角色对应的菜单可见性配置
   * @returns {Object} 菜单权限配置
   */
  function getMenuPermissions() {
    const code = currentRoleCode.value
    if (!code) {
      return _getEmptyMenuPermissions()
    }

    const isSuper = SUPER_ROLES.includes(code)
    const isStudent = code === 'student'

    if (isSuper || isStudent) {
      return {
        suppliers: true,
        customers: true,
        goods: true,
        warehouses: true,
        vehicles: true,
        drivers: true,
        purchase: true,
        transport: true,
        warehouse: true,
        inventory: true,
        reports: isSuper,
        contracts: true,
        finance: true,
        collab: true,
        teacher: isSuper,
        alerts: true,
        help: true,
        users: isSuper,
      }
    }

    return {
      suppliers: code === 'purchaser',
      customers: ['customer_service', 'dispatcher'].includes(code),
      goods: true,
      warehouses: code === 'warehouse_keeper',
      vehicles: code === 'dispatcher',
      drivers: code === 'dispatcher',
      purchase: code === 'purchaser',
      transport: ['customer_service', 'dispatcher', 'driver'].includes(code),
      warehouse: code === 'warehouse_keeper',
      inventory: code === 'warehouse_keeper',
      reports: false,
      contracts: ['purchaser', 'customer_service'].includes(code),
      finance: ['purchaser', 'customer_service'].includes(code),
      collab: true,
      teacher: false,
      alerts: true,
      help: true,
      users: false,
    }
  }

  return {
    hasPermission,
    isSuperRole,
    currentRoleCode,
    getMenuPermissions,
  }
}

function _getEmptyMenuPermissions() {
  return {
    suppliers: false, customers: false, goods: false, warehouses: false,
    vehicles: false, drivers: false, purchase: false, transport: false,
    warehouse: false, inventory: false, reports: false, contracts: false,
    finance: false, collab: false, teacher: false, alerts: false,
    help: true, users: false,
  }
}
