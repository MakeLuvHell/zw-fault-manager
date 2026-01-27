<template>
  <div class="drill-config-container">
    <div class="left-tree">
      <div class="tree-toolbar">
        <el-button type="primary" size="small" :disabled="hasRoot" @click="handleAddRoot">
          添加根节点
        </el-button>
        <el-button
          type="success"
          size="small"
          icon="Refresh"
          circle
          @click="refreshTree"
        ></el-button>
      </div>
      <el-tree
        ref="treeRef"
        :data="treeData"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        highlight-current
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span>{{ data.node_name }}</span>
            <span class="tree-actions">
              <el-button link type="primary" size="small" @click.stop="append(data)">
                添加下级
              </el-button>
              <el-button link type="danger" size="small" @click.stop="remove(node, data)">
                删除
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </div>

    <div v-loading="loadingNode" class="right-form">
      <div v-if="!currentNode" class="empty-tip">请选择或添加节点进行配置</div>
      <el-form v-else ref="formRef" :model="currentNode" label-width="100px" :rules="rules">
        <el-form-item label="节点名称" prop="node_name">
          <el-input v-model="currentNode.node_name" />
        </el-form-item>

        <el-form-item label="SQL语句" prop="sql_text">
          <div
            class="flex-y-center"
            style="justify-content: space-between; margin-bottom: 6px; width: 100%"
          >
            <el-text type="info">只读展示，点击右侧按钮编辑</el-text>
            <el-button type="primary" plain size="small" @click="openSqlDialog">编辑SQL</el-button>
          </div>
          <div
            :class="['code-static', 'cm-theme-dracula']"
            style="max-height: 300px; width: 100%"
            v-html="sqlRunModeHtml"
          ></div>
        </el-form-item>

        <template v-if="currentNode.parent_id">
          <el-form-item label="父级字段" prop="link_field">
            <el-select
              v-model="currentNode.link_field"
              placeholder="请选择父级关联字段"
              filterable
              :loading="loadingParentCols"
              @visible-change="handleParentColsVisible"
            >
              <el-option v-for="col in parentColumns" :key="col" :label="col" :value="col" />
            </el-select>
            <div class="form-tip text-gray-400 text-xs">
              数据来源：父节点SQL的输出字段（点击下拉自动加载）
            </div>
          </el-form-item>

          <el-form-item label="参数名" prop="param_name">
            <el-select
              v-model="currentNode.param_name"
              placeholder="请选择参数名"
              filterable
              allow-create
              default-first-option
              :loading="loadingParamName"
              @visible-change="handleParamNameVisible"
            >
              <el-option
                v-for="param in paramNameOptions"
                :key="param"
                :label="param"
                :value="param"
              />
            </el-select>
            <div class="form-tip text-gray-400 text-xs">
              本节点SQL中使用的参数名 (e.g. SELECT ... WHERE id = :dept_id)
            </div>
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleUpdateNode">
            保存当前节点
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- SQL 编辑弹窗 -->
    <el-dialog
      v-model="sqlDialogVisible"
      :title="'编辑SQL查询语句'"
      :width="sqlDialogWidth"
      :close-on-click-modal="false"
      append-to-body
    >
      <div :class="['code-input', { 'code-input--error': !!sqlEditError }]">
        <Codemirror
          ref="sqlEditRef"
          v-model:value="sqlEditorText"
          :options="cmOptions"
          height="360px"
          width="100%"
          :autofocus="true"
        />
      </div>
      <template v-if="sqlEditError">
        <div class="el-form-item__error" style="position: relative; top: 0; padding-top: 4px">
          {{ sqlEditError }}
        </div>
      </template>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="success" :loading="validating" @click="handleValidateSqlInDialog">
            检测SQL
          </el-button>
          <el-button @click="closeSqlDialog">取消</el-button>
          <el-button type="primary" :disabled="!sqlCheckPassed" @click="confirmSqlEdit">
            确认
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import API, { PxmDataDrillNode } from "@/api/module_datadrill/data_drill_info";
import Codemirror, { CmComponentRef } from "codemirror-editor-vue3";
import CodeMirrorLib from "codemirror";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/sql/sql.js";
import "codemirror/theme/dracula.css";
import "codemirror/addon/runmode/runmode.js";
import "codemirror/addon/hint/show-hint.css";
import "codemirror/addon/hint/show-hint.js";
import "codemirror/addon/hint/sql-hint.js";
import { format as sqlFormat } from "sql-formatter";

