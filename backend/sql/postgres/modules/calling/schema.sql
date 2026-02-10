-- ----------------------------
-- 1. 初始化表结构 (外呼任务配置)
-- ----------------------------
CREATE SCHEMA IF NOT EXISTS calling;

CREATE TABLE IF NOT EXISTS calling.calling_task_config (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cron_expr VARCHAR(100) NOT NULL,
    source_schema VARCHAR(100) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    remark VARCHAR(500),
    field_mapping TEXT NOT NULL,
    created_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 添加注释
COMMENT ON TABLE calling.calling_task_config IS '外呼任务配置表';
COMMENT ON COLUMN calling.calling_task_config.id IS '任务ID';
COMMENT ON COLUMN calling.calling_task_config.name IS '任务名称';
COMMENT ON COLUMN calling.calling_task_config.cron_expr IS 'Cron 表达式';
COMMENT ON COLUMN calling.calling_task_config.source_schema IS '源数据 Schema';
COMMENT ON COLUMN calling.calling_task_config.source_table IS '源数据表名';
COMMENT ON COLUMN calling.calling_task_config.is_enabled IS '是否启用';
COMMENT ON COLUMN calling.calling_task_config.remark IS '备注';
COMMENT ON COLUMN calling.calling_task_config.field_mapping IS '字段映射 JSON';
COMMENT ON COLUMN calling.calling_task_config.created_time IS '创建时间';
COMMENT ON COLUMN calling.calling_task_config.updated_time IS '更新时间';

-- ----------------------------
-- 2. 初始化核心业务表
-- ----------------------------

-- 外呼历史表 (防重去重)
CREATE TABLE IF NOT EXISTS calling.call_history (
    mobile_phone VARCHAR(20) PRIMARY KEY,
    staff_name VARCHAR(50),
    sys_name VARCHAR(50),
    order_type VARCHAR(50),
    order_nums INTEGER
);
COMMENT ON TABLE calling.call_history IS '外呼历史记录表';
COMMENT ON COLUMN calling.call_history.mobile_phone IS '手机号码';

-- 外呼日志表 (流水记录)
CREATE TABLE IF NOT EXISTS calling.call_log (
    id SERIAL PRIMARY KEY,
    mobile_phone VARCHAR(20),
    staff_name VARCHAR(50),
    sys_name VARCHAR(50),
    order_type VARCHAR(50),
    order_nums INTEGER,
    status INTEGER,
    error_msg VARCHAR(2000),
    push_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_call_log_mobile_phone ON calling.call_log(mobile_phone);
COMMENT ON TABLE calling.call_log IS '外呼流水日志表';