# 待办事项：外呼模块严重故障修复 (UniqueViolationError)

**创建日期**: 2026-02-04
**优先级**: 高 (High)
**状态**: 待处理

## 1. 故障描述
线上环境在外呼任务执行后，回写数据库时发生严重错误，导致整个批次的流水日志丢失。

**错误日志**:
```
sqlalchemy.dialects.postgresql.asyncpg.IntegrityError: duplicate key value violates unique constraint "call_history_pkey"
DETAIL: Key (mobile_phone)=(17777601413) already exists.
```

## 2. 问题分析 (Root Cause Analysis)

### 2.1 根本原因
1.  **源数据未去重**：`CallTask` 生成逻辑（Step 2）仅过滤了历史表中已存在的号码 (`NOT EXISTS`)，但**未对本次查询出的源数据进行自身去重**。如果源表（如工单表）中同一个手机号有多条记录（例如多条工单），查询结果就会包含重复号码。
2.  **推送逻辑缺陷**：程序遍历重复的号码列表，导致对同一用户进行了多次 API 推送。
3.  **回写机制脆弱**：Step 5 使用 `db.add_all()` 批量插入 `CallHistory`。由于 `mobile_phone` 是主键，当列表中有重复号码（或与库中已有号码冲突）时，触发唯一键约束冲突，导致整个事务回滚。

### 2.2 后果
*   **重复外呼**：用户短时间内收到多个电话。
*   **数据丢失**：由于事务回滚，虽然电话打出去了，但系统内没有任何 `CallLog` 流水记录，也无法更新 `CallHistory`，造成“打过电话但系统不知道”的数据不一致。

## 3. 修复方案 (Fix Plan)

建议采用 **双重保险** 策略修复：

### 3.1 修复点 1：应用层去重 (Service.py)
在 Step 2 获取到数据库记录后，在生成 `tasks` 列表前进行去重。

**代码修改建议 (`backend/app/plugin/module_calling/service.py`)**:
```python
# 修改前
for row in rows:
    task = CallTask(...)
    tasks.append(task)

# 修改后 (建议)
seen_mobiles = set()
tasks = []
for row in rows:
    mobile = str(row[0]) if row[0] else ""
    if not mobile or mobile in seen_mobiles:
        continue  # 跳过空号或重复号
    
    seen_mobiles.add(mobile)
    task = CallTask(
        mobile_phone=mobile,
        # ... 其他字段
    )
    tasks.append(task)
```

### 3.2 修复点 2：数据库回写改用 UPSERT (Service.py)
将 Step 5 的直接插入改为“存在则更新”，作为最后的防线，防止并发或其他情况下的冲突导致事务崩溃。

**代码修改建议**:
需引入: `from sqlalchemy.dialects.postgresql import insert`

```python
# 修改前
if success_tasks:
    history_records = [...]
    db.add_all(history_records)

# 修改后 (建议)
if success_tasks:
    # 构造字典列表
    data_list = [
        {
            "mobile_phone": t.mobile_phone,
            "staff_name": t.staff_name,
            "sys_name": t.sys_name,
            "order_type": t.order_type,
            "order_nums": t.order_nums,
            "updated_time": datetime.now() # 假设有此字段
        } for t in success_tasks
    ]
    
    # 构建 UPSERT 语句
    stmt = insert(CallHistory).values(data_list)
    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=['mobile_phone'],  # 冲突键
        set_={
            "staff_name": stmt.excluded.staff_name,
            "sys_name": stmt.excluded.sys_name,
            "order_type": stmt.excluded.order_type,
            "order_nums": stmt.excluded.order_nums,
            # "updated_time": stmt.excluded.updated_time
        }
    )
    await db.execute(do_update_stmt)
```

## 4. 后续优化 (Optional)
*   考虑在 SQL 查询层直接加入 `DISTINCT` 关键字。
*   考虑为 `CallHistory` 添加自增 ID 主键，解除 `mobile_phone` 的物理主键约束（但这涉及表结构变更，成本较高）。
