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
 * 下载导入模板
 */
export function downloadWxSafeTemplate() {
  return request({
    url: '/wxsafe/info/template',
    method: 'get',
    responseType: 'blob'
  });
}
