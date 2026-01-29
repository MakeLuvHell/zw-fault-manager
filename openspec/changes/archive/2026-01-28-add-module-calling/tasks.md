## 1. 基础架构准备
- [ ] 1.1 创建目录结构 `backend/app/plugin/module_calling` (Service, CRUD, Model)。
- [ ] 1.2 在 `backend/app/config/setting.py` 中添加外呼相关的配置项 (API_URL, KEYS 等)。

## 2. 数据模型实现
- [ ] 2.1 创建 `model.py`：定义 `CallTask` 和 `CallHistory` 的 SQLAlchemy 模型。

## 3. 核心业务逻辑
- [ ] 3.1 创建 `service.py`：实现 `DistinctIdGenerator` (基于 Redis)。
- [ ] 3.2 实现 `CallingService`：
    - `get_new_tasks()`: 获取并筛选任务。
    - `push_to_api()`: 封装 `httpx` 请求与重试逻辑。
    - `update_history()`: 事务更新历史表。

## 4. 定时任务集成
- [ ] 4.1 创建 `tasks.py`：定义符合 APScheduler 调用的入口函数 `execute_calling_job`。
- [ ] 4.2 在 `backend/app/plugin/init_app.py` 或模块初始化文件中注册该任务。
