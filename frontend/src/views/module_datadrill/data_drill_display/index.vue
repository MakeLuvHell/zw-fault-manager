<template>
  <div class="app-container">
    <!-- 报表选择 -->
    <el-card v-if="!currentReportId" class="select-card">
      <template #header>请选择报表进行查看</template>
      <div class="report-list">
        <el-form :inline="true">
          <el-form-item label="搜索报表">
            <el-input
              v-model="searchKeyword"
              placeholder="请输入报表名称"
              clearable
              @change="loadReports"
            />
          </el-form-item>
        </el-form>
        <el-table
          v-loading="loadingList"
          :data="reportList"
          style="cursor: pointer"
          @row-click="handleSelectReport"
        >
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="report_name" label="报表名称" />
          <el-table-column prop="updated_time" label="更新时间" width="180">
            <template #default="{ row }">{{ formatToDateTime(row.updated_time) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click.stop="handleSelectReport(row)">进入</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="pageNo"
          :total="total"
          layout="prev, pager, next"
          class="mt-4"
          @current-change="loadReports"
        />
      </div>
    </el-card>

    <!-- 报表展示 -->
    <div v-else class="display-area">
      <div class="header-bar mb-6 bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <div class="flex items-center mb-3">
          <el-button
            v-if="!isStandalone"
            icon="Back"
            circle
            class="mr-4 hover:bg-gray-100 transition-colors"
            @click="exitReport"
          ></el-button>
          <div class="flex flex-col">
            <h2 class="text-2xl font-bold text-gray-800 tracking-tight">{{ currentReportName }}</h2>
            <span v-if="breadcrumbs.length > 1" class="text-gray-400 text-xs mt-1">
              当前位置: {{ breadcrumbs[breadcrumbs.length - 1].label }}
            </span>
          </div>
        </div>

        <el-divider class="my-3" />

        <!-- 面包屑 -->
        <el-breadcrumb separator="/" class="ml-1 text-sm">
          <el-breadcrumb-item v-if="isStandalone">
            <a
              class="cursor-pointer hover:text-blue-600 font-semibold text-blue-500 flex items-center"
              @click="backToMainReport"
            >
              <el-icon class="mr-1"><Back /></el-icon>
              返回主报表
            </a>
          </el-breadcrumb-item>
          <el-breadcrumb-item v-for="(crumb, index) in breadcrumbs" :key="index">
            <a
              v-if="!isStandalone && index < breadcrumbs.length - 1"
              class="cursor-pointer hover:text-blue-500 transition-colors"
              @click="handleBreadcrumb(index)"
            >
              {{ crumb.label }}
            </a>
            <span v-else class="text-gray-600 font-medium">{{ crumb.label }}</span>
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <el-card v-loading="loadingData">
        <!-- 操作栏 -->
        <div class="toolbar mb-4 flex justify-between">
          <div>
            <span v-if="validChildNodes.length > 0" class="text-gray-500 text-sm">
              <el-icon><InfoFilled /></el-icon>
              点击蓝色链接字段可下钻
            </span>
          </div>
          <div>
            <el-button icon="Refresh" circle @click="refreshCurrentData"></el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <el-table :data="tableData" border stripe highlight-current-row>
          <el-table-column
            v-for="col in columns"
            :key="col"
            :prop="col"
            :label="col"
            min-width="120"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span
                v-if="isLinkColumn(col)"
                class="text-blue-500 cursor-pointer hover:underline font-medium"
                @click.stop="handleCellClick(row, col)"
              >
                {{ row[col] }}
              </span>
              <span v-else>{{ row[col] }}</span>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container mt-4 flex justify-end">
          <el-pagination
            v-model:current-page="dataPageNo"
            v-model:page-size="dataPageSize"
            :total="dataTotal"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="refreshCurrentData"
            @current-change="refreshCurrentData"
          />
        </div>
      </el-card>

      <!-- 下钻选择弹窗 (当同一列有多个下钻维度时) -->
      <el-dialog v-model="drillSelectVisible" title="选择下钻维度" width="300px">
        <div class="flex flex-col gap-2">
          <el-button v-for="node in drillTargets" :key="node.id" @click="confirmDrillOpen(node)">
            {{ node.node_name }}
          </el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import API, {
  PxmDataDrillInfo,
  PxmDataDrillNode,
} from "@/api/module_datadrill/data_drill_info";
import { formatToDateTime } from "@/utils/dateUtil";
import { ElMessage } from "element-plus";
import { Back, Refresh, InfoFilled } from "@element-plus/icons-vue";
import { useTagsViewStore } from "@/store/modules/tags-view.store";

const route = useRoute();
const router = useRouter();
const tagsViewStore = useTagsViewStore();

// --- 列表逻辑 ---
const reportList = ref<PxmDataDrillInfo[]>([]);
const searchKeyword = ref("");
const pageNo = ref(1);
const total = ref(0);
const loadingList = ref(false);

