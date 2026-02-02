-- 外呼任务配置表
-- 用于管理外呼任务的调度配置和字段映射

-- 创建外呼任务配置表
CREATE TABLE IF NOT EXISTS calling_task_config (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '任务名称',
    cron_expr VARCHAR(100) NOT NULL COMMENT 'Cron 表达式',
    source_schema VARCHAR(100) NOT NULL COMMENT '源数据 Schema',
    source_table VARCHAR(100) NOT NULL COMMENT '源数据表名',
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否启用',
    remark VARCHAR(500) COMMENT '备注',
    field_mapping TEXT NOT NULL COMMENT '字段映射 JSON',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '更新时间'
);

-- 添加表注释
COMMENT ON TABLE calling_task_config IS '外呼任务配置表';
COMMENT ON COLUMN calling_task_config.id IS '任务ID';
COMMENT ON COLUMN calling_task_config.name IS '任务名称';
COMMENT ON COLUMN calling_task_config.cron_expr IS 'Cron 表达式';
COMMENT ON COLUMN calling_task_config.source_schema IS '源数据 Schema';
COMMENT ON COLUMN calling_task_config.source_table IS '源数据表名';
COMMENT ON COLUMN calling_task_config.is_enabled IS '是否启用';
COMMENT ON COLUMN calling_task_config.remark IS '备注';
COMMENT ON COLUMN calling_task_config.field_mapping IS '字段映射 JSON';
COMMENT ON COLUMN calling_task_config.created_time IS '创建时间';
COMMENT ON COLUMN calling_task_config.updated_time IS '更新时间';

-- 插入外呼模块菜单
-- 假设父菜单 ID 需要根据实际情况调整

-- 获取最大菜单ID后插入
DO $$
DECLARE
    max_id INT;
    parent_id INT;
BEGIN
    -- 获取当前最大菜单ID
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM sys_menu;
    
    -- 创建外呼管理父菜单
    INSERT INTO sys_menu (id, name, code, icon, path, sort, parent_id, component, redirect, status, hidden, "keepAlive", is_link)
    VALUES (max_id + 1, '外呼管理', 'module_calling', 'phone', '/module_calling', 60, 0, 'Layout', '/module_calling/task', '0', FALSE, FALSE, FALSE);
    parent_id := max_id + 1;
    
    -- 创建任务管理子菜单
    INSERT INTO sys_menu (id, name, code, icon, path, sort, parent_id, component, redirect, status, hidden, "keepAlive", is_link)
    VALUES (max_id + 2, '任务管理', 'module_calling:task', 'list', 'task', 1, parent_id, 'module_calling/task/index', NULL, '0', FALSE, FALSE, FALSE);
    
    -- 创建权限按钮
    INSERT INTO sys_menu (id, name, code, icon, path, sort, parent_id, component, redirect, status, hidden, "keepAlive", is_link)
    VALUES 
        (max_id + 3, '查询', 'module_calling:task:query', NULL, NULL, 1, max_id + 2, NULL, NULL, '0', FALSE, FALSE, FALSE),
        (max_id + 4, '详情', 'module_calling:task:detail', NULL, NULL, 2, max_id + 2, NULL, NULL, '0', FALSE, FALSE, FALSE),
        (max_id + 5, '新增', 'module_calling:task:create', NULL, NULL, 3, max_id + 2, NULL, NULL, '0', FALSE, FALSE, FALSE),
        (max_id + 6, '编辑', 'module_calling:task:update', NULL, NULL, 4, max_id + 2, NULL, NULL, '0', FALSE, FALSE, FALSE),
        (max_id + 7, '删除', 'module_calling:task:delete', NULL, NULL, 5, max_id + 2, NULL, NULL, '0', FALSE, FALSE, FALSE),
        (max_id + 8, '执行', 'module_calling:task:execute', NULL, NULL, 6, max_id + 2, NULL, NULL, '0', FALSE, FALSE, FALSE);
    
    RAISE NOTICE '菜单插入完成，父菜单ID: %, 子菜单ID: %', parent_id, max_id + 2;
END $$;

-- 为管理员角色分配权限（假设管理员角色ID为1）
-- 需要根据实际情况调整
-- INSERT INTO sys_role_menu (role_id, menu_id)
-- SELECT 1, id FROM sys_menu WHERE code LIKE 'module_calling%';
