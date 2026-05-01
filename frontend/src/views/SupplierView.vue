<template>
  <div class="supplier-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>供应商管理</span>
          <el-button type="primary" @click="showAddDialog">新增</el-button>
        </div>
      </template>

      <el-table :data="supplierList" style="width: 100%">
        <el-table-column prop="name" label="供应商名称" />
        <el-table-column prop="contact" label="联系人" />
        <el-table-column prop="phone" label="联系电话" />
        <el-table-column prop="address" label="地址" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '新增供应商' : '编辑供应商'">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" type="textarea" />
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
import { supplierAPI } from '../api/common'
import { ElMessage, ElMessageBox } from 'element-plus'

const supplierList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('add')  // add 或 edit
const currentId = ref(null)
const form = ref({
  name: '',
  contact: '',
  phone: '',
  address: ''
})

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

// 加载列表
const loadData = async () => {
  try {
    const res = await supplierAPI.list()
    if (res.data.code === 200) {
      supplierList.value = res.data.data
    }
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

// 显示新增对话框
const showAddDialog = () => {
  dialogType.value = 'add'
  form.value = { name: '', contact: '', phone: '', address: '' }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogType.value = 'edit'
  currentId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

// 保存
const handleSave = async () => {
  try {
    let res
    if (dialogType.value === 'add') {
      res = await supplierAPI.create(form.value)
    } else {
      res = await supplierAPI.update(currentId.value, form.value)
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

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该供应商吗？', '提示', { type: 'warning' })
    const res = await supplierAPI.delete(row.id)
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

onMounted(() => {
  checkWidth();
  window.addEventListener('resize', checkWidth);
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

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
