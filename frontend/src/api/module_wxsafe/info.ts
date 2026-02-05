import request from '@/utils/request';

/**
 * 获取涉诈信息列表
 */
export function listWxSafeInfo(query: any) {
  return request({
    url: '/wxsafe/info/list',
    method: 'get',
    params: query
  });
}

/**
 * 获取核查任务列表 (带属地过滤)
 */
export function listWxSafeInvestigation(query: any) {
  return request({
    url: '/wxsafe/info/investigation/list',
    method: 'get',
    params: query
  });
}

/**
 * 获取核查任务统计数量
 */
export function getWxSafeInvestigationCounts() {
  return request({
    url: '/wxsafe/info/investigation/counts',
    method: 'get'
  });
}

/**
 * 单条录入涉诈信息
 */
export function addWxSafeInfo(data: any) {
  return request({
    url: '/wxsafe/info/create',
    method: 'post',
    data: data
  });
}

/**
 * 批量导入涉诈信息
 */
export function importWxSafeInfo(data: FormData) {
  return request({
    url: '/wxsafe/info/import',
    method: 'post',
    data: data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/**
 * 核查信息补录
 */
export function updateWxSafeInvestigation(clue_number: string, data: any) {
  return request({
    url: `/wxsafe/info/investigation/${clue_number}`,
    method: 'put',
    data: data
  });
}

/**
 * 下载导入模板
 */
export function downloadWxSafeTemplate() {
  return request({
    url: '/wxsafe/info/template',
    method: 'get',
    responseType: 'blob'
  });
}

/**
 * 导出涉诈信息
 */
export function exportWxSafeInfo(query: any) {
  return request({
    url: '/wxsafe/info/export',
    method: 'post',
    params: query,
    responseType: 'blob'
  });
}
