import request from "@/utils/request";

// Interfaces
export interface DataDrillInfo {
  id?: number;
  report_name?: string;
  status?: string;
  description?: string;
  nodes?: DataDrillNode[];
  created_time?: string;
  updated_time?: string;
  created_by?: any;
  updated_by?: any;
}

export interface DataDrillNode {
  id?: number;
  info_id?: number;
  parent_id?: number | null;
  node_name?: string;
  sql_text?: string;
  link_field?: string;
  param_name?: string;
  status?: string;
  description?: string;
  children?: DataDrillNode[];
}

export interface DrillSQLValidateRequest {
  sql_text: string;
}

export interface DrillSQLValidateResponse {
  valid: boolean;
  message: string;
  columns: string[];
  params: string[];
}

export interface DrillExecuteRequest {
  report_id: number;
  node_id: number;
  params: Record<string, any>;
  page_no?: number;
  page_size?: number;
}

export interface DrillExecuteResponse {
  columns: string[];
  data: any[];
  total: number;
}

// API
const apiPrefix = "/datadrill/data_drill_info";

export default {
  // Info CRUD
  list: (params: any) => request<any>({ url: apiPrefix + "/list", method: "get", params }),
  create: (data: any) => request<any>({ url: apiPrefix + "/create", method: "post", data }),
  update: (id: number, data: any) =>
    request<any>({ url: apiPrefix + "/update", method: "put", params: { id }, data }),
  delete: (ids: number[]) =>
    request<any>({ url: apiPrefix + "/delete", method: "delete", data: ids }),
  detail: (id: number) =>
    request<any>({ url: apiPrefix + "/detail", method: "get", params: { id } }),

  // Node CRUD
  createNode: (data: any) =>
    request<any>({ url: apiPrefix + "/node/create", method: "post", data }),
  updateNode: (id: number, data: any) =>
    request<any>({ url: apiPrefix + "/node/update", method: "put", params: { id }, data }),
  deleteNode: (ids: number[]) =>
    request<any>({ url: apiPrefix + "/node/delete", method: "delete", data: ids }),
  getNodeChildren: (parent_id: number) =>
    request<any>({ url: apiPrefix + "/node/children", method: "get", params: { parent_id } }),

  // Execute/Validate
  validateSql: (data: DrillSQLValidateRequest) =>
    request<any>({ url: apiPrefix + "/validate_sql", method: "post", data }),
  executeDrill: (data: DrillExecuteRequest) =>
    request<any>({ url: apiPrefix + "/execute", method: "post", data }),
};
