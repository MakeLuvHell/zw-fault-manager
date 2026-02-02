## 1. 后端实现
- [x] 1.1 新增外呼任务配置模型 `CallingTaskConfig`
- [x] 1.2 新增元数据服务：获取 Schema 列表、表列表、字段列表
- [x] 1.3 新增外呼任务 CRUD API 路由
- [x] 1.4 新增"立即执行"异步接口

## 2. 前端 API 层
- [x] 2.1 新增 `api/module_calling/task.ts` API 模块

## 3. 前端页面组件
- [x] 3.1 新增任务列表页面 `views/module_calling/task/index.vue`
- [x] 3.2 新增任务编辑弹窗组件 `views/module_calling/task/components/TaskEditModal.vue`
- [x] 3.3 新增 Cron 表达式选择组件（可选，复用或新建）

## 4. 路由与菜单
- [x] 4.1 数据库添加菜单配置
- [x] 4.2 添加权限配置

## 5. 验证
- [x] 5.1 前端页面功能测试
- [x] 5.2 后端 API 测试
