<template>
  <div class="app-container">
    <el-page-header @back="goBack" :title="'分析报告：' + report.filename">
      <template #extra>
        <div class="flex items-center">
          <el-tag v-if="report.created_time" type="info">{{ report.created_time }}</el-tag>
          <el-button class="ml-2" type="primary" @click="handleCopy">复制报告</el-button>
        </div>
      </template>
    </el-page-header>

    <el-row :gutter="20" class="mt-4">
      <!-- 报告内容 -->
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="flex items-center">
              <el-icon class="mr-1"><Memo /></el-icon>
              <span>智能简报正文</span>
            </div>
          </template>
          <div v-loading="loading" class="markdown-body">
            <v-md-preview :text="report.analysis_content || '暂无分析内容'"></v-md-preview>
          </div>
        </el-card>
      </el-col>

      <!-- 侧边信息 -->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>分析元数据</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="文件名">{{ report.filename }}</el-descriptions-item>
            <el-descriptions-item label="关注点">{{ report.focus || '全维度分析' }}</el-descriptions-item>
            <el-descriptions-item label="报告字数">{{ report.word_count }}</el-descriptions-item>
            <el-descriptions-item label="原始记录数">{{ originalCount }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" class="mt-4">
          <template #header>
            <span>数据快照预览</span>
          </template>
          <el-table :data="report.original_data" size="small" border height="300px">
            <el-table-column prop="标题" label="标题" show-overflow-tooltip />
            <el-table-column prop="处理人" label="处理人" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import useClipboard from 'vue-clipboard3';

const route = useRoute();
const router = useRouter();
const { toClipboard } = useClipboard();

const loading = ref(false);
const report = ref<any>({});

const originalCount = computed(() => {
  return report.value.original_data ? report.value.original_data.length : 0;
});

const getDetail = async () => {
  const id = route.params.id;
  loading.value = true;
  try {
    const res: any = await request({
      url: `/brief/${id}`,
      method: 'get'
    });
    report.value = res.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleCopy = async () => {
  try {
    await toClipboard(report.value.analysis_content);
    ElMessage.success('报告内容已复制到剪贴板');
  } catch (e) {
    ElMessage.error('复制失败');
  }
};

const goBack = () => {
  router.push('/brief/report');
};

onMounted(() => {
  getDetail();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.mt-4 {
  margin-top: 1rem;
}
.markdown-body {
  min-height: 400px;
}
</style>
