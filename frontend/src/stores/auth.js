import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const SUPER_ROLES = ['admin', 'teacher']

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const permissions = ref([])      // 权限代码列表，如 ['purchase:create', 'transport:approve']
  const menuPermissions = ref(null) // 菜单可见性配置

  // 登录
  async function login(credentials) {
    try {
      const response = await axios.post('/auth/login', credentials)
      if (response.data.code === 200) {
        const data = response.data.data
        user.value = data
        isLoggedIn.value = true
        permissions.value = data.permissions || []
        menuPermissions.value = data.menu_permissions || null
        return { success: true, data }
      } else {
        return { success: false, message: response.data.message }
      }
    } catch (error) {
      return { success: false, message: error.response?.data?.message || '登录失败' }
    }
  }

  // 登出
  async function logout() {
    try {
      await axios.post('/auth/logout')
    } catch (error) {
      console.error('登出失败', error)
    } finally {
      user.value = null
      isLoggedIn.value = false
      permissions.value = []
      menuPermissions.value = null
    }
  }

  // 检查登录状态
  async function checkAuth() {
    try {
      const response = await axios.get('/auth/me')
      if (response.data.code === 200) {
        const data = response.data.data
        user.value = data
        isLoggedIn.value = true
        permissions.value = data.permissions || []
        menuPermissions.value = data.menu_permissions || null
        return true
      }
    } catch (error) {
      user.value = null
      isLoggedIn.value = false
      permissions.value = []
      menuPermissions.value = null
      return false
    }
  }

  // 是否为教师/管理员
  const isTeacher = computed(() => {
    return user.value && SUPER_ROLES.includes(user.value.role_code)
  })

  // 检查当前用户是否拥有指定角色中的任一角色
  function hasRole(...roles) {
    const code = user.value?.role_code
    if (!code) return false
    if (SUPER_ROLES.includes(code)) return true
    return roles.includes(code)
  }

  // 检查是否拥有指定权限代码
  function hasPermission(permissionCode) {
    if (!user.value) return false
    if (SUPER_ROLES.includes(user.value.role_code)) return true
    return permissions.value.includes(permissionCode)
  }

  // 检查是否拥有任一指定权限
  function hasAnyPermission(...codes) {
    if (!user.value) return false
    if (SUPER_ROLES.includes(user.value.role_code)) return true
    return codes.some(code => permissions.value.includes(code))
  }

  return {
    user,
    isLoggedIn,
    isTeacher,
    permissions,
    menuPermissions,
    hasRole,
    hasPermission,
    hasAnyPermission,
    login,
    logout,
    checkAuth
  }
})
