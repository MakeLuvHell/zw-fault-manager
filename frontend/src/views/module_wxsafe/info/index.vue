<template>
  <div class="app-container">
    <!-- 搜索栏 -->
    <el-card shadow="never" class="mb-4">
      <el-form :inline="true" :model="queryParams" ref="queryFormRef">
        <el-form-item label="线索编号" prop="clue_number">
          <el-input v-model="queryParams.clue_number" placeholder="请输入线索编号" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="业务号码" prop="phone_number">
          <el-input v-model="queryParams.phone_number" placeholder="请输入业务号码" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="search" @click="handleQuery">搜索</el-button>
          <el-button icon="refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card shadow="never">
      <template #header>
        <div class="flex justify-between items-center">
          <div class="flex gap-2">
            <el-button type="primary" icon="plus" @click="handleAdd">单条录入</el-button>
            <el-button type="success" icon="upload" @click="handleImport">批量导入</el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="dataList">
        <el-table-column label="线索编号" align="center" prop="clue_number" />
        <el-table-column label="涉诈或涉案" align="center" prop="category" />
        <el-table-column label="业务号码" align="center" prop="phone_number" />
        <el-table-column label="月份" align="center" prop="report_month" />
        <el-table-column label="涉诈涉案时间" align="center" prop="incident_time" width="180">
          <template #default="scope">
            <span>{{ scope.row.incident_time }}</span>
          </template>
        </el-table-column>
        <el-table-column label="涉诈涉案地" align="center" prop="city" />
        <el-table-column label="涉诈类型" align="center" prop="fraud_type" />
        <el-table-column label="受害人号码" align="center" prop="victim_number" show-overflow-tooltip />
      </el-table>

      <!-- 分页 -->
      <div class="flex justify-end mt-4">
        <el-pagination
          v-model:current-page="queryParams.page_no"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </el-card>

    <!-- 录入弹窗 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px" append-to-body>
      <el-form ref="dataFormRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="线索编号" prop="clue_number">
          <el-input v-model="formData.clue_number" placeholder="请输入线索编号" />
        </el-form-item>
        <el-form-item label="涉诈或涉案" prop="category">
          <el-select v-model="formData.category" placeholder="请选择">
            <el-option label="涉诈" value="涉诈" />
            <el-option label="涉案" value="涉案" />
          </el-select>
        </el-form-item>
        <el-form-item label="业务号码" prop="phone_number">
          <el-input v-model="formData.phone_number" placeholder="请输入11位业务号码" />
        </el-form-item>
        <el-form-item label="月份" prop="report_month">
          <el-input v-model="formData.report_month" placeholder="请输入月份" />
        </el-form-item>
        <el-form-item label="涉诈涉案时间" prop="incident_time">
          <el-date-picker
            v-model="formData.incident_time"
            type="datetime"
            placeholder="选择日期时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="涉诈涉案地" prop="city">
          <el-input v-model="formData.city" placeholder="请输入城市" />
        </el-form-item>
        <el-form-item label="涉诈类型" prop="fraud_type">
          <el-input v-model="formData.fraud_type" placeholder="请输入涉诈类型" />
        </el-form-item>
        <el-form-item label="受害人号码" prop="victim_number">
          <el-input v-model="formData.victim_number" type="textarea" placeholder="请输入受害人号码（多个用逗号隔开）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitForm">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入组件 -->
    <ImportModal
      v-model="importVisible"
      title="批量导入涉诈信息"
      :content-config="importConfig"
      @upload="handleUploadFile"
    />

    <!-- 导入结果明细弹窗 -->
    <el-dialog title="导入结果明细" v-model="resultVisible" width="800px">
      <div class="mb-4">
        <el-tag type="info">总数: {{ importResult.total }}</el-tag>
        <el-tag type="success" class="ml-2">成功: {{ importResult.success_count }}</el-tag>
        <el-tag type="danger" class="ml-2">失败: {{ importResult.fail_count }}</el-tag>
      </div>
      <el-table :data="importResult.details" max-height="400">
        <el-table-column label="线索编号" prop="clue_number" width="200" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="原因" prop="reason" />
      </el-table>
      <template #footer>
        <el-button type="primary" @click="resultVisible = false">关 闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { listWxSafeInfo, addWxSafeInfo, importWxSafeInfo, downloadWxSafeTemplate } from '@/api/module_wxsafe/info';
import ImportModal from '@/components/CURD/ImportModal.vue';

const loading = ref(false);
const total = ref(0);
const dataList = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const importVisible = ref(false);
const resultVisible = ref(false);

const queryParams = reactive({
  page_no: 1,
  page_size: 10,
  clue_number: '',
  phone_number: ''
});

const formData = reactive({
  clue_number: '',
  category: '涉诈',
  phone_number: '',
  report_month: '',
  incident_time: '',
  city: '',
  fraud_type: '',
  victim_number: ''
});

const formRules = {
  clue_number: [{ required: true, message: '请输入线索编号', trigger: 'blur' }],
  phone_number: [
    { required: true, message: '请输入业务号码', trigger: 'blur' },
    { pattern: /^\d{11}$/, message: '请输入11位数字号码', trigger: 'blur' }
  ]
};

const importResult = ref({
  total: 0,
  success_count: 0,
  fail_count: 0,
  details: []
});

const importConfig = {
  importTemplate: downloadWxSafeTemplate
};

async function getList() {
  loading.value = true;
  try {
    const res = await listWxSafeInfo(queryParams);
    dataList.value = res.data.data.items;
    total.value = res.data.data.total;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

function handleQuery() {
  queryParams.page_no = 1;
  getList();
}

function resetQuery() {
  queryParams.clue_number = '';
  queryParams.phone_number = '';
  handleQuery();
}

function handleAdd() {
  dialogTitle.value = '新增涉诈信息';
  dialogVisible.value = true;
  Object.assign(formData, {
    clue_number: '',
    category: '涉诈',
    phone_number: '',
    report_month: '',
    incident_time: '',
    city: '',
    fraud_type: '',
    victim_number: ''
  });
}

const dataFormRef = ref();
async function submitForm() {
  dataFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await addWxSafeInfo(formData);
        ElMessage.success('录入成功');
        dialogVisible.value = false;
        getList();
      } catch (error: any) {
        ElMessage.error(error.message || '录入失败');
      }
    }
  });
}

function handleImport() {
  importVisible.value = true;
}

async function handleUploadFile(formData: FormData) {
  try {
    const res = await importWxSafeInfo(formData);
    importResult.value = res.data.data;
    importVisible.value = false;
    ElMessage.success(`导入完成，成功 ${res.data.data.success_count} 条，失败 ${res.data.data.fail_count} 条`);
    
    if (res.data.data.fail_count > 0) {
      resultVisible.value = true;
    }
    getList();
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败');
  }
}

onMounted(() => {
  getList();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.ml-2 {
  margin-left: 8px;
}
</style>