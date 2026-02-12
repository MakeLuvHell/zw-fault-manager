import request from '@/utils/request';

/**
 * 上传Excel并生成智能分析简报
 * @param data FormData { file: File, focus: string }
 */
export function generateBriefReport(data: FormData) {
  return request({
    url: '/brief/generate',
    method: 'post',
    data: data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/**
 * 分页获取历史分析报告列表
 * @param query { page_no: number, page_size: number }
 */
export function listBriefReport(query: any) {
  return request({
    url: '/brief/list',
    method: 'get',
    params: query
  });
}

/**
 * 获取分析报告详细内容
 * @param id 报告ID
 */
export function getBriefReportDetail(id: number | string) {
  return request({
    url: `/brief/${id}`,
    method: 'get'
  });
}
