<template>
  <el-dialog :title="title" v-model="visible" width="900px" append-to-body destroy-on-close>
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <!-- Tab 1: 核查补录 -->
      <el-tab-pane label="核查补录" name="form">
        <!-- 基础信息展示区 (只读) -->
        <el-descriptions title="基础线索信息" :column="2" border class="mb-4 mt-2">
          <el-descriptions-item label="线索编号">{{ info.clue_number }}</el-descriptions-item>
          <el-descriptions-item label="业务号码">{{ info.phone_number }}</el-descriptions-item>
          <el-descriptions-item label="涉诈类型">{{ info.fraud_type }}</el-descriptions-item>
          <el-descriptions-item label="入网属地">{{ info.join_location }}</el-descriptions-item>
          <el-descriptions-item label="涉诈时间">{{ info.incident_time }}</el-descriptions-item>
        </el-descriptions>

        <!-- 核查补录表单 -->
        <el-form ref="formRef" :model="formData" label-width="140px">
          <el-divider content-position="left">核查结果录入</el-divider>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="是否合规受理" prop="is_compliant">
                <el-select v-model="formData.is_compliant" placeholder="请选择" class="w-full">
                  <el-option label="是" value="是" />
                  <el-option label="否" value="否" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="涉诈前是否有复通" prop="has_resume_before">
                <el-select v-model="formData.has_resume_before" placeholder="请选择" class="w-full">
                  <el-option label="是" value="是" />
                  <el-option label="否" value="否" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="复通是否规范" prop="is_resume_compliant">
                <el-select v-model="formData.is_resume_compliant" placeholder="请选择" class="w-full">
                  <el-option label="是" value="是" />
                  <el-option label="否" value="否" />
                  <el-option label="不涉及" value="不涉及" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="责任认定" prop="responsibility">
                <el-input v-model="formData.responsibility" placeholder="请输入责任认定" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="是否本人/亲属涉诈" prop="is_self_or_family">
                <el-select v-model="formData.is_self_or_family" placeholder="请选择" class="w-full">
                  <el-option label="是" value="是" />
                  <el-option label="否" value="否" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="警企协同情况" prop="police_collab">
                <el-input v-model="formData.police_collab" placeholder="请输入警企协同情况" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="调查户主备注" prop="investigation_note">
                <el-input v-model="formData.investigation_note" type="textarea" :rows="2" placeholder="请输入调查备注" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="异常场景识别" prop="abnormal_scene">
                <el-input v-model="formData.abnormal_scene" type="textarea" :rows="2" placeholder="请输入异常场景识别" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="核查情况反馈" prop="feedback">
                <el-input v-model="formData.feedback" type="textarea" :rows="3" placeholder="请输入最终核查反馈" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-tab-pane>

      <!-- Tab 2: 变更日志 -->
      <el-tab-pane label="变更日志" name="logs">
        <div class="log-container p-4" v-loading="logsLoading">
          <el-empty v-if="logs.length === 0" description="暂无修改记录" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="(log, index) in logs"
              :key="index"
              :timestamp="log.created_time"
              placement="top"
              type="primary"
            >
              <el-card shadow="hover" class="mb-2">
                <div class="flex justify-between items-center mb-2">
                  <span class="font-bold text-blue-600">操作人: {{ log.operator_name || '未知' }}</span>
                  <el-tag size="small">{{ log.action_type }}</el-tag>
                </div>
                <div class="text-sm text-[var(--el-text-color-regular)]">
                  <div v-for="(val, field) in log.change_diff" :key="field" class="mb-2 last:mb-0 flex items-center flex-wrap">
                    <span class="inline-block px-2 py-0.5 mr-2 rounded bg-[var(--el-fill-color-light)] text-[var(--el-color-primary)] font-bold border border-[var(--el-border-color-light)]">
                      {{ fieldMap[field] || field }}
                    </span>
                    <span class="mr-2">从</span>
                    <span class="text-[var(--el-color-danger)] opacity-70 line-through mr-2">{{ val[0] || '(空)' }}</span> 
                    <span class="mr-2">修改为</span>
                    <span class="text-[var(--el-color-success)] font-bold">{{ val[1] || '(空)' }}</span>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div v-if="activeTab === 'form'">
        <el-button @click="visible = false">取 消</el-button>
        <el-button type="primary" :loading="loading" @click="submitForm">提 交</el-button>
      </div>
      <div v-else>
        <el-button @click="visible = false">关 闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { updateWxSafeInvestigation, listWxSafeLogs } from '@/api/module_wxsafe/info';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  data: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['update:modelValue', 'success']);

const loading = ref(false);
const logsLoading = ref(false);
const formRef = ref();
const activeTab = ref('form');
const logs = ref([]);

// 字段映射表
const fieldMap = {
  is_compliant: '是否合规受理',
  has_resume_before: '涉诈前是否有复通',
  is_resume_compliant: '复通是否规范',
  responsibility: '责任认定',
  is_self_or_family: '是否本人/亲属涉诈',
  police_collab: '警企协同情况',
  investigation_note: '调查户主备注',
  abnormal_scene: '异常场景识别',
  feedback: '核查情况反馈'
};

// 基础信息
const info = computed(() => props.data);

// 只有9个补充字段
const formData = reactive({
  is_compliant: '',
  has_resume_before: '',
  is_resume_compliant: '',
  responsibility: '',
  is_self_or_family: '',
  police_collab: '',
  investigation_note: '',
  abnormal_scene: '',
  feedback: ''
});

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const title = computed(() => `核查补录 - ${info.value.clue_number}`);

// 打开时初始化表单数据
function init(row: any) {
  activeTab.value = 'form';
  logs.value = [];
  Object.keys(formData).forEach(key => {
    formData[key] = row[key] || '';
  });
}

/** 加载日志 */
async function loadLogs() {
  if (!info.value.clue_number) return;
  logsLoading.value = true;
  try {
    const res = await listWxSafeLogs(info.value.clue_number);
    logs.value = res.data.data;
  } catch (error) {
    console.error('加载日志失败', error);
  } finally {
    logsLoading.value = false;
  }
}

function handleTabClick(tab: any) {
  if (tab.paneName === 'logs' && logs.value.length === 0) {
    loadLogs();
  }
}

async function submitForm() {
  loading.value = true;
  try {
    await updateWxSafeInvestigation(info.value.clue_number, formData);
    ElMessage.success('核查信息保存成功');
    visible.value = false;
    emit('success');
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败');
  } finally {
    loading.value = false;
  }
}

watch(() => props.data, (newVal) => {
  if (newVal && Object.keys(newVal).length > 0) {
    init(newVal);
  }
}, { immediate: true });

</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}
.log-container {
  max-height: 500px;
  overflow-y: auto;
}
.w-full {
  width: 100%;
}
</style>
