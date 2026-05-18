/**
 * v-permission 自定义指令
 * 用法：v-permission="'admin','teacher'" 或 v-permission="['admin', 'teacher']"
 *
 * 逻辑：
 * - admin 角色自动放行所有
 * - teacher 角色自动放行所有
 * - 其他角色检查是否在允许列表中
 * - 不匹配时移除 DOM 元素（类似 v-if）
 */

const SUPER_ROLES = ['admin', 'teacher']

function hasPermission(allowedRoles, userRoleCode) {
  if (!allowedRoles || !userRoleCode) return false
  if (SUPER_ROLES.includes(userRoleCode)) return true

  // 支持字符串（逗号分隔）和数组格式
  const roles = typeof allowedRoles === 'string'
    ? allowedRoles.split(',').map(r => r.trim())
    : Array.isArray(allowedRoles)
      ? allowedRoles
      : []

  return roles.includes(userRoleCode)
}

export const permissionDirective = {
  mounted(el, binding) {
    const { value } = binding
    // 从 Pinia store 获取当前用户角色
    let roleCode = null
    try {
      const { useAuthStore } = require('../stores/auth')
      const authStore = useAuthStore()
      roleCode = authStore.user?.role_code
    } catch {
      // fallback: 从 localStorage 获取
      try {
        const stored = localStorage.getItem('user')
        if (stored) {
          roleCode = JSON.parse(stored).role_code
        }
      } catch {
        // ignore
      }
    }

    if (!hasPermission(value, roleCode)) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  },

  updated(el, binding) {
    // updated 生命周期与 mounted 相同逻辑
    const { value } = binding
    let roleCode = null
    try {
      const { useAuthStore } = require('../stores/auth')
      const authStore = useAuthStore()
      roleCode = authStore.user?.role_code
    } catch {
      try {
        const stored = localStorage.getItem('user')
        if (stored) {
          roleCode = JSON.parse(stored).role_code
        }
      } catch {
        // ignore
      }
    }

    if (!hasPermission(value, roleCode)) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  }
}

export default permissionDirective