// --- 展示逻辑 ---
const currentReportId = ref<number | null>(null);
const currentReportName = ref("");
const breadcrumbs = ref<{ label: string; nodeId: number; params: any }[]>([]);
const tableData = ref<any[]>([]);
const columns = ref<string[]>([]);
const loadingData = ref(false);
const dataPageNo = ref(1);
const dataPageSize = ref(10);
const dataTotal = ref(0);
const isStandalone = ref(false); // 独立模式（新标签页打开），简化导航

// 当前状态
const currentNodeId = ref<number | null>(null);
const currentParams = ref<any>({});
const childNodes = ref<PxmDataDrillNode[]>([]); // 可能的下钻路径

// 有效的子节点（已配置关联字段）
const validChildNodes = computed(() => {
  return childNodes.value.filter((n) => !!n.link_field);
});

// 下钻选择
const drillSelectVisible = ref(false);
const selectedRow = ref<any>(null);
const drillTargets = ref<PxmDataDrillNode[]>([]);

onMounted(() => {
  console.log("Index mounted, query:", route.query);
  // 检查查询参数
  if (route.query.report_id) {
    if (route.query.node_id) {
      console.log("Init from query with node_id");
      initFromQuery();
    } else {
      // 只有 report_id，加载该报表首页
      console.log("Load report by id from mounted:", route.query.report_id);
      loadReportById(Number(route.query.report_id));
    }
  } else {
    loadReports();
  }
});

// 监听路由变化，以便在切换带有不同参数的标签页时重新加载数据
watch(
  () => route.query,
  (newQuery) => {
    console.log("Route query changed:", newQuery);
    if (newQuery.report_id) {
      if (newQuery.node_id) {
        // 仅在独立模式下参数变化时重新加载
        if (
          currentReportId.value !== Number(newQuery.report_id) ||
          currentNodeId.value !== Number(newQuery.node_id) ||
          JSON.stringify(currentParams.value) !== newQuery.params
        ) {
          console.log("Reloading from query (standalone)...");
          initFromQuery();
        }
      } else if (Number(newQuery.report_id) !== currentReportId.value) {
        // 切换到了另一个报表的首页
        console.log("Switching report...", newQuery.report_id);
        loadReportById(Number(newQuery.report_id));
      }
    } else if (currentReportId.value) {
      // 参数被清空，回到列表
      console.log("Query cleared, back to list");
      currentReportId.value = null;
      loadReports();
    }
  }
);

async function loadReportById(id: number) {
  console.log("Loading report:", id);
  if (isNaN(id)) {
    ElMessage.error("无效的报表ID");
    return;
  }

  currentReportId.value = id;
  try {
    const res = await API.detail(id);
    const reportData = res.data.data;
    currentReportName.value = reportData.report_name;

    const nodes = reportData.nodes || [];
    const root = nodes.find((n: any) => !n.parent_id);

    if (!root) {
      ElMessage.warning("该报表未配置初始查询");
      // 注意：这里不再强制清除 URL，以便用户知道当前处于该报表下但出错了
      return;
    }

    // 初始化面包屑
    const rootLabel = reportData.description || "总览";
    breadcrumbs.value = [{ label: rootLabel, nodeId: root.id as number, params: {} }];

    // 加载根节点数据
    await loadNodeData(root.id as number, {});
  } catch (e) {
    console.error("Failed to load report:", e);
    ElMessage.error("加载报表配置失败");
    // 出错时不自动跳转回列表，以免用户困惑
    // currentReportId.value = null;
    // router.push({ path: route.path });
  }
}

async function initFromQuery() {
  isStandalone.value = true;
  const rId = Number(route.query.report_id);
  const nId = Number(route.query.node_id);
  const pStr = route.query.params as string;
  let params = {};
  try {
    params = pStr ? JSON.parse(pStr) : {};
  } catch (e) {
    console.error("Failed to parse params", e);
  }

  currentReportId.value = rId;

  // 获取报表信息以显示标题
  try {
    const res = await API.detail(rId);
    currentReportName.value = res.data.data.report_name;

    // 获取当前节点名称用于面包屑
    const nodes = res.data.data.nodes || [];
    const node = nodes.find((n: any) => n.id === nId);
    const nodeName = node ? node.node_name : "详情";

    // 更新当前标签页标题：报表名称 - 节点名称
    const visitedView = tagsViewStore.visitedViews.find(
      (v) => v.path === route.path && v.query?.node_id === String(nId)
    );
    if (visitedView) {
      visitedView.title = `${currentReportName.value} - ${nodeName}`;
    }

    breadcrumbs.value = [{ label: nodeName, nodeId: nId, params }];
  } catch (e) {
    currentReportName.value = "报表详情";
  }

  await loadNodeData(nId, params);
}

async function loadReports() {
  loadingList.value = true;
  try {
    const res = await API.list({
      page_no: pageNo.value,
      page_size: 10,
      report_name: searchKeyword.value,
      status: "0", // 仅活跃状态
    });
    reportList.value = res.data.data.items;
    total.value = res.data.data.total;
  } catch (e) {
    console.error(e);
  } finally {
    loadingList.value = false;
  }
}

