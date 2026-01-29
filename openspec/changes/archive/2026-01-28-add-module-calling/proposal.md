# 变更：集成自动外呼模块 (Module Calling)

## 为什么
目前的自动外呼功能 (`calling_v1`) 是一个独立的 Python 脚本项目，无法享受 `zw-fault-manager` 主平台提供的统一鉴权、日志监控、数据库连接池管理和分布式调度能力。
为了降低维护成本并提升系统稳定性，需要将其迁移为 `zw-fault-manager` 的一个标准插件模块。

## 变更内容
- **新增插件模块**：`backend/app/plugin/module_calling`。
- **数据库迁移**：将原生的 SQL 表结构转换为 SQLAlchemy 异步模型 (`CallTask`, `CallHistory`)。
- **逻辑重构**：
    - 使用 `httpx` 替代 `requests` 进行异步 HTTP 请求。
    - 使用平台现有的 `SchedulerUtil` 替代原生的 `APScheduler` 初始化代码。
    - 使用 Redis 替代内存锁生成全局唯一的 `distinct_id`。
- **配置集成**：将 API 地址、Keys 等配置移入 `app/config/setting.py`。

## 影响
- **受影响规范**：新增 `calling` 规范。
- **受影响代码**：
    - `backend/app/plugin/init_app.py` (注册模块)
    - `backend/app/config/setting.py` (新增配置)
    - 数据库将新增两张表（或复用现有表结构但由 ORM 管理）。
