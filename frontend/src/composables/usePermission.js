/**
 * usePermission composable
 *
 * 在 JS/TS 逻辑中检查权限（非模板指令）
 *
 * 用法：
 *   const { hasRole, hasPermission, hasAnyPermission } = usePermission()
 *   if (hasPermission('purchase:approve')) { ... }
 *   if (hasRole('admin', 'teacher')) { ... }
 */

import { useAuthStore } from '../stores/auth'

const SUPER_ROLES = ['admin', 'teacher']

export function usePermission() {
  const authStore = useAuthStore()

  /**
   * 检查当前用户是否拥有指定角色中的任一角色
   * @param {...string} roles - 角色代码列表
   */
  function hasRole(...roles) {
    return authStore.hasRole(...roles)
  }

  /**
   * 检查当前用户是否拥有指定权限代码
   * @param {string} code - 权限代码，如 'purchase:approve'
   */
  function hasPermission(code) {
    return authStore.hasPermission(code)
  }

  /**
   * 检查当前用户是否拥有任一指定权限代码
   * @param {...string} codes - 权限代码列表
   */
  function hasAnyPermission(...codes) {
    return authStore.hasAnyPermission(...codes)
  }

  /**
   * 获取当前用户角色代码
   */
  function getRoleCode() {
    return authStore.user?.role_code
  }

  /**
   * 是否为超级角色（admin/teacher）
   */
  function isSuperRole() {
    const code = authStore.user?.role_code
    return SUPER_ROLES.includes(code)
  }

  return {
    hasRole,
    hasPermission,
    hasAnyPermission,
    getRoleCode,
    isSuperRole
  }
}
