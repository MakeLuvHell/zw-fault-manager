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
        <el-form-item label="入网属地" prop="join_location">
          <el-input v-model="queryParams.join_location" placeholder="请输入入网属地" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="涉诈时间" prop="report_month">
          <el-date-picker
            v-model="queryParams.report_month"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            value-format="YYYY-MM"
            style="width: 240px"
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
            <el-button 
              v-hasPerm="['module_wxsafe:info:add']"
              type="primary" 
              icon="plus" 
              @click="handleAdd"
            >单条录入</el-button>
            <el-button 
              v-hasPerm="['module_wxsafe:info:import']"
              type="success" 
              icon="upload" 
              @click="handleImport"
            >批量导入</el-button>
            <el-button 
              v-hasPerm="['module_wxsafe:info:export']"
              type="warning" 
              icon="download" 
              @click="handleExport"
            >导出全量</el-button>
            <el-button 
              v-hasPerm="['module_wxsafe:info:export_log']"
              type="info" 
              icon="list" 
              plain
              @click="handleViewExportLogs"
            >导出记录</el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table 
        v-loading="loading" 
        :data="dataList" 
        border 
        stripe 
        row-key="clue_number"
        style="width: 100%"
      >
        <!-- 展开行：展示所有 36 个字段的详情 -->
        <el-table-column type="expand">
          <template #default="props">
            <div class="p-4">
              <el-descriptions title="线索详查画像" :column="3" border size="small" class="custom-descriptions">
                <el-descriptions-item label="入网时间">{{ props.row.join_date || '-' }}</el-descriptions-item>
                <el-descriptions-item label="在网时长(月)">{{ props.row.online_duration || '-' }}</el-descriptions-item>
                <el-descriptions-item label="新装或存量">{{ props.row.install_type || '-' }}</el-descriptions-item>
                <el-descriptions-item label="入网属地">{{ props.row.join_location || '-' }}</el-descriptions-item>
                <el-descriptions-item label="办理方式">{{ props.row.is_local_handle || '-' }}</el-descriptions-item>
                <el-descriptions-item label="机主名称">{{ props.row.owner_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="证件地址" :span="2">{{ props.row.cert_address || '-' }}</el-descriptions-item>
                <el-descriptions-item label="客户类型">{{ props.row.customer_type || '-' }}</el-descriptions-item>
                <el-descriptions-item label="名下手机号" :span="2">{{ props.row.other_phones || '-' }}</el-descriptions-item>
                <el-descriptions-item label="年龄">{{ props.row.age || '-' }}</el-descriptions-item>
                <el-descriptions-item label="代理商">{{ props.row.agent_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="受理厅店">{{ props.row.store_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="受理人工号">{{ props.row.staff_id || '-' }}</el-descriptions-item>
                <el-descriptions-item label="受理人">{{ props.row.staff_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="同时办理卡号">{{ props.row.concurrent_cards || '-' }}</el-descriptions-item>
                <el-descriptions-item label="套餐名称">{{ props.row.package_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="是否融合">{{ props.row.is_fusion_package || '-' }}</el-descriptions-item>
                <el-descriptions-item label="宽带业务">{{ props.row.has_broadband || '-' }}</el-descriptions-item>
                <el-descriptions-item label="主副卡">{{ props.row.card_type || '-' }}</el-descriptions-item>
                <!-- <el-descriptions-item label="受害人号码" :span="3">
                  <div v-if="props.row.victim_number" class="flex flex-wrap gap-2 items-center min-h-[32px]">
                    <el-tag v-for="num in props.row.victim_number.split(',')" :key="num">{{ num }}</el-tag>
                    <el-button link type="primary" icon="copy-document" @click="copyText(props.row.victim_number)">复制全部</el-button>
                  </div>
                  <span v-else>-</span>
                </el-descriptions-item> -->
              </el-descriptions>

              <el-descriptions title="核查反馈信息" :column="3" border size="small" class="mt-4 custom-descriptions">
                <el-descriptions-item label="合规受理">
                  <el-tag size="small" :type="props.row.is_compliant === '是' ? 'success' : (props.row.is_compliant === '否' ? 'danger' : 'info')">
                    {{ props.row.is_compliant || '待核查' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="涉案前复通">{{ props.row.has_resume_before || '-' }}</el-descriptions-item>
                <el-descriptions-item label="复通规范">{{ props.row.is_resume_compliant || '-' }}</el-descriptions-item>
                <el-descriptions-item label="责任认定">{{ props.row.responsibility || '-' }}</el-descriptions-item>
                <el-descriptions-item label="亲属涉诈">{{ props.row.is_self_or_family || '-' }}</el-descriptions-item>
                <el-descriptions-item label="警企协同">{{ props.row.police_collab || '-' }}</el-descriptions-item>
                <el-descriptions-item label="异常场景" :span="3">{{ props.row.abnormal_scene || '-' }}</el-descriptions-item>
                <el-descriptions-item label="调查备注" :span="3">{{ props.row.investigation_note || '-' }}</el-descriptions-item>
                <el-descriptions-item label="核查反馈" :span="3">{{ props.row.feedback || '-' }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>

        <!-- 1-8 核心字段 (保留在主表) -->
        <el-table-column label="线索编号" align="center" prop="clue_number" width="180" />
        <el-table-column label="涉诈或涉案" align="center" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.category === '涉诈' ? 'danger' : (scope.row.category === '涉案' ? 'warning' : '')">
              {{ scope.row.category || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="业务号码" align="center" prop="phone_number" width="130" />
        <el-table-column label="月份" align="center" prop="report_month" width="100" />
        <el-table-column label="涉诈涉案时间" align="center" prop="incident_time" width="170" />
        <el-table-column label="涉诈涉案地" align="center" prop="city" width="120" />
        <el-table-column label="涉诈类型" align="center" prop="fraud_type" show-overflow-tooltip />
        <!-- <el-table-column label="受害人号码" align="center" min-width="250">
          <template #default="scope">
            <template v-if="scope.row.victim_number">
              <div class="flex flex-wrap gap-1 justify-center min-h-[32px]">
                <el-tag 
                  v-for="num in scope.row.victim_number.split(',').slice(0, 6)" 
                  :key="num" 
                  size="small" 
                  type="info"
                >
                  {{ num }}
                </el-tag>
                <el-popover
                  v-if="scope.row.victim_number.split(',').length > 6"
                  placement="top"
                  :width="300"
                  trigger="hover"
                >
                  <template #reference>
                    <el-tag size="small" type="warning">+{{ scope.row.victim_number.split(',').length - 6 }}</el-tag>
                  </template>
                  <div class="flex flex-wrap gap-2">
                    <el-tag v-for="num in scope.row.victim_number.split(',')" :key="num" size="small">{{ num }}</el-tag>
                  </div>
                </el-popover>
              </div>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column> -->
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
        <!-- <el-form-item label="受害人号码" prop="victim_number">
          <el-input v-model="formData.victim_number" type="textarea" placeholder="请输入受害人号码（多个用逗号隔开）" />
        </el-form-item> -->
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

    <!-- 导出记录日志弹窗 -->
    <el-dialog title="导出历史记录" v-loading="logLoading" v-model="exportLogVisible" width="800px">
      <el-table :data="exportLogs" max-height="450" stripe border>
        <el-table-column label="操作人" prop="operator_name" width="120" align="center" />
        <el-table-column label="导出条数" width="100" align="center">
          <template #default="scope">
            <el-tag type="success">{{ scope.row.change_diff?.export_count || 0 }}条</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="导出时间" prop="created_time" width="170" align="center" />
        <el-table-column label="检索条件" show-overflow-tooltip>
          <template #default="scope">
            <span class="text-xs text-gray-500">{{ scope.row.change_diff?.export_query || '全量导出' }}</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportLogVisible = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { listWxSafeInfo, addWxSafeInfo, importWxSafeInfo, downloadWxSafeTemplate, exportWxSafeInfo, listExportLogs } from '@/api/module_wxsafe/info';
import ImportModal from '@/components/CURD/ImportModal.vue';

const loading = ref(false);
const total = ref(0);
const dataList = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const importVisible = ref(false);
const resultVisible = ref(false);

// 导出日志相关状态
const exportLogVisible = ref(false);
const logLoading = ref(false);
const exportLogs = ref([]);

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

/** 查看导出记录 */
async function handleViewExportLogs() {
  exportLogVisible.value = true;
  logLoading.value = true;
  try {
    const res = await listExportLogs();
    exportLogs.value = res.data.data;
  } catch (error) {
    console.error(error);
  } finally {
    logLoading.value = false;
  }
}

/** 复制文本 */
function copyText(text: string) {
  const input = document.createElement('textarea');
  input.value = text;
  document.body.appendChild(input);
  input.select();
  try {
    if (document.execCommand('copy')) {
      ElMessage.success('复制成功');
    }
  } catch (err) {
    ElMessage.error('复制失败');
  }
  document.body.removeChild(input);
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
:deep(.custom-descriptions .el-descriptions__label),
:deep(.custom-descriptions .el-descriptions__content) {
  font-size: 13px !important;
  line-height: 1.5;
}
</style>