<!-- 待推送数据预览弹窗 -->
<template>
  <el-dialog
    v-model="visible"
    title="待推送数据预览"
    width="900px"
    align-center
    append-to-body
    destroy-on-close
    @close="handleClose"
  >
    <div class="preview-header">
      <el-alert type="info" :closable="false" show-icon>
        <template #title>
          以下数据为尚未推送的记录（已排除历史已推送数据），共 <strong>{{ total }}</strong> 条
        </template>
      </el-alert>
    </div>

    <el-table
      v-loading="loading"
      :data="tableData"
      border
      stripe
      max-height="400"
      style="margin-top: 16px"
    >
      <template #empty>
        <el-empty :image-size="60" description="暂无待推送数据" />
      </template>

      <el-table-column type="index" label="序号" width="60" align="center">
        <template #default="scope">
          {{ (pageNo - 1) * pageSize + scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="mobile_phone" label="手机号码" min-width="130" />
      <el-table-column prop="staff_name" label="员工姓名" min-width="100" />
      <el-table-column prop="sys_name" label="系统名称" min-width="100" />
      <el-table-column prop="order_type" label="工单类型" min-width="100" />
      <el-table-column prop="order_nums" label="工单数量" width="100" align="center" />
    </el-table>

    <div class="preview-footer">
      <el-pagination
        v-model:current-page="pageNo"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import CallingTaskAPI, { type PreviewDataItem } from "@/api/module_calling/task";

defineOptions({
  name: "PreviewDataModal",
});

const props = defineProps<{
  modelValue: boolean;
  taskId?: number;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
}>();

const loading = ref(false);
const tableData = ref<PreviewDataItem[]>([]);
const total = ref(0);
const pageNo = ref(1);
const pageSize = ref(20);

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

watch(
  () => props.modelValue,
  (val) => {
    if (val && props.taskId) {
      pageNo.value = 1;
      loadData();
    }
  }
);

async function loadData() {
  if (!props.taskId) return;
  loading.value = true;
  try {
    const res = await CallingTaskAPI.previewData(props.taskId, pageNo.value, pageSize.value);
    tableData.value = res.data.data.items || [];
    total.value = res.data.data.total || 0;
  } catch (error) {
    console.error("加载预览数据失败", error);
  } finally {
    loading.value = false;
  }
}

function handleClose() {
  visible.value = false;
  tableData.value = [];
  total.value = 0;
}
</script>

<style scoped>
.preview-header {
  margin-bottom: 8px;
}

.preview-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
