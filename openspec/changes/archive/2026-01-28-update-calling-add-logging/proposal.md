# 变更：增加外呼流水日志 (Add Call Logging)

## 为什么
目前的自动外呼模块仅维护一个瞬态的 `call_history` 表，每次任务执行都会清空重写。这导致无法追溯历史推送记录，一旦出现“用户未收到通知”的客诉，无法排查。
此外，失败的推送记录目前仅存在于文本日志中，不便于统计分析和监控。

## 变更内容
- **新增数据模型**：`CallLog`，用于永久存储每次推送的详细结果。
- **扩展业务逻辑**：在 API 推送结束后，无论成功或失败，都将结果写入 `call_log` 表。

## 影响
- **受影响代码**：
    - `backend/app/plugin/module_calling/model.py` (新增表结构)
    - `backend/app/plugin/module_calling/service.py` (新增写入逻辑)
- **数据库**：新增 `call_log` 表。
