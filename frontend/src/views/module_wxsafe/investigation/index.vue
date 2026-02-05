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
      <el-tabs v-model="queryParams.status" @tab-change="handleTabChange">
        <el-tab-pane name="pending">
          <template #label>
            待核查任务
            <el-badge :value="counts.pending" :hidden="counts.pending === 0" class="ml-1" type="danger" />
          </template>
        </el-tab-pane>
        <el-tab-pane name="verified">
          <template #label>
            已核查记录
            <el-badge :value="counts.verified" :hidden="counts.verified === 0" class="ml-1" type="info" />
          </template>
        </el-tab-pane>
      </el-tabs>

      <el-table v-loading="loading" :data="dataList" style="width: 100%; min-height: 400px;">
        <el-table-column label="线索编号" align="center" prop="clue_number" width="180" />
        <el-table-column label="业务号码" align="center" prop="phone_number" width="130" />
        <el-table-column label="入网属地" align="center" prop="join_location" width="100" />
        
        <!-- 待核查视图特有列 -->
        <template v-if="queryParams.status === 'pending'">
          <el-table-column label="涉诈类型" align="center" prop="fraud_type" show-overflow-tooltip />
          <el-table-column label="涉诈时间" align="center" prop="incident_time" width="170" />
        </template>
        
        <!-- 已核查视图特有列 -->
        <template v-else>
          <el-table-column label="核查反馈" align="center" prop="feedback" show-overflow-tooltip />
          <el-table-column label="更新时间" align="center" prop="updated_time" width="170" />
        </template>

        <el-table-column label="操作" align="center" width="120" fixed="right">
          <template #default="scope">
            <el-button 
              :type="queryParams.status === 'pending' ? 'primary' : 'success'" 
              link 
              :icon="queryParams.status === 'pending' ? 'Edit' : 'View'" 
              @click="handleInvestigate(scope.row)"
            >
              {{ queryParams.status === 'pending' ? '开始核查' : '详情/修改' }}
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
          @size-change="getList"
          @current-change="getList"
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
import { listWxSafeInvestigation, getWxSafeInvestigationCounts } from '@/api/module_wxsafe/info';
import InvestigationDialog from './components/InvestigationDialog.vue';

const loading = ref(false);
const total = ref(0);
const dataList = ref([]);
const dialogVisible = ref(false);
const currentRow = ref({});
const counts = reactive({
  pending: 0,
  verified: 0
});

const queryParams = reactive({
  page_no: 1,
  page_size: 10,
  clue_number: '',
  phone_number: '',
  status: 'pending'
});

/** 获取统计数量 */
async function getCounts() {
  try {
    const res = await getWxSafeInvestigationCounts();
    counts.pending = res.data.data.pending;
    counts.verified = res.data.data.verified;
  } catch (error) {
    console.error('获取统计数量失败', error);
  }
}

async function getList() {
  loading.value = true;
  dataList.value = [];
  try {
    const res = await listWxSafeInvestigation(queryParams);
    dataList.value = res.data.data.items;
    total.value = res.data.data.total;
    // 每次查完列表顺便更新下 Tab 上的数字
    getCounts();
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

function handleTabChange() {
  handleQuery();
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
