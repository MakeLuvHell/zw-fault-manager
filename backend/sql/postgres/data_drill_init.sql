-- ----------------------------
-- 1. 初始化表结构
-- ----------------------------

-- 下钻报表主表
CREATE TABLE IF NOT EXISTS data_drill_info (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL UNIQUE,
    report_name VARCHAR(255) NOT NULL,
    status VARCHAR(10) DEFAULT '0' NOT NULL,
    description TEXT,
    created_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_id INTEGER,
    updated_id INTEGER
);
COMMENT ON TABLE data_drill_info IS '下钻报表定义';
COMMENT ON COLUMN data_drill_info.report_name IS '报表名称';
COMMENT ON COLUMN data_drill_info.status IS '是否启用(0:启用 1:禁用)';

-- 下钻报表节点表
CREATE TABLE IF NOT EXISTS data_drill_node (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL UNIQUE,
    info_id INTEGER NOT NULL REFERENCES data_drill_info(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES data_drill_node(id),
    node_name VARCHAR(255) NOT NULL,
    sql_text TEXT,
    link_field VARCHAR(255),
    param_name VARCHAR(255),
    status VARCHAR(10) DEFAULT '0' NOT NULL,
    description TEXT,
    created_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE data_drill_node IS '下钻报表节点';
COMMENT ON COLUMN data_drill_node.info_id IS '主表ID';
COMMENT ON COLUMN data_drill_node.parent_id IS '父节点ID';
COMMENT ON COLUMN data_drill_node.sql_text IS '查询SQL';
COMMENT ON COLUMN data_drill_node.link_field IS '父级关联字段';
COMMENT ON COLUMN data_drill_node.param_name IS '参数名';

-- ----------------------------
-- 2. 初始化菜单数据
-- ----------------------------

-- 1. 插入一级目录: 数据下钻 (ID: 138)
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('数据下钻', 1, 100, NULL, 'data-analysis', 'ModuleDataDrill', '/module_datadrill', 'Layout', NULL, false, true, true, '数据下钻', NULL, false, NULL, 138, '9d5d24f2-19f6-4d9e-9f9c-ccba3c157560', '0', '数据下钻模块根目录', NOW(), NOW());

-- 2. 插入菜单: 报表配置管理 (ID: 139)
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('报表配置管理', 2, 1, 'module_datadrill:data_drill_info:list', 'setting', 'PxmDataDrillInfo', 'data_drill_info', 'module_datadrill/data_drill_info/index', NULL, false, true, false, '报表配置管理', NULL, false, 138, 139, '541c5e5d-a7bf-45c6-bf82-944504680def', '0', '下钻报表配置', NOW(), NOW());

-- 按钮权限: 配置查询
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('配置查询', 3, 1, 'module_datadrill:data_drill_info:query', NULL, NULL, NULL, NULL, NULL, false, true, false, '配置查询', NULL, false, 139, 140, '4f81598d-e747-49bb-a89a-00511861c553', '0', NULL, NOW(), NOW());

-- 按钮权限: 配置新增
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('配置新增', 3, 2, 'module_datadrill:data_drill_info:create', NULL, NULL, NULL, NULL, NULL, false, true, false, '配置新增', NULL, false, 139, 141, 'ce582296-f158-41b5-a814-ea90a0058868', '0', NULL, NOW(), NOW());

-- 按钮权限: 配置修改
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('配置修改', 3, 3, 'module_datadrill:data_drill_info:update', NULL, NULL, NULL, NULL, NULL, false, true, false, '配置修改', NULL, false, 139, 142, 'a7634291-2377-4125-8846-4fb9ddc53d8b', '0', NULL, NOW(), NOW());

-- 按钮权限: 配置删除
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('配置删除', 3, 4, 'module_datadrill:data_drill_info:delete', NULL, NULL, NULL, NULL, NULL, false, true, false, '配置删除', NULL, false, 139, 143, '8380e157-dd89-4045-b522-15f6cbde1b9e', '0', NULL, NOW(), NOW());

-- 按钮权限: SQL校验
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('SQL校验', 3, 5, 'module_datadrill:data_drill_info:validate', NULL, NULL, NULL, NULL, NULL, false, true, false, 'SQL校验', NULL, false, 139, 144, 'bfd81d62-10fa-4ba1-9c2b-04e7ad0692f0', '0', NULL, NOW(), NOW());

-- 3. 插入菜单: 报表数据展示 (ID: 140)
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('报表数据展示', 2, 2, 'module_datadrill:data_drill_display:list', 'chart', 'PxmDataDrillDisplay', 'data_drill_display', 'module_datadrill/data_drill_display/index', NULL, false, true, false, '报表数据展示', NULL, false, 138, 145, 'da48ef8a-c4cf-4c88-8bb4-4ea945b31a2b', '0', '下钻报表展示', NOW(), NOW());

-- 按钮权限: 展示查询
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('展示查询', 3, 1, 'module_datadrill:data_drill_display:query', NULL, NULL, NULL, NULL, NULL, false, true, false, '展示查询', NULL, false, 140, 146, 'f3c35cf8-60cf-4585-95a6-74c8e2fac75b', '0', NULL, NOW(), NOW());

-- 按钮权限: 下钻执行
INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, id, "uuid", status, description, created_time, updated_time) 
VALUES('下钻执行', 3, 2, 'module_datadrill:data_drill_display:execute', NULL, NULL, NULL, NULL, NULL, false, true, false, '下钻执行', NULL, false, 140, 147, '1023093c-8815-4525-a06c-f2a7f9d2f327', '0', NULL, NOW(), NOW());
