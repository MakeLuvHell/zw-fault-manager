<template>
  <div class="app-container">
    <div class="search-container">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="报表名称">
          <el-input v-model="queryParams.report_name" placeholder="请输入报表名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button type="success" @click="handleAdd">新增</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-card>
      <el-table v-loading="loading" :data="tableData" border>
        <el-table-column label="ID" prop="id" width="80" />
        <el-table-column label="报表名称" prop="report_name" />
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '0' ? 'success' : 'info'">
              {{ row.status === "0" ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" prop="description" />
        <el-table-column label="更新时间" prop="updated_time" width="180">
          <template #default="{ row }">
            {{ formatToDateTime(row.updated_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleConfig(row)">配置下钻</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page_no"
          v-model:page-size="queryParams.page_size"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </el-card>

    <!-- Base Info Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @close="resetForm">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="报表名称" prop="report_name">
          <el-input v-model="formData.report_name" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="0">启用</el-radio>
            <el-radio label="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input v-model="formData.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- Config Dialog -->
    <el-dialog
      v-model="configVisible"
      title="下钻配置"
      width="80%"
      top="5vh"
      :close-on-click-modal="false"
    >
      <DrillConfigTree v-if="configVisible" :info-id="currentId" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import API, { PxmDataDrillInfo } from "@/api/module_datadrill/data_drill_info";
import DrillConfigTree from "./components/DrillConfigTree.vue";
import { formatToDateTime } from "@/utils/dateUtil";

const loading = ref(false);
const tableData = ref<PxmDataDrillInfo[]>([]);
const total = ref(0);
const queryParams = reactive({
  page_no: 1,
  page_size: 10,
  report_name: "",
});

const dialogVisible = ref(false);
const dialogTitle = ref("");
const formRef = ref();
const formData = reactive<PxmDataDrillInfo>({
  status: "0",
});

const configVisible = ref(false);
const currentId = ref<number>(0);

const rules = {
  report_name: [{ required: true, message: "请输入报表名称", trigger: "blur" }],
};

onMounted(() => {
  handleQuery();
});

async function handleQuery() {
  loading.value = true;
  try {
    const res = await API.list(queryParams);
    tableData.value = res.data.data.items;
    total.value = res.data.data.total;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function handleAdd() {
  dialogTitle.value = "新增报表";
  Object.assign(formData, { id: undefined, report_name: "", status: "0", description: "" });
  dialogVisible.value = true;
}

function handleEdit(row: PxmDataDrillInfo) {
  dialogTitle.value = "编辑报表";
  Object.assign(formData, row);
  dialogVisible.value = true;
}

async function handleDelete(row: PxmDataDrillInfo) {
  ElMessageBox.confirm("确认删除该报表?", "警告", { type: "warning" }).then(async () => {
    if (row.id) {
      await API.delete([row.id]);
      ElMessage.success("删除成功");
      handleQuery();
    }
  });
}

async function submitForm() {
  formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (formData.id) {
          await API.update(formData.id, formData);
        } else {
          await API.create(formData);
        }
        ElMessage.success("保存成功");
        dialogVisible.value = false;
        handleQuery();
      } catch (e) {
        console.error(e);
      }
    }
  });
}

function resetForm() {
  formRef.value?.resetFields();
}

function handleConfig(row: PxmDataDrillInfo) {
  if (row.id) {
    currentId.value = row.id;
    configVisible.value = true;
  }
}
</script>

<style scoped>
.pagination-container {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}
</style>
