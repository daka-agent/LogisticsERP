import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)

  // 登录
  async function login(credentials) {
    try {
      const response = await axios.post('/auth/login', credentials)
      if (response.data.code === 200) {
        user.value = response.data.data
        isLoggedIn.value = true
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
    }
  }

  // 检查登录状态
  async function checkAuth() {
    try {
      const response = await axios.get('/auth/me')
      if (response.data.code === 200) {
        user.value = response.data.data
        isLoggedIn.value = true
        return true
      }
    } catch (error) {
      user.value = null
      isLoggedIn.value = false
      return false
    }
  }

  // 是否为教师（admin 或 teacher 角色）
  const isTeacher = computed(() => {
    return user.value && ['admin', 'teacher'].includes(user.value.role_code)
  })

  return {
    user,
    isLoggedIn,
    isTeacher,
    login,
    logout,
    checkAuth
  }
})
