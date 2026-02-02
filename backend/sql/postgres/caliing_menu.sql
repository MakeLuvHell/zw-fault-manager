-- ----------------------------
-- 初始化菜单数据 (已修复 affix 和 always_show 非空问题)
-- ----------------------------
DO $$
DECLARE
    root_id INT;
    task_menu_id INT;
BEGIN
    -- 1. 获取基础 ID
    SELECT COALESCE(MAX(id), 0) INTO root_id FROM sys_menu;
    
    -- 2. 插入一级目录: 外呼管理
    INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, affix, parent_id, id, "uuid", status, created_time, updated_time) 
    VALUES (
        '外呼管理', 1, 60, NULL, 'phone', 'ModuleCalling', '/module_calling', 'Layout', '/module_calling/task', 
        false, true, true, '外呼管理', false, NULL, root_id + 1, gen_random_uuid(), '0', NOW(), NOW()
    );
    
    root_id := root_id + 1;

    -- 3. 插入菜单: 任务管理
    INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, affix, parent_id, id, "uuid", status, created_time, updated_time) 
    VALUES (
        '任务管理', 2, 1, 'module_calling:task:list', 'list', 'CallingTask', 'task', 'module_calling/task/index', NULL, 
        false, true, false, '任务管理', false, root_id, root_id + 1, gen_random_uuid(), '0', NOW(), NOW()
    );
    
    task_menu_id := root_id + 1;

    -- 4. 插入按钮权限
    -- 重点修复：所有按钮都补充了 always_show = false
    
    -- 查询
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('查询', 3, 1, 'module_calling:task:query', task_menu_id, task_menu_id + 1, gen_random_uuid(), '0', '查询', false, true, false, false, NOW(), NOW());
    
    -- 新增
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('新增', 3, 2, 'module_calling:task:create', task_menu_id, task_menu_id + 2, gen_random_uuid(), '0', '新增', false, true, false, false, NOW(), NOW());
    
    -- 修改
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('修改', 3, 3, 'module_calling:task:update', task_menu_id, task_menu_id + 3, gen_random_uuid(), '0', '修改', false, true, false, false, NOW(), NOW());
    
    -- 删除
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('删除', 3, 4, 'module_calling:task:delete', task_menu_id, task_menu_id + 4, gen_random_uuid(), '0', '删除', false, true, false, false, NOW(), NOW());
    
    -- 执行
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('执行', 3, 5, 'module_calling:task:execute', task_menu_id, task_menu_id + 5, gen_random_uuid(), '0', '执行', false, true, false, false, NOW(), NOW());

    RAISE NOTICE '外呼模块初始化成功！';
END $$;