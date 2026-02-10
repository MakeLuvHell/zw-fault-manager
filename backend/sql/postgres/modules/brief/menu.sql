-- ----------------------------
-- 初始化菜单数据 (智能分析/智能简报)
-- ----------------------------
DO $$
DECLARE
    root_id INT;
    brief_group_id INT;
    brief_menu_id INT;
BEGIN
    -- 1. 获取当前最大 ID 作为起始点
    SELECT COALESCE(MAX(id), 0) INTO root_id FROM sys_menu;
    
    -- 2. 插入一级目录: 智能分析
    INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, affix, parent_id, id, "uuid", status, created_time, updated_time) 
    VALUES (
        '智能分析', 1, 80, NULL, 'el-icon-DataAnalysis', 'Brief', '/brief', 'Layout', '/brief/report', 
        false, true, true, '智能分析', false, NULL, root_id + 1, gen_random_uuid(), '0', NOW(), NOW()
    );
    
    brief_group_id := root_id + 1;

    -- 3. 插入二级菜单: 智能简报 (列表页)
    INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, affix, parent_id, id, "uuid", status, created_time, updated_time) 
    VALUES (
        '智能简报', 2, 1, 'module_brief:report:query', 'el-icon-Document', 'BriefReport', '/brief/report', 'module_brief/report/index', NULL, 
        false, true, false, '智能简报', false, brief_group_id, root_id + 2, gen_random_uuid(), '0', NOW(), NOW()
    );
    
    brief_menu_id := root_id + 2;

    -- 4. 插入按钮权限 (隶属于 智能简报)
    
    -- 查询简报
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('查询简报', 3, 1, 'module_brief:report:query', brief_menu_id, root_id + 3, gen_random_uuid(), '0', '查询简报', false, true, false, false, NOW(), NOW());
    
    -- 上传分析
    INSERT INTO sys_menu ("name", "type", "order", "permission", parent_id, id, "uuid", status, title, hidden, keep_alive, affix, always_show, created_time, updated_time) 
    VALUES ('上传分析', 3, 2, 'module_brief:report:add', brief_menu_id, root_id + 4, gen_random_uuid(), '0', '上传分析', false, true, false, false, NOW(), NOW());

    -- 5. 插入二级菜单: 简报详情 (隐藏路由)
    INSERT INTO sys_menu ("name", "type", "order", "permission", icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, affix, parent_id, id, "uuid", status, created_time, updated_time) 
    VALUES (
        '简报详情', 2, 2, 'module_brief:report:query', 'el-icon-Document', 'BriefDetail', '/brief/report/:id', 'module_brief/report/detail', NULL, 
        true, true, false, '简报详情', false, brief_group_id, root_id + 5, gen_random_uuid(), '0', NOW(), NOW()
    );

    RAISE NOTICE '智能分析模块菜单初始化成功！起始ID: %', brief_group_id;
END $$;
