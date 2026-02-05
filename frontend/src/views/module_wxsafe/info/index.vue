<template>
  <div class="app-container">
    <!-- 搜索栏 -->
    <el-card shadow="never" class="mb-4">
      <el-form :inline="true" :model="queryParams" ref="queryFormRef">
        <el-form-item label="线索编号" prop="clue_number">
          <el-input v-model="queryParams.clue_number" placeholder="请输入" clearable style="width: 200px" @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="业务号码" prop="phone_number">
          <el-input v-model="queryParams.phone_number" placeholder="请输入" clearable style="width: 180px" @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="入网属地" prop="join_location">
          <el-input v-model="queryParams.join_location" placeholder="请输入" clearable style="width: 150px" @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="涉诈时间" prop="report_month">
          <el-date-picker
            v-model="queryParams.report_month"
            type="month"
            placeholder="选择月份"
            value-format="YYYY-MM"
            style="width: 150px"
            @change="handleQuery"
          />
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
            <el-button type="warning" icon="download" @click="handleExport">导出全量</el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="dataList" border stripe style="width: 100%">
        <!-- 1-8 核心字段 -->
        <el-table-column label="线索编号" align="center" prop="clue_number" width="180" fixed="left" />
        <el-table-column label="涉诈或涉案" align="center" prop="category" width="100" />
        <el-table-column label="业务号码" align="center" prop="phone_number" width="130" fixed="left" />
        <el-table-column label="月份" align="center" prop="report_month" width="100" />
        <el-table-column label="涉诈涉案时间" align="center" prop="incident_time" width="170" />
        <el-table-column label="涉诈涉案地" align="center" prop="city" width="120" />
        <el-table-column label="涉诈类型" align="center" prop="fraud_type" width="120" show-overflow-tooltip />
        <el-table-column label="受害人号码" align="center" prop="victim_number" width="150" show-overflow-tooltip />

        <!-- 9-15 基础业务信息 -->
        <el-table-column label="入网时间" align="center" prop="join_date" width="170" />
        <el-table-column label="在网时长(月)" align="center" prop="online_duration" width="110" />
        <el-table-column label="新装或存量" align="center" prop="install_type" width="100" />
        <el-table-column label="入网属地" align="center" prop="join_location" width="110" />
        <el-table-column label="办理方式" align="center" prop="is_local_handle" width="120" />
        <el-table-column label="机主名称" align="center" prop="owner_name" width="100" />
        <el-table-column label="证件地址" align="center" prop="cert_address" width="200" show-overflow-tooltip />

        <!-- 16-20 用户画像 -->
        <el-table-column label="客户类型" align="center" prop="customer_type" width="100" />
        <el-table-column label="名下手机号" align="center" prop="other_phones" width="150" show-overflow-tooltip />
        <el-table-column label="年龄" align="center" prop="age" width="70" />
        <el-table-column label="代理商" align="center" prop="agent_name" width="150" show-overflow-tooltip />
        <el-table-column label="受理厅店" align="center" prop="store_name" width="150" show-overflow-tooltip />

        <!-- 21-27 受理与套餐 -->
        <el-table-column label="受理人工号" align="center" prop="staff_id" width="100" />
        <el-table-column label="受理人" align="center" prop="staff_name" width="100" />
        <el-table-column label="同时办理卡号" align="center" prop="concurrent_cards" width="150" show-overflow-tooltip />
        <el-table-column label="套餐名称" align="center" prop="package_name" width="150" show-overflow-tooltip />
        <el-table-column label="是否融合" align="center" prop="is_fusion_package" width="90" />
        <el-table-column label="宽带业务" align="center" prop="has_broadband" width="90" />
        <el-table-column label="主副卡" align="center" prop="card_type" width="80" />

        <!-- 28-36 核查反馈信息 -->
        <el-table-column label="合规受理" align="center" prop="is_compliant" width="90" />
        <el-table-column label="涉案前复通" align="center" prop="has_resume_before" width="110" />
        <el-table-column label="复通规范" align="center" prop="is_resume_compliant" width="90" />
        <el-table-column label="责任认定" align="center" prop="responsibility" width="120" show-overflow-tooltip />
        <el-table-column label="亲属涉诈" align="center" prop="is_self_or_family" width="90" />
        <el-table-column label="警企协同" align="center" prop="police_collab" width="120" show-overflow-tooltip />
        <el-table-column label="调查备注" align="center" prop="investigation_note" width="150" show-overflow-tooltip />
        <el-table-column label="异常场景" align="center" prop="abnormal_scene" width="150" show-overflow-tooltip />
        <el-table-column label="核查反馈" align="center" prop="feedback" width="200" show-overflow-tooltip />
      </el-table>

      <!-- 分页 -->
      <div class="flex justify-end mt-4">
        <el-pagination
          v-model:current-page="queryParams.page_no"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="getList"
          @current-change="getList"
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
        <div class="dialog-footer">
          <el-button type="primary" @click="resultVisible = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { listWxSafeInfo, addWxSafeInfo, importWxSafeInfo, downloadWxSafeTemplate, exportWxSafeInfo } from '@/api/module_wxsafe/info';
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
  phone_number: '',
  join_location: '',
  report_month: ''
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
  queryParams.join_location = '';
  queryParams.report_month = '';
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

/** 导出处理 */
async function handleExport() {
  try {
    const response = await exportWxSafeInfo(queryParams);
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = `涉诈信息导出_${new Date().getTime()}.xlsx`;
    link.click();
    window.URL.revokeObjectURL(link.href);
    ElMessage.success('导出成功');
  } catch (error) {
    console.error('导出失败', error);
    ElMessage.error('导出失败');
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