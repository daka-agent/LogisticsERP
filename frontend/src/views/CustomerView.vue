<template>
  <div class="customer-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>客户管理</span>
          <el-button type="primary" @click="showAddDialog">新增客户</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="客户名称">
          <el-input v-model="keyword" placeholder="请输入客户名称" clearable />
        </el-form-item>
        <el-form-item label="客户等级">
          <el-select v-model="levelFilter" placeholder="全部" clearable>
            <el-option label="VIP" value="vip" />
            <el-option label="普通" value="normal" />
            <el-option label="潜在" value="potential" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="customerList" style="width: 100%">
        <el-table-column prop="customer_no" label="客户编号" width="140" />
        <el-table-column prop="name" label="客户名称" />
        <el-table-column prop="level" label="等级" width="100">
          <template #default="scope">
            <el-tag :type="getLevelType(scope.row.level)">
              {{ getLevelText(scope.row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="settlement_type" label="结算方式" width="100">
          <template #default="scope">
            {{ getSettlementText(scope.row.settlement_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="credit_limit" label="信用额度" width="100">
          <template #default="scope">
            {{ scope.row.credit_limit ? '¥' + scope.row.credit_limit : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '新增客户' : '编辑客户'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="客户名称" required>
          <el-input v-model="form.name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="客户等级">
          <el-select v-model="form.level" placeholder="请选择">
            <el-option label="VIP" value="vip" />
            <el-option label="普通" value="normal" />
            <el-option label="潜在" value="potential" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_person" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="结算方式">
          <el-select v-model="form.settlement_type" placeholder="请选择">
            <el-option label="月结" value="monthly" />
            <el-option label="现结" value="spot" />
            <el-option label="信用" value="credit" />
          </el-select>
        </el-form-item>
        <el-form-item label="信用额度">
          <el-input-number v-model="form.credit_limit" :min="0" :precision="2" :step="1000" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { customerAPI } from '../api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const customerList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('add')
const currentId = ref(null)
const keyword = ref('')
const levelFilter = ref('')

const defaultForm = {
  name: '',
  level: 'normal',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  settlement_type: '',
  credit_limit: 0.0
}
const form = ref({ ...defaultForm })

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const loadData = async () => {
  try {
    const params = {}
    if (keyword.value) params.keyword = keyword.value
    if (levelFilter.value) params.level = levelFilter.value

    const res = await customerAPI.list(params)
    if (res.data.code === 200) {
      customerList.value = res.data.data
    }
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const showAddDialog = () => {
  dialogType.value = 'add'
  form.value = { ...defaultForm }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  dialogType.value = 'edit'
  currentId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name) {
    ElMessage.warning('客户名称不能为空')
    return
  }
  try {
    let res
    if (dialogType.value === 'add') {
      res = await customerAPI.create(form.value)
    } else {
      res = await customerAPI.update(currentId.value, form.value)
    }
    if (res.data.code === 200) {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      loadData()
    }
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该客户吗？', '提示', { type: 'warning' })
    const res = await customerAPI.delete(row.id)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getLevelType = (level) => {
  const map = { vip: 'warning', normal: '', potential: 'info' }
  return map[level] || ''
}

const getLevelText = (level) => {
  const map = { vip: 'VIP', normal: '普通', potential: '潜在' }
  return map[level] || level
}

const getSettlementText = (type) => {
  const map = { monthly: '月结', spot: '现结', credit: '信用' }
  return map[type] || '-'
}

onMounted(() => {
  checkWidth()
  window.addEventListener('resize', checkWidth)
  loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWidth)
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .search-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
}
</style>
