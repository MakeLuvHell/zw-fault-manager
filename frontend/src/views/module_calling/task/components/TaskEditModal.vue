<!-- 外呼任务编辑弹窗 -->
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="dialogWidth"
    align-center
    append-to-body
    destroy-on-close
    class="task-edit-dialog"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-suffix=":"
      label-width="120px"
      label-position="right"
    >
      <!-- 基础配置 -->
      <el-divider content-position="left">
        <el-icon><Setting /></el-icon>
        基础配置
      </el-divider>

      <el-form-item label="任务名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入任务名称" maxlength="100" />
      </el-form-item>

      <el-form-item label="Cron 表达式" prop="cron_expr">
        <CronEditor v-model="formData.cron_expr" />
      </el-form-item>

      <el-form-item label="启用状态" prop="is_enabled">
        <el-switch v-model="formData.is_enabled" active-text="启用" inactive-text="停用" />
      </el-form-item>

      <!-- 数据源配置 -->
      <el-divider content-position="left">
        <el-icon><Grid /></el-icon>
        数据源配置
      </el-divider>

      <el-form-item label="源数据表" prop="source_schema" required>
        <el-space>
          <el-select
            v-model="formData.source_schema"
            placeholder="选择 Schema"
            style="width: 160px"
            filterable
            @change="handleSchemaChange"
          >
            <el-option
              v-for="item in schemaOptions"
              :key="item.schema_name"
              :label="item.schema_name"
              :value="item.schema_name"
            />
          </el-select>
          <span>.</span>
          <el-select
            v-model="formData.source_table"
            placeholder="选择表"
            style="width: 200px"
            filterable
            :disabled="!formData.source_schema"
            @change="handleTableChange"
          >
            <el-option
              v-for="item in tableOptions"
              :key="item.table_name"
              :label="item.table_comment ? `${item.table_name} (${item.table_comment})` : item.table_name"
              :value="item.table_name"
            />
          </el-select>
        </el-space>
      </el-form-item>

      <!-- 业务参数映射 -->
      <el-divider content-position="left">
        <el-icon><Link /></el-icon>
        业务参数映射
      </el-divider>

      <el-alert
        v-if="!formData.source_table"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      >
        请先选择源数据表，系统将自动加载表字段供映射选择
      </el-alert>

      <template v-else>
        <el-form-item label="手机号字段" prop="field_mapping.mobile_phone" required>
          <el-select
            v-model="formData.field_mapping.mobile_phone"
            placeholder="选择手机号对应的列"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in columnOptions"
              :key="item.column_name"
              :label="item.column_comment ? `${item.column_name} (${item.column_comment})` : item.column_name"
              :value="item.column_name"
            />
          </el-select>
          <div class="mapping-hint">→ 自动映射到 API 的 accs_nbr 和 contact_nbr</div>
        </el-form-item>

        <el-form-item label="员工姓名字段" prop="field_mapping.staff_name" required>
          <el-select
            v-model="formData.field_mapping.staff_name"
            placeholder="选择员工姓名对应的列"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in columnOptions"
              :key="item.column_name"
              :label="item.column_comment ? `${item.column_name} (${item.column_comment})` : item.column_name"
              :value="item.column_name"
            />
          </el-select>
          <div class="mapping-hint">→ 自动映射到 API 的 cust_name 和 staff_name</div>
        </el-form-item>

        <el-form-item label="系统名称字段" prop="field_mapping.sys_name" required>
          <el-select
            v-model="formData.field_mapping.sys_name"
            placeholder="选择系统名称对应的列"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in columnOptions"
              :key="item.column_name"
              :label="item.column_comment ? `${item.column_name} (${item.column_comment})` : item.column_name"
              :value="item.column_name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="工单类型字段" prop="field_mapping.order_type" required>
          <el-select
            v-model="formData.field_mapping.order_type"
            placeholder="选择工单类型对应的列"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in columnOptions"
              :key="item.column_name"
              :label="item.column_comment ? `${item.column_name} (${item.column_comment})` : item.column_name"
              :value="item.column_name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="工单数量字段" prop="field_mapping.order_nums" required>
          <el-select
            v-model="formData.field_mapping.order_nums"
            placeholder="选择工单数量对应的列"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in columnOptions"
              :key="item.column_name"
              :label="item.column_comment ? `${item.column_name} (${item.column_comment})` : item.column_name"
              :value="item.column_name"
            />
          </el-select>
        </el-form-item>
      </template>

      <!-- 备注 -->
      <el-divider content-position="left">
        <el-icon><Document /></el-icon>
        备注信息
      </el-divider>

      <el-form-item label="备注" prop="remark">
        <el-input
          v-model="formData.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import { Setting, Grid, Link, Document } from "@element-plus/icons-vue";
import { useAppStore } from "@/store/modules/app.store";
import { DeviceEnum } from "@/enums/settings/device.enum";
import CallingTaskAPI, {
  MetadataAPI,
  type CallingTaskForm,
  type CallingTaskInfo,
  type SchemaInfo,
  type TableInfo,
  type ColumnInfo,
} from "@/api/module_calling/task";
import CronEditor from "./CronEditor.vue";

defineOptions({
  name: "TaskEditModal",
});

const props = defineProps<{
  modelValue: boolean;
  taskId?: number;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "success"): void;
}>();

const appStore = useAppStore();
const formRef = ref();
const submitLoading = ref(false);

// 响应式对话框宽度
const dialogWidth = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "700px" : "90%"));