async function handleSelectReport(row: PxmDataDrillInfo) {
  if (!row.id) return;

  // 更新路由参数，由 watch 触发加载逻辑
  router.push({ query: { ...route.query, report_id: row.id } });
}

function exitReport() {
  // 清除 report_id 参数，回到列表
  router.push({ path: route.path });
}

function backToMainReport() {
  // 返回当前报表的“初始查询”位置，清除 URL 参数并重载根节点数据

  if (!currentReportId.value) {
    // 如果没有 report_id，只能回列表
    router.push({ path: route.path });
    return;
  }

  // 临时保存 ID，因为路由跳转可能会清除状态
  const reportId = currentReportId.value;
  const reportName = currentReportName.value;

  // 跳转到无参路由
  router.push({ path: route.path }).then(async () => {
    // 恢复状态为“查看该报表详情”的初始状态
    currentReportId.value = reportId;
    currentReportName.value = reportName;
    isStandalone.value = false; // 退出独立模式

    // 重新执行 handleSelectReport 的逻辑（加载根节点）
    try {
      const res = await API.detail(reportId);
      const nodes = res.data.data.nodes || [];
      const root = nodes.find((n: any) => !n.parent_id);

      if (!root) {
        ElMessage.warning("该报表未配置初始查询");
        currentReportId.value = null;
        return;
      }

      // 重置面包屑
      const rootLabel = res.data.data.description || "总览";
      breadcrumbs.value = [{ label: rootLabel, nodeId: root.id as number, params: {} }];

      // 重置标题
      const routeName = route.name as string;
      const visitedView = tagsViewStore.visitedViews.find(
        (v) => v.path === route.path && !v.query?.node_id
      );
      if (visitedView) {
        // 恢复默认标题，或者设置为报表名称
        visitedView.title = reportName || (route.meta.title as string);
      }

      // 加载根节点数据
      dataPageNo.value = 1;
      await loadNodeData(root.id as number, {});
    } catch (e) {
      console.error(e);
      ElMessage.error("加载报表初始数据失败");
      currentReportId.value = null;
    }
  });
}

async function loadNodeData(nodeId: number, params: any) {
  loadingData.value = true;
  currentNodeId.value = nodeId;
  currentParams.value = params;

  try {
    // 1. 执行查询
    const res = await API.executeDrill({
      report_id: currentReportId.value!,
      node_id: nodeId,
      params,
      page_no: dataPageNo.value,
      page_size: dataPageSize.value,
    });

    columns.value = res.data.data.columns;
    tableData.value = res.data.data.data;
    dataTotal.value = res.data.data.total;

    // 2. 获取子节点以便下次下钻
    const childRes = await API.getNodeChildren(nodeId);
    childNodes.value = childRes.data.data || [];
  } catch (e: any) {
    console.error(e);
    ElMessage.error(e.message || "查询失败");
  } finally {
    loadingData.value = false;
  }
}

async function refreshCurrentData() {
  if (currentNodeId.value) {
    await loadNodeData(currentNodeId.value, currentParams.value);
  }
}

// 检查列是否触发下钻
function isLinkColumn(col: string) {
  return validChildNodes.value.some((n) => n.link_field === col);
}

function handleCellClick(row: any, col: string) {
  const targets = validChildNodes.value.filter((n) => n.link_field === col);
  if (targets.length === 0) return;

  selectedRow.value = row;

  if (targets.length === 1) {
    confirmDrillOpen(targets[0]);
  } else {
    drillTargets.value = targets;
    drillSelectVisible.value = true;
  }
}

function confirmDrillOpen(nextNode: PxmDataDrillNode) {
  drillSelectVisible.value = false;
  if (!nextNode.id) return;

  if (!nextNode.link_field) {
    ElMessage.warning("未配置关联字段");
    return;
  }

  // 准备参数
  const val = selectedRow.value[nextNode.link_field];
  const newParams = { ...currentParams.value };
  if (nextNode.param_name) {
    newParams[nextNode.param_name] = val;
  }

  // 在新的内部标签页中打开，构建查询参数
  const query = {
    report_id: currentReportId.value,
    node_id: nextNode.id,
    params: JSON.stringify(newParams),
    _t: Date.now(), // 添加时间戳以确保唯一性
  };

  router.push({ path: route.path, query });
}

async function handleBreadcrumb(index: number) {
  // 回滚到索引（仅适用于非独立模式）
  const target = breadcrumbs.value[index];
  breadcrumbs.value = breadcrumbs.value.slice(0, index + 1);

  dataPageNo.value = 1;
  await loadNodeData(target.nodeId, target.params);
}

const rowStyle = computed(() => {
  // 行不再可点击，仅单元格可点击
  return {};
});
</script>

<style scoped>
.select-card {
  width: 100%;
}
.display-area {
  width: 100%;
}
</style>
