## 上下文

当前 `wxsafe` 模块缺乏对数据修改的审计能力。业务人员在核查过程中可能会多次修改责任认定、反馈信息等敏感字段，一旦出现争议或数据错误，无法追溯修改人和修改时间。

## 目标 / 非目标

**目标：**
*   建立涉诈信息操作日志表，存储所有变更记录。
*   实现“核查补录”操作的自动留痕。
*   提供前端界面查看单条线索的历史轨迹。

**非目标：**
*   暂不实现“一键回滚”功能（仅记录，不负责恢复）。
*   暂不记录“批量导入”产生的日志（导入通常是初始化，数据量大且无旧值，记录意义较小，且容易爆表。本次仅关注**人工修改**）。

## 决策

### 1. 日志存储结构
选用 **PostgreSQL JSONB** 存储变更前后的快照 (`before_data`, `after_data`)。
*   **理由**：涉诈信息字段较多（36+），如果针对每个字段建列太浪费；如果只存 diff 字符串又不利于后续结构化分析。JSONB 提供了灵活性和查询能力。

### 2. 差异计算时机
选择在 **Service 层** 进行差异计算。
*   **理由**：虽然数据库触发器也能做，但业务逻辑（如获取当前操作人信息）在应用层更方便获取。且 Service 层控制事务更灵活。

### 3. 前端展示形式
选择在 **InvestigationDialog** (核查弹窗) 中增加一个 "历史记录" Tab。
*   **理由**：核查人员在补录时最需要参考历史。列表页展开行虽然也可以，但弹窗空间更大，适合展示复杂的时间轴。

## 风险 / 权衡

*   **风险**: JSONB 存储虽然灵活，但会占用较多存储空间。
    *   **缓解**: 仅记录发生变化的字段的快照？不，为了完整性，建议记录完整快照（或至少记录完整的主表字段，因为附表字段变动少）。考虑到数据量级（万级/月），存储压力可控。
    *   **修正决策**：为了节省空间，`before_data` 和 `after_data` **仅存储发生变更的字段及其旧值/新值**，或者仅存储核心业务字段的快照。
    *   **最终方案**: 存储**完整的主表字段快照**。因为主表字段是核查重点，数量不多（10+个），全量存取便查询和回滚。

## 数据库设计

```sql
CREATE TABLE wxsafe.wxsafe_fz_log (
    id BIGSERIAL PRIMARY KEY,
    clue_number VARCHAR(100) NOT NULL,
    operator_id VARCHAR(50),
    operator_name VARCHAR(100),
    action_type VARCHAR(20) DEFAULT 'UPDATE',
    change_diff JSONB,  -- 存储差异 { "field": [old, new] }
    created_time TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_wxsafe_log_clue_number ON wxsafe.wxsafe_fz_log(clue_number);
```
*注：改为存储 `change_diff` 更直接，节省空间且前端渲染方便。*

## API 设计

*   `GET /wxsafe/info/logs/{clue_number}`: 返回 Log 列表。
