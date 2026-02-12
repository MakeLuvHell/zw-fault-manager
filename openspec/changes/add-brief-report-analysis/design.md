## 上下文

当前易问单数据分析主要依赖人工处理 Excel，效率低下。我们需要一个自动化系统，能够接收 Excel 文件，进行数据统计，并利用 LLM 生成分析报告。系统将基于现有的 `FastAPI` 后端和 `Vue3` 前端架构，并集成 Dify 作为 AI 引擎。

## 目标 / 非目标

**目标：**
- 实现 Excel 文件上传与解析（支持 `.xls`, `.xlsx`）。
- 实现基于 Pandas 的数据清洗与多维度统计（分类、角色、关键词）。
- 集成 Dify 工作流 API，生成自然语言分析简报。
- 持久化存储分析报告历史。
- 提供前端界面供用户交互和查看结果。

**非目标：**
- 实现实时的流式分析（目前采用同步或异步任务等待模式）。
- 在 Dify 侧进行复杂的原始数据清洗（清洗逻辑在后端完成）。

## 决策

### 1. 数据处理策略：后端预计算 (Pandas) vs 全量传 LLM
**决策**: 采用 **后端预计算** 策略。
**理由**:
- **成本与性能**: 原始 Excel 可能包含数千行数据，直接传给 LLM 会消耗大量 Token 且容易超时。
- **准确性**: Pandas 在统计计数（如“某分类有多少单”）上绝对精准，而 LLM 容易产生幻觉。
- **流程**: 后端使用 Pandas 计算出 `summary`（包含 Top 分类、数量、关键词等），仅将这个轻量级的 JSON 摘要传给 Dify。

### 2. Dify 集成方式
**决策**: 使用 **Dify Workflow API** (Run Workflow)。
**理由**:
- 工作流模式允许我们在 Dify 侧编排 Prompt 和参数，而不需要在后端硬编码 Prompt。
- 我们将定义一个接受 `statistical_summary` 和 `focus` (关注点) 的工作流。

### 3. 数据存储模型
**决策**: 使用 PostgreSQL (SQLAlchemy) 存储报告记录。
**模型设计**:
```python
class BriefReport(BaseModel):
    __tablename__ = 'brief_report'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, comment="源文件名")
    focus = Column(String(500), nullable=True, comment="分析关注点")
    summary_data = Column(JSON, nullable=False, comment="统计摘要数据(JSON)")
    report_content = Column(Text, nullable=False, comment="LLM生成的报告内容")
    report_date = Column(Date, nullable=False, comment="报告所属月份(从文件名提取或当前时间)")
    creator_id = Column(Integer, nullable=True, comment="创建人ID")
```

### 4. 异步处理
**决策**: 初版采用 **同步等待** (FastAPI直接返回) 或 **简单的后台任务**。
**理由**: 考虑到并发量较低（内部管理使用），且 Pandas 处理几千行数据通常在秒级，Dify 生成在 10-20秒左右，前端加 Loading 遮罩即可，暂不引入复杂的 Celery 任务队列。

## 风险 / 权衡

- **风险**: Dify 接口超时或生成失败。
  - **缓解**: 后端设置合理的超时时间（如 60s），并做好异常捕获，保存“失败”状态或仅保存统计数据。
- **风险**: Excel 格式变更导致解析失败。
  - **缓解**: 增加列名校验逻辑，如果缺少关键列（如“自分类”）明确报错。

## 迁移计划

1.  添加 `pandas`, `xlrd` 到 `requirements.txt`。
2.  执行数据库迁移创建 `brief_report` 表。
3.  配置 Dify API Key 到环境变量。
