## 1. 基础环境与模型

- [x] 1.1 安装 `pandas` 和 `xlrd` 依赖，并更新 `backend/requirements.txt`。
- [x] 1.2 在 `backend/app/plugin/module_brief` 中初始化模块结构（info/model.py, schema.py, service.py, router.py）。
- [x] 1.3 定义 `BriefReport` SQLAlchemy 模型并创建数据库迁移脚本。
- [x] 1.4 定义 `BriefReport` 相关的 Pydantic Schema (Create, Response, Summary)。

## 2. 后端核心逻辑

- [x] 2.1 实现 Excel 解析服务：使用 Pandas 读取上传文件，校验必要列。
- [x] 2.2 实现数据统计服务：按分类、角色聚合数据，提取 Top 关键词，生成 JSON 摘要。
- [x] 2.3 配置 Dify 客户端：在 `backend/app/core/config` 或模块内配置 Dify API Key 和 Base URL。
- [x] 2.4 实现 Dify 调用服务：封装 HTTP 请求，将统计摘要发送给 Dify Workflow 并获取响应。
- [x] 2.5 集成完整流程：在 Service 层串联“解析 -> 统计 -> Dify生成 -> 入库保存”。

## 3. 接口层实现

- [x] 3.1 实现上传分析接口 `POST /api/brief/generate`。
- [x] 3.2 实现历史列表查询接口 `GET /api/brief/list`。
- [x] 3.3 实现详情查看接口 `GET /api/brief/{id}`。
- [x] 3.4 注册 Router 到 FastAPI 主应用。

## 4. 前端实现

- [x] 4.1 定义前端 API 接口文件 `frontend/src/api/module_brief/index.ts`。
- [x] 4.2 创建“智能简报”主页面组件 `BriefReportIndex.vue`。
- [x] 4.3 实现 Excel 上传与参数输入表单（关注点）。
- [x] 4.4 实现 Markdown 报告展示组件（集成 markdown-it 或现有渲染器）。
- [x] 4.5 联调前后端接口，验证完整流程。
