## 1. 数据库与模型

- [ ] 1.1 创建 `wxsafe_fz_log` 表的 SQL 迁移脚本 (`backend/sql/postgres/modules/wxsafe/log.sql`) 并执行。
- [ ] 1.2 在后端定义 `WxSafeLog` SQLAlchemy 模型 (`backend/app/plugin/module_wxsafe/info/model.py`)。
- [ ] 1.3 定义 Log 相关的 Pydantic Schema (`backend/app/plugin/module_wxsafe/info/schema.py`)。

## 2. 后端逻辑实现

- [ ] 2.1 在 `WxSafeService` 中实现变更差异计算逻辑 (`_calculate_diff`)。
- [ ] 2.2 修改 `update_wx_safe_investigation` 方法，集成日志记录功能。
- [ ] 2.3 实现获取日志列表的 Service 方法 (`get_wx_safe_logs`)。
- [ ] 2.4 在 `controller.py` 中暴露日志查询 API (`GET /wxsafe/info/logs/{clue_number}`)。

## 3. 前端交互实现

- [ ] 3.1 定义日志 API 接口文件 (`frontend/src/api/module_wxsafe/log.ts`)。
- [ ] 3.2 封装 Timeline 组件，用于展示格式化的差异日志。
- [ ] 3.3 修改 `InvestigationDialog.vue`，增加“历史记录” Tab 并集成 Timeline 组件。
