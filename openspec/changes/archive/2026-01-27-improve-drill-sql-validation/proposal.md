# 变更：改进下钻报表 SQL 校验与参数解析

## 为什么
目前下钻报表的 SQL 校验功能存在两个主要问题：
1.  **校验报错**：当 SQL 包含绑定参数（如 `:province_name`）时，后端直接执行导致数据库报错“缺少参数值”，用户无法保存合法的参数化 SQL。
2.  **参数提示错误**：前端“参数名”下拉框使用的是 SQL 的**返回列**（Columns），而实际上用户需要选择的是**输入参数**（Bind Parameters）。这导致用户体验混乱，往往需要手动输入参数名。

## 变更内容
- **后端 (`DrillService`)**：
    - 引入 `sqlglot` 库对 SQL 进行静态分析。
    - 在校验执行前，**移除 WHERE 子句**，确保 `LIMIT 0` 查询能成功执行，无论是否包含参数。
    - 遍历语法树，**提取所有绑定参数**（Bind Parameters）。
    - 更新响应结构，返回 `params` 列表。
- **前端 (`DrillConfigTree`)**：
    - 更新 API 接口定义，增加 `params` 字段。
    - 修改下拉框数据源逻辑：优先使用后端分析出的 `params` 填充“参数名”选项。

## 影响
- **受影响规范**：下钻报表管理 (Data Drill Management)
- **受影响代码**：
    - `backend/app/plugin/module_datadrill/data_drill_info/service.py`
    - `backend/app/plugin/module_datadrill/data_drill_info/schema.py`
    - `frontend/src/api/module_datadrill/data_drill_info.ts`
    - `frontend/src/views/module_datadrill/data_drill_info/components/DrillConfigTree.vue`
