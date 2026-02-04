-- ----------------------------
-- 初始化菜单数据 (网信安管理)
-- ----------------------------
DO $$
DECLARE
    root_id INT;
    wxsafe_menu_id INT;
BEGIN
    -- 1. 获取基础 ID
    SELECT COALESCE(MAX(id), 0) INTO root_id FROM sys_menu;
    
    -- 2. 插入一级目录: 网信安管理
    INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, affix, parent_id, id, "uuid", status, created_time, updated_time) 
    VALUES (
        '网信安管理', 1, 70, NULL, 'lock', 'ModuleWxSafe', '/wxsafe', 'Layout', '/wxsafe/info', 
        false, true, true, '网信安管理', false, NULL, root_id + 1, gen_random_uuid(), '0', NOW(), NOW()
    );
    
    root_id := root_id + 1;

    -- 3. 插入菜单: 涉诈信息管理
    INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, affix, parent_id, id, "uuid", status, created_time, updated_time) 
    VALUES (
        '涉诈信息管理', 2, 1, 'module_wxsafe:info:list', 'list', 'WxSafeInfo', 'info', 'module_wxsafe/info/index', NULL, 
        false, true, false, '涉诈信息管理', false, root_id, root_id + 1, gen_random_uuid(), '0', NOW(), NOW()
    );
    
    wxsafe_menu_id := root_id + 1;

    -- 4. 插入按钮权限
    
    -- 查询
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('查询', 3, 1, 'module_wxsafe:info:query', wxsafe_menu_id, wxsafe_menu_id + 1, gen_random_uuid(), '0', '查询', false, true, false, false, NOW(), NOW());
    
    -- 新增
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('新增', 3, 2, 'module_wxsafe:info:add', wxsafe_menu_id, wxsafe_menu_id + 2, gen_random_uuid(), '0', '新增', false, true, false, false, NOW(), NOW());
    
    -- 导入
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('导入', 3, 3, 'module_wxsafe:info:import', wxsafe_menu_id, wxsafe_menu_id + 3, gen_random_uuid(), '0', '导入', false, true, false, false, NOW(), NOW());

    RAISE NOTICE '网信安模块初始化成功！';
END $$;
