# 项目 上下文

## 目的
FastApiAdmin (zw-fault-manager) 是一个现代化全栈快速开发平台，旨在为企业级中后台系统提供高效、稳定、可扩展的解决方案。它强调模块化设计、高性能异步处理以及与 AI 智能体（基于 LangChain）的集成。

## 技术栈
### 后端
- **语言/框架**: Python 3.10+, FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据库迁移**: Alembic
- **定时任务**: APScheduler
- **验证/配置**: Pydantic 2.0, Pydantic Settings
- **日志**: Loguru
- **认证**: PyJWT (JWT + OAuth2), Passlib, RBAC 权限控制
- **AI/智能体**: LangChain, LangGraph
- **并发**: Uvicorn, Gunicorn

### 前端
- **核心框架**: Vue 3, Vite, TypeScript
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式**: Sass, UnoCSS, Autoprefixer
- **工具库**: VueUse, Axios, Dayjs, ECharts

### 基础设施
- **容器化**: Docker, Docker Compose
- **Web 服务器/代理**: Nginx
- **缓存/中间件**: Redis
- **数据库支持**: MySQL 8.0+, PostgreSQL 17+, SQLite

## 项目约定

### 代码风格
- **Python**: 遵循 PEP 8 规范。
    - 使用 **Ruff** 进行 linting 和格式化。
    - 每行最大长度: 100 字符。
    - 缩进: 4 个空格。
    - 引用符号: 双引号。
- **前端**: 遵循 ESLint, Prettier 和 Stylelint 规范。
    - 缩进: 2 个空格 (标准 Web 约定)。
    - 使用 `pnpm` 作为包管理器。

### 架构模式
- **插件化后端架构**: 
    - 业务逻辑应在 `backend/app/plugin/module_xxx` 下开发。
    - **自动路由发现**: 系统自动扫描插件目录下的 `controller.py`。
    - **分层模型**: 控制器 (Controller) -> 业务层 (Service) -> 数据访问层 (CRUD) -> 数据模型 (Model) / 验证模型 (Schema)。
- **前后端分离**: 通过 RESTful API 进行通信。
- **权限控制**: 所有 API 接口必须添加权限控制依赖 (`AuthPermission`)。
- **统一响应**: 使用 `SuccessResponse` 或 `ErrorResponse` 返回标准 JSON。

### 测试策略
- **后端**: 使用 `pytest` 进行单元测试和集成测试，位于 `backend/tests/`。
- **前端**: 使用 `vitest` 和 `Vue Test Utils`。

### Git 工作流
- **提交规范**: 使用 **Commitizen (cz-git)** 进行规范化提交。
- **Hooks**: 使用 **Husky** 在提交前执行代码风格检查和格式化。

## 领域上下文
- **故障管理**: 根据项目名 `zw-fault-manager`，该系统可能用于设备或软件系统的故障监测、记录和处理。
- **后台管理**: 包含完整的用户、角色、部门、岗位、字典、参数配置等基础管理功能。

## 重要约束
- 插件模块名必须以 `module_` 开头。
- 控制器文件必须命名为 `controller.py` 才能被自动识别。
- 环境配置文件（`.env.dev`, `.env.prod`）必须根据 `.example` 文件正确配置。

## 外部依赖
- **Redis**: 核心缓存和限流组件。
- **MySQL/PostgreSQL**: 核心数据存储。
- **AI APIs**: 如 OpenAI, Anthropic (通过 LangChain 集成)。