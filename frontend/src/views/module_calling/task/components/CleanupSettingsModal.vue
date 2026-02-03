<!-- 历史记录清理设置弹窗 -->
<template>
  <el-dialog
    v-model="visible"
    title="历史记录清理设置"
    width="500px"
    align-center
    append-to-body
    destroy-on-close
    @close="handleClose"
  >
    <el-alert
      title="清空历史记录后，第二天执行任务时将不再过滤已推送过的号码。"
      type="warning"
      show-icon
      :closable="false"
      class="mb-4"
    />

    <el-form ref="formRef" :model="formData" label-width="120px" class="mt-4">
      <el-form-item label="自动清理">
        <el-switch v-model="formData.is_enabled" active-text="开启" inactive-text="关闭" />
      </el-form-item>

      <el-form-item label="清理时间" v-if="formData.is_enabled">
        <el-input v-model="formData.cron_expr" placeholder="请输入 Cron 表达式" />
        <div class="cron-hint">
          默认: <code>0 0 0 * * *</code> (每天凌晨0点)
        </div>
      </el-form-item>
    </el-form>

    <div class="manual-cleanup-section">
      <el-divider content-position="left">手动操作</el-divider>
      <div class="flex justify-between items-center">
        <span class="text-gray-500 text-sm">立即清空所有历史记录，慎点！</span>
        <el-popconfirm
          title="确定要立即清空所有历史记录吗？数据不可恢复！"
          confirm-button-text="确认清空"
          cancel-button-text="取消"
          confirm-button-type="danger"
          @confirm="handleManualCleanup"
        >
          <template #reference>
            <el-button type="danger" plain size="small" :loading="cleanupLoading">
              立即清理
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
        保存配置
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import { CleanupAPI, type CleanupConfig } from "@/api/module_calling/task";

defineOptions({
  name: "CleanupSettingsModal",
});

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
}>();

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const submitLoading = ref(false);
const cleanupLoading = ref(false);
const formData = ref<CleanupConfig>({
  is_enabled: false,
  cron_expr: "0 0 0 * * *",
});

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      loadConfig();
    }
  }
);

async function loadConfig() {
  try {
    const res = await CleanupAPI.getConfig();
    formData.value = res.data.data;
  } catch (error) {
    console.error("加载清理配置失败", error);
  }
}

async function handleSubmit() {
  submitLoading.value = true;
  try {
    await CleanupAPI.setConfig(formData.value);
    ElMessage.success("清理配置已保存");
    handleClose();
  } finally {
    submitLoading.value = false;
  }
}

async function handleManualCleanup() {
  cleanupLoading.value = true;
  try {
    await CleanupAPI.executeCleanup();
    ElMessage.success("已触发清理任务，请稍后查看日志");
  } finally {
    cleanupLoading.value = false;
  }
}

function handleClose() {
  visible.value = false;
}
</script>

<style scoped>
.cron-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
.manual-cleanup-section {
  margin-top: 24px;
  padding: 0 12px;
}
.mb-4 {
  margin-bottom: 16px;
}
.mt-4 {
  margin-top: 16px;
}
</style>
