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
          <div v-loading="loading" class="markdown-body" v-html="renderedContent">
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
            <el-descriptions-item label="工单总数">{{ summary.total_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="所属月份">{{ report.report_date ? report.report_date.substring(0, 7) : '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" class="mt-4">
          <template #header>
            <span>自分类分布 (Top 10)</span>
          </template>
          <el-table :data="typeData" size="small" border>
            <el-table-column prop="name" label="分类" show-overflow-tooltip />
            <el-table-column prop="value" label="数量" width="80" align="center" />
          </el-table>
        </el-card>

        <el-card v-if="hasDuration" shadow="never" class="mt-4">
          <template #header>
            <span>效能指标 (平均)</span>
          </template>
          <div class="flex justify-around py-2">
            <el-statistic title="平均办结时长" :value="summary.duration_metrics.avg_duration">
              <template #suffix>小时</template>
            </el-statistic>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getBriefReportDetail } from '@/api/module_brief';
import MarkdownIt from 'markdown-it';

const md = new MarkdownIt();
const route = useRoute();
const router = useRouter();

const loading = ref(false);
const report = ref<any>({});

const summary = computed(() => report.value.summary_data || {});
const typeData = computed(() => {
  const dist = summary.value.type_distribution || {};
  return Object.keys(dist).map(key => ({ name: key, value: dist[key] }));
});
const hasDuration = computed(() => summary.value.duration_metrics && summary.value.duration_metrics.avg_duration);

const renderedContent = computed(() => {
  if (report.value.report_content) {
    return md.render(report.value.report_content);
  }
  return '暂无分析内容';
});

const getDetail = async () => {
  const id = route.params.id as string;
  loading.value = true;
  try {
    const res: any = await getBriefReportDetail(id);
    report.value = res.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleCopy = async () => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(report.value.report_content);
      ElMessage.success('报告内容已复制到剪贴板');
    } else {
      throw new Error('当前环境不支持自动复制');
    }
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
