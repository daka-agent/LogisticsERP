<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <img src="/logo.png" alt="大卡" class="logo-img" />
          <h2>大卡@物流系统模拟仿真</h2>
          <p>用户登录</p>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="loginForm" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="demo-account">
        <p>演示账号：admin / admin123</p>
      </div>

    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loginForm = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  await loginForm.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      const result = await authStore.login(form)
      loading.value = false

      if (result.success) {
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        ElMessage.error(result.message)
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 90%;
  max-width: 450px;
}

.card-header {
  text-align: center;
}

.logo-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 15px;
  object-fit: cover;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.card-header p {
  margin: 10px 0 0;
  color: #909399;
  font-size: 14px;
}

.demo-account {
  margin-top: 15px;
  padding: 10px;
  background-color: #f4f4f5;
  border-radius: 4px;
  text-align: center;
  font-size: 13px;
  color: #909399;
}

</style>
