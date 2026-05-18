import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const SUPER_ROLES = ['admin', 'teacher']

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const menuPermissions = ref(null)

  // 登录
  async function login(credentials) {
    try {
      const response = await axios.post('/auth/login', credentials)
      if (response.data.code === 200) {
        user.value = response.data.data
        isLoggedIn.value = true
        // 登录成功后获取菜单权限
        _initMenuPermissions()
        return { success: true, data: response.data.data }
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
      menuPermissions.value = null
    }
  }

  // 检查登录状态
  async function checkAuth() {
    try {
      const response = await axios.get('/auth/me')
      if (response.data.code === 200) {
        user.value = response.data.data
        isLoggedIn.value = true
        _initMenuPermissions()
        return true
      }
    } catch (error) {
      user.value = null
      isLoggedIn.value = false
      menuPermissions.value = null
      return false
    }
  }

  // 是否为教师/管理员
  const isTeacher = computed(() => {
    return user.value && SUPER_ROLES.includes(user.value.role_code)
  })

  // 检查当前用户是否拥有指定角色中的任一角色
  function hasPermission(...roles) {
    const code = user.value?.role_code
    if (!code) return false
    if (SUPER_ROLES.includes(code)) return true
    return roles.includes(code)
  }

  // 初始化菜单权限
  function _initMenuPermissions() {
    const code = user.value?.role_code
    if (!code) {
      menuPermissions.value = null
      return
    }

    const isSuper = SUPER_ROLES.includes(code)
    const isStudent = code === 'student'

    if (isSuper || isStudent) {
      menuPermissions.value = {
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
    } else {
      menuPermissions.value = {
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
  }

  return {
    user,
    isLoggedIn,
    isTeacher,
    menuPermissions,
    hasPermission,
    login,
    logout,
    checkAuth
  }
})
