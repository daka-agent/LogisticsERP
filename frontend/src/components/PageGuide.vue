<template>
  <div class="page-guide" v-if="!collapsed || showContent">
    <el-alert
      :title="title"
      type="info"
      :closable="true"
      @close="collapse"
      show-icon
      :description="collapsed ? undefined : ''"
    >
      <template v-if="showContent">
        <!-- 操作步骤 -->
        <div class="guide-section" v-if="steps && steps.length">
          <div class="guide-label">操作步骤</div>
          <div class="guide-steps">
            <div class="guide-step" v-for="(step, i) in steps" :key="i">
              <span class="step-num">{{ i + 1 }}</span>
              <span class="step-text">{{ step }}</span>
              <span v-if="i < steps.length - 1" class="step-arrow">→</span>
            </div>
          </div>
        </div>
        <!-- 注意事项 -->
        <div class="guide-section" v-if="tips && tips.length">
          <div class="guide-label">注意事项</div>
          <ul class="guide-tips">
            <li v-for="(tip, i) in tips" :key="i">{{ tip }}</li>
          </ul>
        </div>
        <!-- 展开按钮（已收起状态） -->
        <div class="guide-expand" v-if="!collapsed">
          <el-button text size="small" @click="collapse">收起提示</el-button>
        </div>
      </template>
      <template v-if="collapsed">
        <el-button text size="small" type="primary" @click="expand">展开操作提示</el-button>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  title: { type: String, default: '操作指引' },
  steps: { type: Array, default: () => [] },
  tips: { type: Array, default: () => [] },
})

const route = useRoute()
const storageKey = computed(() => `guide_collapsed_${route.path}`)

const collapsed = ref(localStorage.getItem(storageKey.value) === 'true')

const showContent = computed(() => !collapsed.value)

function collapse() {
  collapsed.value = true
  localStorage.setItem(storageKey.value, 'true')
}

function expand() {
  collapsed.value = false
  localStorage.setItem(storageKey.value, 'false')
}
</script>

<style scoped>
.page-guide {
  margin-bottom: 16px;
}

.guide-section {
  margin-top: 8px;
}

.guide-label {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.guide-steps {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.guide-step {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #409EFF;
  color: white;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.step-arrow {
  color: #909399;
  margin: 0 2px;
  font-size: 12px;
}

.step-text {
  white-space: nowrap;
}

.guide-tips {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #606266;
}

.guide-tips li {
  line-height: 1.8;
}

.guide-expand {
  margin-top: 8px;
  text-align: right;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .guide-steps {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .step-arrow {
    display: none;
  }

  .guide-step {
    gap: 6px;
  }

  .step-text {
    white-space: normal;
  }
}

/* 覆盖 el-alert 在收起态的样式 */
.page-guide :deep(.el-alert__description) {
  margin: 0;
}
</style>
