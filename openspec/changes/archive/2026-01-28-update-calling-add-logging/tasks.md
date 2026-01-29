## 1. 数据模型变更
- [ ] 1.1 在 `model.py` 中新增 `CallLog` 类。
    - 字段：`id`, `mobile_phone`, `staff_name`, `sys_name`, `order_type`, `order_nums`
    - 新增审计字段：`status` (1=成功, 0=失败), `error_msg`, `push_time`。

## 2. 业务逻辑增强
- [ ] 2.1 修改 `CallingService.push_to_api` 方法，使其返回更详细的结果对象（包含 `status`, `error_msg` 等），而不仅仅是 bool。
- [ ] 2.2 修改 `CallingService.execute_task`：
    - 在循环推送过程中，收集所有的日志记录对象。
    - 在事务提交阶段，批量插入 `CallLog` 记录。
