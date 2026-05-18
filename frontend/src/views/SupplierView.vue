<template>
  <div class="supplier-view">
    <PageGuide v-bind="guideConfig" />
<el-card>
      <template #header>
        <div class="card-header">
          <span>供应商管理</span>
          <div class="card-header-actions">
            <el-button @click="handleDownloadTemplate">下载模板</el-button>
            <el-button type="success" @click="importDialogVisible = true">批量导入</el-button>
            <el-button type="primary" @click="showAddDialog">新增</el-button>
          </div>
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

    <!-- 批量导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="批量导入供应商" width="560px">
      <div v-if="!importResult">
        <el-upload
          drag
          :auto-upload="false"
          :limit="1"
          accept=".xlsx"
          :on-change="handleFileChange"
          :on-exceed="() => ElMessage.warning('只能上传一个文件')"
        >
          <el-icon style="font-size: 48px; color: #c0c4cc; margin-bottom: 8px;"><UploadFilled /></el-icon>
          <div>将 .xlsx 文件拖到此处，或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">仅支持 .xlsx 格式，请先下载模板填写数据</div>
          </template>
        </el-upload>
      </div>
      <div v-else>
        <el-alert
          :type="importResult.failed > 0 ? 'warning' : 'success'"
          :title="`导入完成：成功 ${importResult.success} 条`"
          :description="importResult.skipped > 0 || importResult.failed > 0 ? `跳过 ${importResult.skipped} 条，失败 ${importResult.failed} 条` : ''"
          show-icon
          :closable="false"
          style="margin-bottom: 16px;"
        />
        <el-table v-if="importResult.errors && importResult.errors.length" :data="importResult.errors" style="width: 100%" max-height="250">
          <el-table-column prop="row" label="行号" width="80" />
          <el-table-column prop="reason" label="原因" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false; importResult = null; importFile = null">
          {{ importResult ? '关闭' : '取消' }}
        </el-button>
        <el-button v-if="!importResult" type="primary" :loading="importLoading" :disabled="!importFile" @click="handleImport">
          开始导入
        </el-button>
        <el-button v-if="importResult && importResult.success > 0" type="primary" @click="importDialogVisible = false; importResult = null; importFile = null; loadData()">
          刷新列表
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import PageGuide from '../components/PageGuide.vue'

const guideConfig = { title: '供应商管理操作指引', steps: [
        "新建供应商，填写基本信息",
        "编辑或停用供应商"
    ], tips: [
        "供应商信息用于采购订单关联"
    ] }
import { ref, onMounted, onUnmounted } from 'vue'
import { supplierAPI, importAPI } from '../api/common'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

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

// 批量导入
const importDialogVisible = ref(false)
const importFile = ref(null)
const importLoading = ref(false)
const importResult = ref(null)

const handleDownloadTemplate = async () => {
  try {
    const res = await importAPI.downloadSuppliersTemplate()
    importAPI.downloadBlob(res, '供应商导入模板.xlsx')
  } catch (error) {
    ElMessage.error('下载模板失败')
  }
}

const handleFileChange = (uploadFile) => {
  importFile.value = uploadFile.raw
}

const handleImport = async () => {
  if (!importFile.value) return
  importLoading.value = true
  try {
    const res = await importAPI.importSuppliers(importFile.value)
    if (res.data.code === 200) {
      importResult.value = res.data.data
      if (res.data.data.failed === 0) {
        ElMessage.success(`成功导入 ${res.data.data.success} 条供应商`)
      }
    } else {
      ElMessage.error(res.data.message || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败，请检查文件格式')
  } finally {
    importLoading.value = false
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

.card-header-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .card-header-actions {
    flex-wrap: wrap;
  }
}
</style>