const props = defineProps<{
  infoId: number;
}>();

const treeData = ref<PxmDataDrillNode[]>([]);
const currentNode = ref<PxmDataDrillNode | null>(null);
const loadingNode = ref(false);
const saving = ref(false);
const validating = ref(false);
const parentColumns = ref<string[]>([]);
const loadingParentCols = ref(false);

// SQL Dialog State
const sqlDialogVisible = ref(false);
const sqlEditorText = ref("");
const sqlEditRef = ref<CmComponentRef>();
const sqlEditError = ref("");
const sqlCheckPassed = ref(false);

const cmOptions = {
  mode: "text/x-sql",
  theme: "dracula",
  lineNumbers: true,
  smartIndent: true,
  indentUnit: 2,
  lineWrapping: true,
};

const rules = {
  node_name: [{ required: true, message: "请输入节点名称", trigger: "blur" }],
  sql_text: [{ required: true, message: "请输入SQL", trigger: "blur" }],
};

const hasRoot = computed(() => treeData.value.length > 0);
const sqlDialogWidth = computed(() => (window.innerWidth < 768 ? "90%" : "800px"));

// SQL Read-only Display Logic
const formattedSQL = computed(() => {
  const s = currentNode.value?.sql_text || "";
  if (!s) return "";
  try {
    return sqlFormat(s, { language: "postgresql" });
  } catch {
    return s;
  }
});

