 -- 1. 创建销售订单测试表
CREATE TABLE IF NOT EXISTS t_sales_order (
    id SERIAL PRIMARY KEY,              -- 订单ID
    province_name VARCHAR(100) NOT NULL, -- 省份名称
    city_name VARCHAR(100) NOT NULL,     -- 城市名称
    amount DECIMAL(12, 2) NOT NULL,      -- 销售金额
    order_date DATE NOT NULL             -- 订单日期
    );
-- 2. 为查询性能添加基础索引
CREATE INDEX idx_sales_province ON t_sales_order(province_name);
CREATE INDEX idx_sales_city ON t_sales_order(city_name);
-- 3. 插入模拟测试数据
INSERT INTO t_sales_order (province_name, city_name, amount, order_date) VALUES
   ('浙江省', '杭州市', 1000.00, '2024-01-01'),
   ('浙江省', '杭州市', 1500.50, '2024-01-05'),
   ('浙江省', '宁波市', 1200.00, '2024-01-02'),
   ('浙江省', '温州市', 900.00, '2024-01-10'),
   ('江苏省', '南京市', 800.00, '2024-01-01'),
   ('江苏省', '苏州市', 1500.00, '2024-01-03'),
   ('江苏省', '无锡市', 1100.00, '2024-01-04'),
   ('江苏省', '南京市', 2200.00, '2024-01-15'),
   ('广东省', '广州市', 3000.00, '2024-01-01'),
   ('广东省', '深圳市', 5000.00, '2024-01-02'),
   ('广东省', '东莞市', 1800.00, '2024-01-03'),
   ('上海市', '上海市', 4500.00, '2024-01-01'),
   ('北京市', '北京市', 4200.00, '2024-01-02');
