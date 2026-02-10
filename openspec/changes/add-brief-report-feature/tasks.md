## 1. 后端插件基础架构

- [x] 1.1 创建 `backend/app/plugin/module_brief` 目录及其初始化文件 `__init__.py`
- [x] 1.2 定义 `BriefReport` 数据库模型 (`model.py`) 并执行数据库初始化
- [x] 1.3 定义 Pydantic Schema 用于 API 输入输出校验 (`schema.py`)
- [x] 1.4 创建基础 CRUD 操作 (`crud.py`)

## 2. 核心业务逻辑实现

- [x] 2.1 实现 Excel 解析服务，提取关键列并转换为 JSON (`service.py`)
- [x] 2.2 实现 Dify API 异步调用工具，处理工作流请求 (`service.py`)
- [x] 2.3 开发 FastAPI 路由控制器，暴露 `/upload`、`/list`、`/{id}` 接口 (`controller.py`)

## 3. 前端界面开发

- [x] 3.1 创建“智能简报”菜单项并配置 Vue 路由
- [x] 3.2 实现工单上传与进度反馈组件 (`BriefUpload.vue`)
- [x] 3.3 实现分析报告列表页面 (`BriefList.vue`)
- [x] 3.4 实现 Markdown 渲染预览页面 (`BriefDetail.vue`)

## 4. 集成验证与调优

- [x] 4.1 进行端到端的功能测试（上传 -> AI 处理 -> 结果展示）
- [x] 4.2 优化 Dify API 调用超时处理和错误重试机制
