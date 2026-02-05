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

    <!-- 列表栏 -->
    <el-card shadow="never">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-bold">待核查任务列表</span>
          <!-- 分公司用户一般没有导入权限，这里不放按钮 -->
        </div>
      </template>

      <el-table v-loading="loading" :data="dataList">
        <el-table-column label="线索编号" align="center" prop="clue_number" width="180" />
        <el-table-column label="业务号码" align="center" prop="phone_number" width="150" />
        <el-table-column label="入网属地" align="center" prop="join_location" width="120" />
        <el-table-column label="涉诈类型" align="center" prop="fraud_type" show-overflow-tooltip />
        <el-table-column label="涉诈时间" align="center" prop="incident_time" width="180" />
        
        <!-- 核查状态展示 (简单判断某个必填字段是否有值) -->
        <el-table-column label="核查状态" align="center" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.feedback" type="success">已核查</el-tag>
            <el-tag v-else type="warning">待核查</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" align="center" width="150" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              link 
              icon="Edit" 
              @click="handleInvestigate(scope.row)"
            >
              核查补录
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="flex justify-end mt-4">
        <el-pagination
          v-model:current-page="queryParams.page_no"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </el-card>

    <!-- 核查弹窗 -->
    <InvestigationDialog
      v-model="dialogVisible"
      :data="currentRow"
      @success="handleQuery"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { listWxSafeInfo } from '@/api/module_wxsafe/info';
import InvestigationDialog from './components/InvestigationDialog.vue';

const loading = ref(false);
const total = ref(0);
const dataList = ref([]);
const dialogVisible = ref(false);
const currentRow = ref({});

const queryParams = reactive({
  page_no: 1,
  page_size: 10,
  clue_number: '',
  phone_number: ''
});

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

function handleInvestigate(row: any) {
  currentRow.value = row;
  dialogVisible.value = true;
}

onMounted(() => {
  getList();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}
</style>
