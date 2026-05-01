<template>
  <div class="goods-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="showAddDialog">新增商品</el-button>
        </div>
      </template>

      <el-table :data="goodsList" style="width: 100%">
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="spec" label="规格" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="min_stock" label="最低库存" width="100" />
        <el-table-column prop="max_stock" label="最高库存" width="100" />
        <el-table-column label="采购价" width="100">
          <template #default="scope">
            {{ scope.row.purchase_price ? '¥' + scope.row.purchase_price : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="销售价" width="100">
          <template #default="scope">
            {{ scope.row.selling_price ? '¥' + scope.row.selling_price : '-' }}
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
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '新增商品' : '编辑商品'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="SKU" required>
          <el-input v-model="form.sku" placeholder="请输入SKU编码" />
        </el-form-item>
        <el-form-item label="商品名称" required>
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="规格">
          <el-input v-model="form.spec" placeholder="如：500g/瓶" />
        </el-form-item>
        <el-form-item label="单位">
          <el-select v-model="form.unit" placeholder="请选择">
            <el-option label="个" value="个" />
            <el-option label="箱" value="箱" />
            <el-option label="吨" value="吨" />
            <el-option label="立方米" value="立方米" />
            <el-option label="千克" value="千克" />
            <el-option label="件" value="件" />
          </el-select>
        </el-form-item>
        <el-form-item label="最低库存">
          <el-input-number v-model="form.min_stock" :min="0" />
        </el-form-item>
        <el-form-item label="最高库存">
          <el-input-number v-model="form.max_stock" :min="0" />
        </el-form-item>
        <el-form-item label="采购价">
          <el-input-number v-model="form.purchase_price" :min="0" :precision="2" :step="0.1" />
        </el-form-item>
        <el-form-item label="销售价">
          <el-input-number v-model="form.selling_price" :min="0" :precision="2" :step="0.1" />
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
import { goodsAPI } from '../api/common'
import { ElMessage, ElMessageBox } from 'element-plus'

const goodsList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('add')
const currentId = ref(null)
const defaultForm = {
  sku: '',
  name: '',
  spec: '',
  unit: '个',
  min_stock: 0,
  max_stock: 99999,
  purchase_price: null,
  selling_price: null
}
const form = ref({ ...defaultForm })

const isMobile = ref(false)
const checkWidth = () => { isMobile.value = window.innerWidth < 768 }

const loadData = async () => {
  try {
    const res = await goodsAPI.list()
    if (res.data.code === 200) {
      goodsList.value = res.data.data
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
  if (!form.value.sku || !form.value.name) {
    ElMessage.warning('SKU和商品名称不能为空')
    return
  }
  try {
    let res
    if (dialogType.value === 'add') {
      res = await goodsAPI.create(form.value)
    } else {
      res = await goodsAPI.update(currentId.value, form.value)
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
    await ElMessageBox.confirm('确定删除该商品吗？', '提示', { type: 'warning' })
    const res = await goodsAPI.delete(row.id)
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

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