// 弹窗可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

// 弹窗标题
const title = computed(() => (props.taskId ? "编辑外呼任务" : "新增外呼任务"));

// 表单数据
const formData = reactive<CallingTaskForm>({
  name: "",
  cron_expr: "",
  source_schema: "",
  source_table: "",
  is_enabled: true,
  remark: "",
  field_mapping: {
    mobile_phone: "",
    staff_name: "",
    sys_name: "",
    order_type: "",
    order_nums: "",
  },
});

// 下拉选项
const schemaOptions = ref<SchemaInfo[]>([]);
const tableOptions = ref<TableInfo[]>([]);
const columnOptions = ref<ColumnInfo[]>([]);

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入任务名称", trigger: "blur" }],
  cron_expr: [{ required: true, message: "请输入 Cron 表达式", trigger: "blur" }],
  source_schema: [{ required: true, message: "请选择 Schema", trigger: "change" }],
  source_table: [{ required: true, message: "请选择数据表", trigger: "change" }],
  "field_mapping.mobile_phone": [{ required: true, message: "请选择手机号字段", trigger: "change" }],
  "field_mapping.staff_name": [{ required: true, message: "请选择员工姓名字段", trigger: "change" }],
  "field_mapping.sys_name": [{ required: true, message: "请选择系统名称字段", trigger: "change" }],
  "field_mapping.order_type": [{ required: true, message: "请选择工单类型字段", trigger: "change" }],
  "field_mapping.order_nums": [{ required: true, message: "请选择工单数量字段", trigger: "change" }],
});

// 监听弹窗打开
watch(
  () => props.modelValue,
  async (val) => {
    if (val) {
      await loadSchemas();
      if (props.taskId) {
        await loadTaskDetail();
      } else {
        resetForm();
      }
    }
  }
);

// 加载 Schema 列表
async function loadSchemas() {
  try {
    const res = await MetadataAPI.getSchemas();
    schemaOptions.value = res.data.data || [];
  } catch (error) {
    console.error("加载 Schema 列表失败", error);
  }
}

// 加载任务详情
async function loadTaskDetail() {
  if (!props.taskId) return;
  try {
    const res = await CallingTaskAPI.detailTask(props.taskId);
    const data = res.data.data;
    Object.assign(formData, {
      name: data.name,
      cron_expr: data.cron_expr,
      source_schema: data.source_schema,
      source_table: data.source_table,
      is_enabled: data.is_enabled,
      remark: data.remark || "",
      field_mapping: { ...data.field_mapping },
    });
    // 加载表和列
    if (data.source_schema) {
      await loadTables(data.source_schema);
    }
    if (data.source_schema && data.source_table) {
      await loadColumns(data.source_schema, data.source_table);
    }
  } catch (error) {
    console.error("加载任务详情失败", error);
    ElMessage.error("加载任务详情失败");
  }
}

// Schema 变更
async function handleSchemaChange(schema: string) {
  formData.source_table = "";
  formData.field_mapping = {
    mobile_phone: "",
    staff_name: "",
    sys_name: "",
    order_type: "",
    order_nums: "",
  };
  tableOptions.value = [];
  columnOptions.value = [];
  if (schema) {
    await loadTables(schema);
  }
}

// 表变更
async function handleTableChange(table: string) {
  formData.field_mapping = {
    mobile_phone: "",
    staff_name: "",
    sys_name: "",
    order_type: "",
    order_nums: "",
  };
  columnOptions.value = [];
  if (table && formData.source_schema) {
    await loadColumns(formData.source_schema, table);
  }
}

// 加载表列表
async function loadTables(schema: string) {
  try {
    const res = await MetadataAPI.getTables(schema);
    tableOptions.value = res.data.data || [];
  } catch (error) {
    console.error("加载表列表失败", error);
  }
}

// 加载列列表
async function loadColumns(schema: string, table: string) {
  try {
    const res = await MetadataAPI.getColumns(schema, table);
    columnOptions.value = res.data.data || [];
  } catch (error) {
    console.error("加载列列表失败", error);
  }
}

// 重置表单
function resetForm() {
  Object.assign(formData, {
    name: "",
    cron_expr: "",
    source_schema: "",
    source_table: "",
    is_enabled: true,
    remark: "",
    field_mapping: {
      mobile_phone: "",
      staff_name: "",
      sys_name: "",
      order_type: "",
      order_nums: "",
    },
  });
  tableOptions.value = [];
  columnOptions.value = [];
  formRef.value?.clearValidate();
}

// 关闭弹窗
function handleClose() {
  visible.value = false;
  resetForm();
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value?.validate();
    submitLoading.value = true;

    if (props.taskId) {
      await CallingTaskAPI.updateTask(props.taskId, formData);
      ElMessage.success("更新任务成功");
    } else {
      await CallingTaskAPI.createTask(formData);
      ElMessage.success("创建任务成功");
    }

    emit("success");
    handleClose();
  } catch (error) {
    console.error("提交失败", error);
  } finally {
    submitLoading.value = false;
  }
}
</script>

<style scoped>
.mapping-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
</style>

<style>
/* 任务编辑对话框样式 - 禁用滚动，一页显示 */
.task-edit-dialog .el-dialog__body {
  max-height: none;
  overflow: visible;
  padding-top: 10px;
  padding-bottom: 10px;
}

.task-edit-dialog .el-divider {
  margin: 12px 0;
}

.task-edit-dialog .el-form-item {
  margin-bottom: 12px;
}
</style>

