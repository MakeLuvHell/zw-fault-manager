# 设计：网信安分表架构与功能同步

## 1. 数据库模型 (Database Models)

### 主表: `t_wx_safe_info`
*   `clue_number` (PK)
*   `phone_number`
*   `join_location` (保留以便过滤)
*   `is_compliant` 等 9 个核查字段
*   审计字段 (created_time, updated_time)

### 附表: `t_wx_safe_detail`
*   `clue_number` (PK/FK)
*   `phone_number` (冗余以供外部查询)
*   画像字段 (join_date, owner_name, staff_name 等 18 个字段)

## 2. 后端适配 (Backend Adaptation)

### 数据展平逻辑
在 `WxSafeInfoInDB` 模式中使用 `model_validator(mode="before")`，自动将关联的 `detail` 对象字段合并到父级字典中。这保证了 REST API 返回的 JSON 结构与拆分前保持 100% 兼容。

### 写入原子性
重写 `CRUDWxSafe.create` 方法，使用 `auth.db.add()` 同时操作主附两个 ORM 对象，并确保在同一个数据库会话中 flush，保证数据一致性。

## 3. 前端交互 (Frontend Interaction)

### 核查 Tab 逻辑
*   **状态判定**：`is_compliant` 为 NULL 为待核查，非 NULL 为已核查。
*   **实时统计**：每次列表刷新后调用 `/counts` 接口更新角标。
*   **体验优化**：切换 Tab 时立即清空列表，防止数据闪烁。
