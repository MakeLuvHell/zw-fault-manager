# 设计：网信安涉诈信息核查与数据隔离

**Author**: Gemini Agent
**Date**: 2026-02-04

## 1. 后端设计 (Backend Design)

### 1.1 数据隔离策略
*   **机制**：在 Service 层查询方法中注入过滤逻辑。
*   **匹配规则**：
    *   获取当前登录用户：`user = current_user`
    *   判断权限：`if not user.is_superuser`
    *   获取部门：`dept_name = user.dept.name` (需处理空值情况)
    *   构建查询：`query = query.where(WxSafeInfo.join_location.like(f"{dept_name}%"))`
    *   *注：采用前缀匹配以适应“广州分公司”匹配“广州”或“广州市”的情况。*

### 1.2 接口设计 (API)
#### A. 列表查询接口 (现有接口增强)
*   **URL**: `GET /wxsafe/info/list`
*   **变更**: 内部增加上述隔离逻辑，出参不变。

#### B. 核查补录接口 (新增)
*   **URL**: `PUT /wxsafe/info/investigation/{clue_number}`
*   **Method**: `PUT`
*   **Summary**: 更新涉诈信息的核查结果
*   **Request Body**: `WxSafeInfoInvestigationUpdate` (Schema 见下)
*   **Permission**:
    *   登录用户必须有权访问该 `clue_number` 对应的数据（复用隔离逻辑检查）。
    *   如果数据不存在或无权访问，返回 404 或 403。

### 1.3 Schema 定义
```python
class WxSafeInfoInvestigationUpdate(BaseModel):
    is_compliant: str | None
    has_resume_before: str | None
    is_resume_compliant: str | None
    responsibility: str | None
    is_self_or_family: str | None
    police_collab: str | None
    investigation_note: str | None
    abnormal_scene: str | None
    feedback: str | None
```

## 2. 前端设计 (Frontend Design)

### 2.1 菜单结构
```
网信安模块
  ├── 涉诈信息管理 (现有, path: /wxsafe/info)
  └── 涉诈信息核查 (新增, path: /wxsafe/investigation)
```

### 2.2 涉诈信息核查页面 (`views/module_wxsafe/investigation/index.vue`)
*   **布局**：
    *   **搜索栏**：线索编号、业务号码。
    *   **列表表格**：
        *   显示字段：线索编号、业务号码、涉诈类型、入网属地、涉诈时间。
        *   操作列：仅显示 **[核查]** 按钮。
*   **核查弹窗 (`InvestigationDialog.vue`)**：
    *   **Header**：显示当前操作的线索编号。
    *   **Info Section** (只读)：展示线索的基础信息，辅助判断。
    *   **Form Section** (可编辑)：展示上述 9 个字段。
        *   下拉框字段：`is_compliant` (是/否), `has_resume_before` (是/否) 等。
        *   文本框字段：`responsibility`, `investigation_note` 等。

### 2.3 权限控制
*   通过后端返回的菜单数据控制左侧菜单的显示（前提是 RBAC 系统已配置）。
*   本设计重点在于页面实现，菜单数据的插入通过 SQL 脚本提供。

## 3. 数据库变更 (Database Changes)
无表结构变更。
仅需插入新的菜单记录（SQL 待执行）。
