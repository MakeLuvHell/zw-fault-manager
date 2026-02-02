from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin


class JobModel(ModelMixin, UserMixin):
    """
    定时任务调度表
    - 0: 运行中
    - 1: 暂停中
    """

    __tablename__: str = "app_job"
    __table_args__: dict[str, str] = {"comment": "定时任务调度表"}
    __loader_options__: list[str] = ["job_logs", "created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default="", comment="任务名称"
    )
    jobstore: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default="default", comment="存储器"
    )
    executor: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default="default", comment="执行器"
    )
    trigger: Mapped[str] = mapped_column(String(64), nullable=False, comment="触发器")
    trigger_args: Mapped[str | None] = mapped_column(Text, nullable=True, comment="触发器参数")
    func: Mapped[str] = mapped_column(Text, nullable=False, comment="任务函数")
    args: Mapped[str | None] = mapped_column(Text, nullable=True, comment="位置参数")
    kwargs: Mapped[str | None] = mapped_column(Text, nullable=True, comment="关键字参数")
    coalesce: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        comment="是否合并运行",
    )
    max_instances: Mapped[int] = mapped_column(
        Integer, nullable=True, default=1, comment="最大实例数"
    )
    start_date: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="开始时间")
    end_date: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="结束时间")

    # 关联关系
    # job_logs: Mapped[list["JobLogModel"] | None] = relationship(
    #     back_populates="job", lazy="selectin"
    # )


class JobLogModel(ModelMixin):
    """
    定时任务调度日志表
    """

    __tablename__: str = "app_job_log"
    __table_args__: dict[str, str] = {"comment": "定时任务调度日志表"}
    __loader_options__: list[str] = ["job"]

    job_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="任务名称")
    job_group: Mapped[str] = mapped_column(String(64), nullable=False, comment="任务组名")
    job_executor: Mapped[str] = mapped_column(String(64), nullable=False, comment="任务执行器")
    invoke_target: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="调用目标字符串"
    )
    job_args: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default="", comment="位置参数"
    )
    job_kwargs: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default="", comment="关键字参数"
    )
    job_trigger: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default="", comment="任务触发器"
    )
    job_message: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default="", comment="日志信息"
    )
    exception_info: Mapped[str | None] = mapped_column(
        String(2000), nullable=True, default="", comment="异常信息"
    )

    # 任务关联
    job_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, comment="任务ID"
    )

    # 由于移除了外键，这里使用 primaryjoin 进行逻辑关联，或者直接移除 relationship
    # 为了兼容现有代码，尝试保留逻辑关联（如果 SQLAlchemy 支持无外键关联），
    # 但通常跨类型关联（Int vs String）比较麻烦。
    # 考虑到日志主要是记录，且 app_job 可能不存在对应记录（外呼任务），
    # 最好是将 job 属性改为可选，或者暂时移除 relationship 如果没有代码强依赖它。
    # 检查代码发现 ap_scheduler.py 中并没有用到 log.job 属性。
    # 稳妥起见，我们移除 relationship，避免 ORM 查询错误。

