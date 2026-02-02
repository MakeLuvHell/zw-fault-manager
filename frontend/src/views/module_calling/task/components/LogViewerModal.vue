<!-- 外呼执行日志弹窗 -->
<template>
  <el-dialog
    v-model="visible"
    title="执行日志"
    width="900px"
    append-to-body
    destroy-on-close
    @open="loadLogs"
  >
    <div class="log-container">
      <el-table
        v-loading="loading"
        :data="logData"
        height="400"
        border
        stripe
      >
        <template #empty>
          <el-empty :image-size="60" description="暂无执行日志" />
        </template>

        <el-table-column prop="push_time" label="推送时间" width="170" />
        <el-table-column prop="mobile_phone" label="手机号" width="130" />
        <el-table-column prop="staff_name" label="员工姓名" width="100" />
        <el-table-column prop="sys_name" label="系统名称" width="100" show-overflow-tooltip />
        <el-table-column prop="order_type" label="工单类型" width="80" />
        <el-table-column prop="order_nums" label="工单数" width="70" align="center" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 1 ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_msg" label="错误信息" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.error_msg" class="error-msg">{{ scope.row.error_msg }}</span>
            <span v-else class="no-error">-</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 统计信息 -->
      <div class="log-stats" v-if="logData.length > 0">
        <span>共 {{ logData.length }} 条记录</span>
        <span class="stat-item success">成功: {{ successCount }}</span>
        <span class="stat-item fail">失败: {{ failCount }}</span>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="loadLogs" :loading="loading" icon="Refresh">
          刷新
        </el-button>
        <el-button @click="visible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import CallingTaskAPI, { type CallLogInfo } from "@/api/module_calling/task";

defineOptions({
  name: "LogViewerModal",
});

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
}>();

const loading = ref(false);
const logData = ref<CallLogInfo[]>([]);

// 弹窗可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

// 统计
const successCount = computed(() => logData.value.filter((log) => log.status === 1).length);
const failCount = computed(() => logData.value.filter((log) => log.status === 0).length);

// 加载日志
async function loadLogs() {
  loading.value = true;
  try {
    const res = await CallingTaskAPI.getLogs(200);
    logData.value = res.data.data || [];
  } catch (error) {
    console.error("加载日志失败", error);
    ElMessage.error("加载日志失败");
  } finally {
    loading.value = false;
  }
}

// 监听弹窗打开
watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      loadLogs();
    }
  }
);
</script>

<style scoped>
.log-container {
  min-height: 200px;
}

.log-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
  padding: 8px 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  font-size: 14px;
}

.stat-item {
  font-weight: 500;
}

.stat-item.success {
  color: var(--el-color-success);
}

.stat-item.fail {
  color: var(--el-color-danger);
}

.error-msg {
  color: var(--el-color-danger);
}

.no-error {
  color: var(--el-text-color-placeholder);
}
</style>
