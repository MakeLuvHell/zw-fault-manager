import request from "@/utils/request";

const API_PATH = "/calling/task";
const METADATA_PATH = "/calling/metadata";

/**
 * 字段映射配置
 */
export interface FieldMapping {
  mobile_phone: string;
  staff_name: string;
  sys_name: string;
  order_type: string;
  order_nums: string;
}

/**
 * 外呼任务创建/更新表单
 */
export interface CallingTaskForm {
  name: string;
  cron_expr: string;
  source_schema: string;
  source_table: string;
  is_enabled: boolean;
  remark?: string;
  field_mapping: FieldMapping;
}

/**
 * 外呼任务信息
 */
export interface CallingTaskInfo extends CallingTaskForm {
  id: number;
  created_time: string;
  updated_time: string;
}

/**
 * 外呼任务查询参数
 */
export interface CallingTaskQuery extends PageQuery {
  name?: string;
  source_table?: string;
  is_enabled?: boolean;
}

/**
 * Schema 信息
 */
export interface SchemaInfo {
  schema_name: string;
}

/**
 * 表信息
 */
export interface TableInfo {
  table_name: string;
  table_comment?: string;
}

/**
 * 列信息
 */
export interface ColumnInfo {
  column_name: string;
  data_type: string;
  column_comment?: string;
  is_nullable: boolean;
}

/**
 * 外呼日志信息
 */
export interface CallLogInfo {
  id: number;
  mobile_phone: string;
  staff_name: string;
  sys_name: string;
  order_type: string;
  order_nums: number;
  status: number;
  error_msg?: string;
  push_time: string;
}

export const CallingTaskAPI = {
  /**
   * 获取任务列表
   */
  listTask(query: CallingTaskQuery) {
    return request<ApiResponse<PageResult<CallingTaskInfo[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  /**
   * 获取任务详情
   */
  detailTask(id: number) {
    return request<ApiResponse<CallingTaskInfo>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  /**
   * 创建任务
   */
  createTask(data: CallingTaskForm) {
    return request<ApiResponse<CallingTaskInfo>>({
      url: `${API_PATH}/create`,
      method: "post",
      data,
    });
  },

  /**
   * 更新任务
   */
  updateTask(id: number, data: CallingTaskForm) {
    return request<ApiResponse<CallingTaskInfo>>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data,
    });
  },

  /**
   * 删除任务
   */
  deleteTask(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  /**
   * 立即执行任务
   */
  executeTask(id: number) {
    return request<ApiResponse>({
      url: `${API_PATH}/execute/${id}`,
      method: "post",
    });
  },

  /**
   * 获取执行日志
   */
  getLogs(limit: number = 100) {
    return request<ApiResponse<CallLogInfo[]>>({
      url: `${API_PATH}/logs`,
      method: "get",
      params: { limit },
    });
  },
};

export const MetadataAPI = {
  /**
   * 获取 Schema 列表
   */
  getSchemas() {
    return request<ApiResponse<SchemaInfo[]>>({
      url: `${METADATA_PATH}/schemas`,
      method: "get",
    });
  },

  /**
   * 获取表列表
   */
  getTables(schemaName: string) {
    return request<ApiResponse<TableInfo[]>>({
      url: `${METADATA_PATH}/tables`,
      method: "get",
      params: { schema_name: schemaName },
    });
  },

  /**
   * 获取列列表
   */
  getColumns(schemaName: string, tableName: string) {
    return request<ApiResponse<ColumnInfo[]>>({
      url: `${METADATA_PATH}/columns`,
      method: "get",
      params: { schema_name: schemaName, table_name: tableName },
    });
  },
};

export default CallingTaskAPI;

