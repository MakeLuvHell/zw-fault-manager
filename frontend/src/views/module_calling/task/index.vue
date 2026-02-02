<!-- 外呼任务管理 -->
<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <div class="search-container">
      <el-form
        ref="queryFormRef"
        :model="queryFormData"
        :inline="true"
        label-suffix=":"
        @submit.prevent="handleQuery"
      >
        <el-form-item prop="name" label="任务名称">
          <el-input v-model="queryFormData.name" placeholder="请输入任务名称" clearable />
        </el-form-item>
        <el-form-item prop="source_table" label="源数据表">
          <el-input v-model="queryFormData.source_table" placeholder="请输入表名" clearable />
        </el-form-item>
        <el-form-item prop="is_enabled" label="状态">
          <el-select
            v-model="queryFormData.is_enabled"
            placeholder="请选择状态"
            style="width: 120px"
            clearable
          >
            <el-option label="启用" :value="true" />
            <el-option label="停用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item class="search-buttons">
          <el-button
            v-hasPerm="['module_calling:task:query']"
            type="primary"
            icon="search"
            native-type="submit"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['module_calling:task:query']"
            icon="refresh"
            @click="handleResetQuery"
          >
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格卡片 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            <el-tooltip content="管理外呼任务的调度配置和字段映射">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
            外呼任务列表
          </span>
        </div>
      </template>

      <!-- 工具栏 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_calling:task:create']"
                type="success"
                icon="plus"
                @click="handleOpenModal()"
              >
                新增任务
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_calling:task:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
          </el-row>
        </div>

        <div class="data-table__toolbar--right">
          <el-tooltip content="执行日志">
            <el-button
              v-hasPerm="['module_calling:task:query']"
              type="primary"
              icon="Document"
              @click="handleOpenLogModal"
            >
              执行日志
            </el-button>
          </el-tooltip>
          <el-tooltip content="刷新">
            <el-button
              v-hasPerm="['module_calling:task:query']"
              type="default"
              icon="refresh"
              circle
              @click="loadData"
            />
          </el-tooltip>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="tableData"
        highlight-current-row
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <template #empty>
          <el-empty :image-size="80" description="暂无数据" />
        </template>

        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center">
          <template #default="scope">
            {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
          </template>
        </el-table-column>

        <el-table-column prop="name" label="任务名称" min-width="150" show-overflow-tooltip />

        <el-table-column prop="cron_expr" label="Cron 表达式" min-width="140" show-overflow-tooltip>
          <template #default="scope">
            <el-tag type="info" size="small">{{ scope.row.cron_expr }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="源数据表" min-width="200" show-overflow-tooltip>
          <template #default="scope">
            <span class="source-table">
              {{ scope.row.source_schema }}.{{ scope.row.source_table }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="is_enabled" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_enabled ? 'success' : 'danger'">
              {{ scope.row.is_enabled ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />

        <el-table-column prop="updated_time" label="更新时间" width="180" />

        <el-table-column fixed="right" label="操作" width="280" align="center">
          <template #default="scope">
            <el-button
              v-hasPerm="['module_calling:task:execute']"
              type="success"
              size="small"
              link
              icon="VideoPlay"
              :disabled="!scope.row.is_enabled"
              @click="handleExecute(scope.row)"
            >
              立即执行
            </el-button>
            <el-button
              v-hasPerm="['module_calling:task:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenModal(scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_calling:task:delete']"
              type="danger"
              size="small"
              link
              icon="delete"
              @click="handleDelete([scope.row.id])"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <template #footer>
        <pagination
          v-model:total="total"
          v-model:page="queryFormData.page_no"
          v-model:limit="queryFormData.page_size"
          @pagination="loadData"
        />
      </template>
    </el-card>

    <!-- 任务编辑弹窗 -->
    <TaskEditModal
      v-model="modalVisible"
      :task-id="editingTaskId"
      @success="handleModalSuccess"
    />

    <!-- 日志查看弹窗 -->
    <LogViewerModal v-model="logModalVisible" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { QuestionFilled } from "@element-plus/icons-vue";
import CallingTaskAPI, { type CallingTaskInfo, type CallingTaskQuery } from "@/api/module_calling/task";
import TaskEditModal from "./components/TaskEditModal.vue";
import LogViewerModal from "./components/LogViewerModal.vue";

defineOptions({
  name: "CallingTask",
  inheritAttrs: false,
});

const queryFormRef = ref();
const tableRef = ref();
const loading = ref(false);
const total = ref(0);
const tableData = ref<CallingTaskInfo[]>([]);
const selectIds = ref<number[]>([]);

// 弹窗状态
const modalVisible = ref(false);
const editingTaskId = ref<number | undefined>(undefined);
const logModalVisible = ref(false);

// 查询参数
const queryFormData = reactive<CallingTaskQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  source_table: undefined,
  is_enabled: undefined,
});

// 加载数据
async function loadData() {
  loading.value = true;
  try {
    const res = await CallingTaskAPI.listTask(queryFormData);
    tableData.value = res.data.data.items || [];
    total.value = res.data.data.total || 0;
  } catch (error) {
    console.error("加载任务列表失败", error);
  } finally {
    loading.value = false;
  }
}

// 查询
function handleQuery() {
  queryFormData.page_no = 1;
  loadData();
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  queryFormData.name = undefined;
  queryFormData.source_table = undefined;
  queryFormData.is_enabled = undefined;
  queryFormData.page_no = 1;
  loadData();
}

// 选择变更
function handleSelectionChange(selection: CallingTaskInfo[]) {
  selectIds.value = selection.map((item) => item.id);
}

// 打开弹窗
function handleOpenModal(taskId?: number) {
  editingTaskId.value = taskId;
  modalVisible.value = true;
}

// 弹窗成功回调
function handleModalSuccess() {
  loadData();
}

// 删除任务
async function handleDelete(ids: number[]) {
  if (ids.length === 0) return;

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${ids.length} 个任务吗？`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await CallingTaskAPI.deleteTask(ids);
    ElMessage.success("删除成功");
    loadData();
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("删除失败", error);
    }
  }
}

// 立即执行任务
async function handleExecute(row: CallingTaskInfo) {
  try {
    await ElMessageBox.confirm(
      `确定要立即执行任务 "${row.name}" 吗？任务将在后台异步执行。`,
      "执行确认",
      {
        confirmButtonText: "确定执行",
        cancelButtonText: "取消",
        type: "info",
      }
    );

    const res = await CallingTaskAPI.executeTask(row.id);
    ElMessage.success(res.data.msg || "任务已触发执行");
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("执行失败", error);
    }
  }
}

// 打开日志弹窗
function handleOpenLogModal() {
  logModalVisible.value = true;
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.source-table {
  font-family: monospace;
  color: var(--el-color-primary);
}

.data-table__toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.data-table__toolbar--left,
.data-table__toolbar--right {
  display: flex;
  align-items: center;
}

.card-header {
  display: flex;
  align-items: center;
}
</style>
