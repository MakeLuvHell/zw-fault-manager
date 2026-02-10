# 网信安涉诈信息管理模块规范 (WxSafe Info Spec)

## 1. 概述
本模块用于管理网信安相关的涉诈线索信息，提供数据的录入、查询、导入和统计功能。
数据存储在独立的数据库 Schema `wxsafe` 中，以支持“大表”结构（36+字段）。

## 2. 数据模型 (Data Model)

### 2.1 数据库表：`t_wx_safe_info`
*   **Schema**: `wxsafe`
*   **Primary Key**: `clue_number` (线索编号)

| 字段名 | 类型 | 说明 | 备注 |
| :--- | :--- | :--- | :--- |
| **clue_number** | VARCHAR(100) | 线索编号 | 主键，唯一 |
| **category** | VARCHAR(50) | 涉诈或涉案 | |
| **phone_number** | VARCHAR(20) | 业务号码 | 必须为11位数字 |
| **report_month** | VARCHAR(20) | 月份 | |
| **incident_time** | TIMESTAMP | 涉诈（涉案）时间 | |
| **city** | VARCHAR(100) | 涉诈涉案地（城市） | |
| **fraud_type** | VARCHAR(100) | 涉诈类型 | |
| **victim_number** | TEXT | 受害人号码 | |
| **join_date** | TIMESTAMP | 入网时间 | |
| **online_duration** | INTEGER | 在网时长（月） | |
| **install_type** | VARCHAR(50) | 新装或存量 | |
| **join_location** | VARCHAR(100) | 入网属地 | |
| **is_local_handle** | VARCHAR(50) | 属地或非属地办理 | |
| **owner_name** | VARCHAR(100) | 机主名称 | |
| **cert_address** | VARCHAR(255) | 证件地址 | |
| **customer_type** | VARCHAR(50) | 政企或个人 | |
| **other_phones** | TEXT | 名下手机号码 | |
| **age** | INTEGER | 年龄 | |
| **agent_name** | VARCHAR(100) | 代理商 | |
| **store_name** | VARCHAR(100) | 受理厅店 | |
| **staff_id** | VARCHAR(50) | 受理人工号 | |
| **staff_name** | VARCHAR(100) | 受理人 | |
| **concurrent_cards** | TEXT | 关联卡号 | |
| **package_name** | VARCHAR(100) | 套餐名称 | |
| **is_fusion_package** | VARCHAR(50) | 是否融合套餐 | |
| **has_broadband** | VARCHAR(50) | 是否有宽带 | |
| **card_type** | VARCHAR(50) | 主卡/副卡 | |
| **is_compliant** | VARCHAR(50) | 是否合规受理 | |
| **has_resume_before** | VARCHAR(50) | 涉诈前是否复通 | |
| **is_resume_compliant** | VARCHAR(50) | 复通是否规范 | |
| **responsibility** | VARCHAR(100) | 责任认定 | |
| **is_self_or_family** | VARCHAR(50) | 是否本人/亲属 | |
| **police_collab** | VARCHAR(255) | 警企协同情况 | |
| **investigation_note** | TEXT | 调查备注 | |
| **abnormal_scene** | TEXT | 异常场景识别 | |
| **feedback** | TEXT | 核查反馈 | |
| **created_time** | TIMESTAMP | 创建时间 | 自动生成 |
| **updated_time** | TIMESTAMP | 更新时间 | 自动更新 |

## 3. 接口规范 (API Spec)

所有接口位于 `/api/v1/wxsafe/info` 下。

### 3.1 查询列表
*   **Method**: `GET /list`
*   **Query Params**:
    *   `page_no`: 页码
    *   `page_size`: 每页数量
    *   `clue_number`: 线索编号（模糊查询）
    *   `phone_number`: 业务号码（模糊查询）
*   **Response**: 分页数据

### 3.2 单条创建
*   **Method**: `POST /create`
*   **Body**: JSON，包含前8个核心字段
*   **Validation**:
    *   `clue_number` 必须唯一。
    *   `phone_number` 必须为11位数字。

### 3.3 批量导入
*   **Method**: `POST /import`
*   **Body**: `multipart/form-data` (file)
*   **Logic**:
    *   解析 Excel 文件。
    *   强制转换 `report_month` 为字符串。
    *   校验每行数据的格式和唯一性。
    *   返回成功条数、失败条数及失败明细（含线索编号和原因）。

### 3.4 下载模板
*   **Method**: `GET /template`
*   **Response**: Excel 文件流

## 4. 业务逻辑需求 (Business Logic)

### 需求：更新操作必须触发审计记录
系统在处理任何针对涉诈信息的更新请求（包括单条更新、批量核查等）时，必须同步触发 `wxsafe-audit` 能力记录变更日志。

#### 场景：核查信息补录触发审计
- **当** 核查人员在“核查页面”提交补录信息
- **那么** `wxsafe` 模块在持久化更新数据的同时，必须调用审计服务记录此次变更
- **并且** 如果审计记录失败，更新操作应回滚（或记录错误日志，视一致性要求而定，建议强一致性）

## 5. 前端功能
*   **路径**: `src/views/module_wxsafe/info/index.vue`
*   **功能**:
    *   数据表格展示。
    *   录入弹窗。
    *   导入弹窗（含失败详情表格）。