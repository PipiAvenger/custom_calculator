-- 创建配置数据表
CREATE TABLE IF NOT EXISTS calculator_config (
    id BIGINT PRIMARY KEY,
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL,
    key_type TEXT Not NULL,
    parent_id BIGINT DEFAULT 0
);

-- 创建每月总费用历史数据表
CREATE TABLE IF NOT EXISTS calculator_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_month_use INTEGER NOT NULL,
    this_month_use INTEGER NOT NULL,
    power_rate REAL NOT NULL,
    public_fee REAL NOT NULL,
    total_fee REAL NOT NULL,
    whois TEXT,
    create_date DATE NOT NULL
);

-- 树的根
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (0, '', '', '', 0);

-- 子叶
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (1, '管理费', '111.73', 'public', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (2, '水费', '58.8', 'public', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (3, '垃圾清运费', '0', 'public', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (4, '电费单价', '0.699', 'public', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (5, '总计用电度数', '6', 'public-ex', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (6, '上月用电度数', '0', 'public-ex', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (7, '本月用电度数', '1', 'public-ex', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (8, '公摊电费', '0', 'public', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (9, '维修基金', '12.41', 'public', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (10, '房间1', '林', 'room', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (11, '房间2', '蔺', 'room', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (12, '房间3', '陈', 'room', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (13, '房间4', '曾', 'room', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (14, '房间5', '郭', 'room', 0);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (15, '上月用电度数', '0', 'item', 10);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (16, '本月用电度数', '1', 'item', 10);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (17, '上月用电度数', '0', 'item', 11);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (18, '本月用电度数', '1', 'item', 11);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (29, '上月用电度数', '0', 'item', 12);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (20, '本月用电度数', '1', 'item', 12);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (21, '上月用电度数', '0', 'item', 13);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (22, '本月用电度数', '1', 'item', 13);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (23, '上月用电度数', '0', 'item', 14);
INSERT INTO calculator_config (id, key_name, key_value, key_type, parent_id) VALUES (24, '本月用电度数', '1', 'item', 14);