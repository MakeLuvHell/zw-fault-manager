## 上下文

项目已具备成熟的插件发现机制（`discover.py`），支持自动挂载 `/app/plugin` 下的模块。目前需要新增一个名为 `brief` 的模块，专门处理“易问单”工单的 AI 智能分析。前端采用 Vue 3，需要一个新的交互页面来上传文件并展示报告。

## 目标 / 非目标

**目标：**
- 实现 `module_brief` 插件，提供 RESTful API。
- 使用 `pandas` 高效解析 Excel 工单数据，并转换为标准 JSON。
- 异步调用外部 Dify 工作流 API，避免阻塞 Web 服务。
- 存储分析结果（Markdown 格式）及元数据，支持历史追溯。
- 前端实现文件上传控件和 Markdown 渲染器。

**非目标：**
- 不对 Excel 原始文件进行长期存储（解析后即处理）。
- 本阶段不实现 Dify 工作流的在线编辑功能。

## 决策

1. **命名空间**: 顶级目录命名为 `module_brief`，自动映射 API 前缀 `/brief`。这与 `module_calling` 等既有模块保持风格一致。
2. **数据处理库**: 选择 `pandas` + `openpyxl`。理由：对于表格数据的解析和清洗，`pandas` 具有极高的健壮性和灵活性。
3. **通信协议**: 后端与 Dify 之间使用 `httpx` (Async)。理由：Dify API 响应可能在 10s-30s 之间，异步调用是保证并发性能的关键。
4. **数据模型**: 使用 SQLAlchemy 定义 `BriefReport` 表，核心字段包括 `original_data` (JSONB/Text), `analysis_content` (Markdown Text)。
5. **前端组件**: 使用 Element Plus 的 `Upload` 组件和 `v-md-editor` 进行展示。

## 风险 / 权衡

- **[风险] Dify API 超时** → **[缓解措施]** 前端实现加载状态展示，后端设置合理的超时时间（如 60s），并在必要时引入异步任务队列（虽然当前初步实现可先用 `asyncio.create_task`）。
- **[风险] Excel 格式不规范** → **[缓解措施]** 在 `service.py` 中增加严格的列名检查和数据校验。
- **[权衡] 数据库存储量** → 原始数据转为 JSON 存储会增加存储压力，但为了后续“基于历史报告的二次分析”，目前选择保留原始 JSON。
