## 1. 后端实施
- [x] 1.1 更新 `DrillSQLValidateResponse` Schema，增加 `params: List[str]` 字段。
- [x] 1.2 修改 `DrillService.validate_sql`：
    - 使用 `sqlglot` 解析 SQL。
    - 提取绑定参数列表。
    - 移除 `WHERE` 子句生成清洗后的 SQL。
    - 执行清洗后的 SQL 获取列结构。
    - 返回 `valid=True`，并包含 `columns` 和 `params`。

## 2. 前端实施
- [x] 2.1 更新 `src/api/module_datadrill/data_drill_info.ts` 中的 `DrillSQLValidateResponse` 接口定义。
- [x] 2.2 修改 `DrillConfigTree.vue` 中的 `loadParamNameOptions` 方法，改为使用 API 返回的 `params` 填充下拉框。
