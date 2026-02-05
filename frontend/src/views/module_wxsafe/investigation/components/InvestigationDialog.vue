<template>
  <el-dialog :title="title" v-model="visible" width="800px" append-to-body destroy-on-close>
    <!-- 基础信息展示区 (只读) -->
    <el-descriptions title="基础线索信息" :column="2" border class="mb-4">
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
            <el-select v-model="formData.is_compliant" placeholder="请选择">
              <el-option label="是" value="是" />
              <el-option label="否" value="否" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="涉诈前是否有复通" prop="has_resume_before">
            <el-select v-model="formData.has_resume_before" placeholder="请选择">
              <el-option label="是" value="是" />
              <el-option label="否" value="否" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="复通是否规范" prop="is_resume_compliant">
            <el-select v-model="formData.is_resume_compliant" placeholder="请选择">
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
            <el-select v-model="formData.is_self_or_family" placeholder="请选择">
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

    <template #footer>
      <el-button @click="visible = false">取 消</el-button>
      <el-button type="primary" :loading="loading" @click="submitForm">提 交</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { updateWxSafeInvestigation } from '@/api/module_wxsafe/info';

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
const formRef = ref();

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
  Object.keys(formData).forEach(key => {
    formData[key] = row[key] || '';
  });
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

// 暴露 init 方法供父组件调用（如果需要，不过目前是通过 props.data 传进来的）
// 实际上父组件在打开 dialog 前会设置 data，这里我们可以监听 visible 变化或者直接在 setup 里做 watch
import { watch } from 'vue';
watch(() => props.data, (newVal) => {
  if (newVal) {
    init(newVal);
  }
}, { immediate: true });

</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}
</style>
