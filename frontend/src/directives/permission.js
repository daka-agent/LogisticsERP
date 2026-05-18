/**
 * v-permission 自定义指令
 *
 * 两种用法：
 *   1. 角色控制:  v-role="'admin','teacher'"
 *   2. 权限代码:  v-permission="'purchase:approve'"
 *
 * admin/teacher 角色自动放行所有权限。
 * 不匹配时隐藏 DOM 元素（display:none，而非移除，以支持动态角色切换）。
 */

import { useAuthStore } from '../stores/auth'

const SUPER_ROLES = ['admin', 'teacher']

function getRoleCode() {
  try {
    const authStore = useAuthStore()
    return authStore.user?.role_code
  } catch {
    return null
  }
}

function checkRoles(value) {
  const roleCode = getRoleCode()
  if (!roleCode || !value) return false
  if (SUPER_ROLES.includes(roleCode)) return true

  const roles = typeof value === 'string'
    ? value.split(',').map(r => r.trim()).filter(Boolean)
    : Array.isArray(value)
      ? value
      : []

  return roles.includes(roleCode)
}

function checkPermission(value) {
  const roleCode = getRoleCode()
  if (!roleCode || !value) return false
  if (SUPER_ROLES.includes(roleCode)) return true

  try {
    const authStore = useAuthStore()
    const permissions = authStore.permissions || []
    // 支持单个代码字符串或逗号分隔的多个代码
    const codes = typeof value === 'string'
      ? value.split(',').map(c => c.trim()).filter(Boolean)
      : Array.isArray(value)
        ? value
        : []
    return codes.some(code => permissions.includes(code))
  } catch {
    return false
  }
}

/**
 * v-permission="'purchase:approve'"
 * 按权限代码控制元素可见性
 */
export const permissionDirective = {
  mounted(el, binding) {
    if (!checkPermission(binding.value)) {
      el.style.display = 'none'
      el.dataset.permissionHidden = 'true'
    }
  },
  updated(el, binding) {
    const hidden = el.dataset.permissionHidden === 'true'
    const allowed = checkPermission(binding.value)
    if (hidden && allowed) {
      el.style.display = ''
      delete el.dataset.permissionHidden
    } else if (!hidden && !allowed) {
      el.style.display = 'none'
      el.dataset.permissionHidden = 'true'
    }
  }
}

/**
 * v-role="'admin','teacher'"
 * 按角色控制元素可见性
 */
export const roleDirective = {
  mounted(el, binding) {
    if (!checkRoles(binding.value)) {
      el.style.display = 'none'
      el.dataset.roleHidden = 'true'
    }
  },
  updated(el, binding) {
    const hidden = el.dataset.roleHidden === 'true'
    const allowed = checkRoles(binding.value)
    if (hidden && allowed) {
      el.style.display = ''
      delete el.dataset.roleHidden
    } else if (!hidden && !allowed) {
      el.style.display = 'none'
      el.dataset.roleHidden = 'true'
    }
  }
}
