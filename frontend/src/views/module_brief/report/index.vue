<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="flex justify-between items-center">
          <span>智能简报列表</span>
          <el-button type="primary" @click="handleUpload">上传分析</el-button>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column prop="focus" label="分析关注点" min-width="150" show-overflow-tooltip />
        <el-table-column prop="word_count" label="字数" width="100" align="center" />
        <el-table-column prop="created_time" label="生成时间" width="180" align="center" />
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleDetail(scope.row)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page_no"
          v-model:page-size="queryParams.page_size"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="getList"
          @current-change="getList"
        />
      </div>
    </el-card>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传工单分析" width="500px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="分析关注点">
          <el-input v-model="uploadForm.focus" placeholder="例如：分析处理效率、异常时长等" />
        </el-form-item>
        <el-form-item label="Excel文件">
          <el-upload
            ref="uploadRef"
            action=""
            :auto-upload="false"
            :limit="1"
            accept=".xlsx"
            :on-change="handleFileChange"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitUpload">开始分析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';

const router = useRouter();
const loading = ref(false);
const list = ref([]);
const total = ref(0);
const queryParams = ref({
  page_no: 1,
  page_size: 10
});

const uploadVisible = ref(false);
const uploading = ref(false);
const uploadForm = ref({
  focus: ''
});
const uploadFile = ref<any>(null);

const getList = async () => {
  loading.value = true;
  try {
    const res: any = await request({
      url: '/brief/list',
      method: 'get',
      params: queryParams.value
    });
    list.value = res.data.items || [];
    total.value = res.data.total || 0;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleUpload = () => {
  uploadVisible.value = true;
};

const handleFileChange = (file: any) => {
  uploadFile.value = file.raw;
};

const submitUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择文件');
    return;
  }
  uploading.value = true;
  const formData = new FormData();
  formData.append('file', uploadFile.value);
  if (uploadForm.value.focus) {
    formData.append('focus', uploadForm.value.focus);
  }

  try {
    const res: any = await request({
      url: '/brief/upload',
      method: 'post',
      data: formData,
      params: { focus: uploadForm.value.focus }, // 有些接口可能从 query 传 focus
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    ElMessage.success('分析成功');
    uploadVisible.value = false;
    getList();
    // 跳转到详情
    router.push(`/brief/report/${res.data.id}`);
  } catch (error) {
    console.error(error);
  } finally {
    uploading.value = false;
  }
};

const handleDetail = (row: any) => {
  router.push(`/brief/report/${row.id}`);
};

onMounted(() => {
  getList();
});
</script>

<style scoped>
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