const sqlRunModeHtml = computed(() => {
  const text = formattedSQL.value || "";
  const mode = "text/x-sql";
  let html = "";
  const lines = text.split("\n");
  for (let i = 0; i < lines.length; i++) {
    CodeMirrorLib.runMode(lines[i], mode, (tokenText: string, style?: string | null) => {
      if (!tokenText) return;
      const esc = tokenText.replace(
        /[&<>]/g,
        (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[ch] as string
      );
      if (style) {
        html += `<span class="cm-${style}">${esc}</span>`;
      } else {
        html += esc;
      }
    });
    if (i < lines.length - 1) html += "<br>";
  }
  return html;
});

onMounted(() => {
  refreshTree();
});

async function refreshTree() {
  if (!props.infoId) return;
  try {
    const res = await API.detail(props.infoId);
    const nodes = res.data.data.nodes || [];
    treeData.value = buildTree(nodes);
    currentNode.value = null;
  } catch (e) {
    console.error(e);
  }
}

function buildTree(nodes: PxmDataDrillNode[]) {
  const map: Record<number, PxmDataDrillNode> = {};
  const roots: PxmDataDrillNode[] = [];
  const list = JSON.parse(JSON.stringify(nodes));
  list.forEach((node: any) => {
    map[node.id] = node;
    node.children = [];
  });
  list.forEach((node: any) => {
    if (node.parent_id && map[node.parent_id]) {
      map[node.parent_id].children?.push(node);
    } else {
      roots.push(node);
    }
  });
  return roots;
}

async function handleAddRoot() {
  const newNode = {
    info_id: props.infoId,
    node_name: "初始查询",
    sql_text: "SELECT * FROM ...",
    parent_id: null,
  };
  try {
    await API.createNode(newNode);
    ElMessage.success("添加成功");
    refreshTree();
  } catch (e) {
    console.error(e);
  }
}

async function append(data: PxmDataDrillNode) {
  const newNode = {
    info_id: props.infoId,
    node_name: "新节点",
    sql_text: "",
    parent_id: data.id,
    link_field: "",
    param_name: "",
  };
  try {
    await API.createNode(newNode);
    ElMessage.success("添加成功");
    refreshTree();
  } catch (e) {
    console.error(e);
  }
}

async function remove(node: any, data: PxmDataDrillNode) {
  ElMessageBox.confirm("确认删除该节点及其子节点吗?", "提示", {
    type: "warning",
  }).then(async () => {
    if (data.id) {
      await API.deleteNode([data.id]);
      ElMessage.success("删除成功");
      refreshTree();
    }
  });
}

const paramNameOptions = ref<string[]>([]);
const loadingParamName = ref(false);

async function handleParamNameVisible(visible: boolean) {
  // Use sqlEditorText if dialog is open and validated, otherwise use currentNode.sql_text
  // But wait, user says "子节点sql", which implies current node's SQL.
  // The param name dropdown is inside the form, so it refers to the SQL of the CURRENT node.
  if (visible) {
    await loadParamNameOptions();
  }
}

async function loadParamNameOptions() {
  const sql = currentNode.value?.sql_text;
  if (!sql) return;
  loadingParamName.value = true;
  try {
    // Use backend validation API to extract parameters if possible,
    // BUT the current API (validateSql) returns result columns, not input parameters.
    // However, regex is unreliable for all SQL dialects.
    // Since the user asked to "use query SQL return field names",
    // it seems they might have misunderstood "param_name" as "output fields from current SQL"
    // OR they want the fields from the PARENT SQL to be used as params here?

    // Clarification:
    // "param_name" usually refers to the parameter IN THE CURRENT SQL (e.g. `WHERE id = :param`)
    // that will be filled by the parent's data.
    // If the user wants "field names from SQL result", they might mean `link_field`.

    // Re-reading user request: "请通过查询SQL返回字段名称的方式获取" (Please get it by querying SQL return field names).
    // This strongly suggests they want the OUTPUT COLUMNS of the CURRENT SQL to be available as "param_name"?
    // This is unusual. Usually `param_name` is an INPUT.
    // UNLESS: The user means "Get the bind parameters detected by the backend".

    // BUT, if the user implies "I want to select one of the columns of THIS node",
    // then we should call `validateSql`.

    // Let's assume the user wants to populate the dropdown with the result columns of the current SQL.
    // (Even though `param_name` is typically an input bind variable).
    // If the user actually means "I want to bind a parent column to a specific param name",
    // and they want to pick from available params...

    // Wait, if the user explicitly said "return field names" (返回字段名称),
    // they likely mean `validateSql` which returns `columns`.

    const res = await API.validateSql({ sql_text: sql });
    if (res.data.data.valid) {
      // The user might be confusing param_name (input) with link_field (output),
      // OR they want to see what columns are available.
      // But sticking to the instruction: use SQL return fields.
      paramNameOptions.value = res.data.data.columns || [];
      if (paramNameOptions.value.length === 0) {
        ElMessage.info("该SQL没有返回字段");
      }
    } else {
      ElMessage.warning("SQL校验未通过，无法获取字段: " + res.data.data.message);
    }
  } catch (e) {
    console.error(e);
    ElMessage.error("获取字段失败");
  } finally {
    loadingParamName.value = false;
  }
}

function handleNodeClick(data: PxmDataDrillNode) {
  currentNode.value = { ...data };
  parentColumns.value = [];
  paramNameOptions.value = [];
}

// SQL Dialog Functions
function openSqlDialog() {
  sqlEditorText.value = currentNode.value?.sql_text || "";
  sqlEditError.value = "";
  sqlCheckPassed.value = false;
  sqlDialogVisible.value = true;
  nextTick(() => {
    const cm = sqlEditRef.value?.cminstance;
    cm?.refresh();
    cm?.focus();
    // Enable hints
    cm?.setOption("extraKeys", {
      "Ctrl-Space": "autocomplete",
      "Cmd-Space": "autocomplete",
      "Alt-Space": "autocomplete",
    });
  });
}

function closeSqlDialog() {
  sqlDialogVisible.value = false;
  sqlCheckPassed.value = false;
  sqlEditError.value = "";
}

async function handleValidateSqlInDialog() {
  if (!sqlEditorText.value || !sqlEditorText.value.trim()) {
    sqlEditError.value = "SQL语句不能为空";
    return;
  }
  validating.value = true;
  sqlEditError.value = "";
  try {
    const res = await API.validateSql({ sql_text: sqlEditorText.value });
    const { valid, message } = res.data.data;
    if (valid) {
      sqlCheckPassed.value = true;
      ElMessage.success(message);
    } else {
      sqlCheckPassed.value = false;
      sqlEditError.value = message;
    }
  } catch (e) {
    console.error(e);
    sqlEditError.value = "校验请求失败";
    sqlCheckPassed.value = false;
  } finally {
    validating.value = false;
  }
}

function confirmSqlEdit() {
  const s = sqlEditorText.value || "";
  try {
    const fmt = sqlFormat(s, { language: "postgresql" });
    if (currentNode.value) {
      currentNode.value.sql_text = fmt;
    }
    closeSqlDialog();
  } catch (e) {
    sqlEditError.value = "格式化失败，请检查语法";
  }
}

watch(sqlEditorText, () => {
  sqlCheckPassed.value = false;
});

async function handleParentColsVisible(visible: boolean) {
  if (visible && parentColumns.value.length === 0 && currentNode.value?.parent_id) {
    await loadParentColumns();
  }
}

async function loadParentColumns() {
  if (!currentNode.value?.parent_id) return;
  const parent = findNode(treeData.value, currentNode.value.parent_id);
  if (parent && parent.sql_text) {
    loadingParentCols.value = true;
    try {
      const res = await API.validateSql({ sql_text: parent.sql_text });
      if (res.data.data.valid) {
        parentColumns.value = res.data.data.columns;
      } else {
        ElMessage.warning("父节点SQL校验未通过，无法获取字段");
      }
    } catch (e) {
      console.error(e);
    } finally {
      loadingParentCols.value = false;
    }
  } else {
    ElMessage.warning("未找到父节点配置");
  }
}

function findNode(nodes: PxmDataDrillNode[], id: number): PxmDataDrillNode | null {
  for (const node of nodes) {
    if (node.id === id) return node;
    if (node.children) {
      const found = findNode(node.children, id);
      if (found) return found;
    }
  }
  return null;
}

async function handleUpdateNode() {
  if (!currentNode.value?.id) return;
  if (!currentNode.value.node_name) {
    ElMessage.warning("请输入节点名称");
    return;
  }
  if (!currentNode.value.sql_text) {
    ElMessage.warning("请输入SQL");
    return;
  }
  if (currentNode.value.parent_id) {
    if (!currentNode.value.link_field || !currentNode.value.param_name) {
      ElMessage.warning("请配置父级关联字段和参数名");
      return;
    }
  }

  saving.value = true;
  try {
    await API.updateNode(currentNode.value.id, currentNode.value);
    ElMessage.success("保存成功");
    refreshTree();
  } catch (e) {
    console.error(e);
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.drill-config-container {
  display: flex;
  height: 600px;
  border: 1px solid #eee;
}
.left-tree {
  width: 300px;
  border-right: 1px solid #eee;
  padding: 10px;
  display: flex;
  flex-direction: column;
}
.tree-toolbar {
  margin-bottom: 10px;
  display: flex;
  gap: 5px;
}
.right-form {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}
.text-success {
  color: #67c23a;
}
.text-danger {
  color: #f56c6c;
}
.form-tip {
  margin-top: 4px;
  line-height: 1.4;
}

.code-input {
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  min-height: 360px;
  width: 100%;
}
.code-input--error {
  border-color: var(--el-color-danger);
}
:deep(.CodeMirror) {
  height: 100%;
  width: 100%;
}

/* SQL Static Display Styles */
.code-static {
  padding: 8px;
  overflow: auto;
  background-color: var(--el-fill-color-blank);
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New",
    monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: normal;
  word-break: break-word;
}

.cm-theme-dracula {
  background: #282a36;
  color: #f8f8f2;
}

:deep(.cm-keyword) {
  color: #bd93f9;
  font-weight: 600;
}
:deep(.cm-def) {
  color: #50fa7b;
}
:deep(.cm-variable) {
  color: #f8f8f2;
}
:deep(.cm-string) {
  color: #f1fa8c;
}
:deep(.cm-number) {
  color: #8be9fd;
}
:deep(.cm-comment) {
  color: #6272a4;
}
</style>
