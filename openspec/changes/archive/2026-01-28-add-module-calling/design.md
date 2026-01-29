# 设计：自动外呼模块 (Module Calling)

## 上下文
原 `calling_v1` 项目核心逻辑为：定时从 `call_task` 表读取数据，与 `call_history` 表比对去重后，调用第三方 API 推送数据，并更新历史表。

## 目标 / 非目标
- **目标**：
    - 实现与原项目一致的业务逻辑（去重、重试、推送）。
    - 采用全异步架构 (FastAPI + SQLAlchemy Async + HTTPX)。
    - 利用 Redis 实现分布式锁和序列号生成。
    - 集成到现有系统的日志和调度体系中。
- **非目标**：
    - 改变原有的第三方 API 接口契约。
    - 提供复杂的前端管理界面（本阶段仅后端实现）。
    - 增加额外的监控、日志表或熔断机制（保持基础版逻辑）。

## 决策

### 1. 模块化架构
在 `backend/app/plugin/module_calling` 下实现。

### 2. 异步 HTTP 客户端
使用 `httpx.AsyncClient`，以避免在定时任务执行时阻塞事件循环。

### 3. 分布式流水号生成
使用 Redis 的 `INCR` 命令维护毫秒级时间戳下的序列号，格式为 `YYYYMMDDHHmmss + 3位序列号`，确保分布式唯一性。

### 4. 数据库事务管理
使用 SQLAlchemy 的 `AsyncSession` 上下文管理器，确保“清空历史”和“插入新历史”在同一事务中完成。

### 5. 任务调度
利用 `app.plugin.module_application.job.tools.ap_scheduler.SchedulerUtil`。通过代码直接注册任务，简化部署。

## 风险 / 权衡
- **风险**：第三方 API 响应慢可能导致任务执行时间过长。
- **缓解**：`httpx` 设置合理的 `timeout`，且 APScheduler 配置 `max_instances=1` 防止任务堆积。

## 迁移计划
1. 定义数据模型。
2. 实现核心 Service。
3. 注册定时任务。
