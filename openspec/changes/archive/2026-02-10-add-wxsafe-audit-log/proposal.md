## 为什么

为了满足网信安业务对敏感数据修改的合规性要求，同时防止多人协作核查时产生数据冲突和责任不清的问题，需要对“涉诈信息核查”过程中的数据变更进行全量留痕和可追溯管理。

## 变更内容

1.  **数据库变更**：新增 `wxsafe.wxsafe_fz_log` 表，用于存储操作日志（操作人、时间、变更前快照、变更后快照）。
2.  **后端逻辑变更**：
    *   在更新涉诈信息（核查补录）时，自动计算差异并记录日志。
    *   新增获取指定线索变更历史的 API。
3.  **前端交互变更**：
    *   在“涉诈信息核查”页面的详情弹窗或列表中，增加查看“操作日志/历史轨迹”的入口。
    *   以时间轴（Timeline）形式展示变更记录，高亮显示修改的具体字段。

## 功能 (Capabilities)

### 新增功能
- `wxsafe-audit`: 涉诈信息操作审计功能，负责日志的结构化存储、差异比对及查询服务。

### 修改功能
- `wxsafe`: 网信安涉诈信息管理核心功能。需修改其更新逻辑，集成审计日志记录机制。

## 影响

*   **Database**: 新增表 `wxsafe.wxsafe_fz_log`。
*   **Backend**: 
    *   修改 `WxSafeService.update_wx_safe_investigation` 方法。
    *   新增 `WxSafeAuditService` (或集成在 `WxSafeService` 中)。
    *   新增 API `GET /wxsafe/info/logs/{clue_number}`。
*   **Frontend**: 
    *   修改 `views/module_wxsafe/investigation/index.vue` 及相关组件。
    *   新增日志展示组件。
