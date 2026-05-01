-- ============================================================
-- 物流教学软件 - 数据库设计
-- 版本: v1.0 | 日期: 2026-05-01
-- 数据库: SQLite（开发）/ MySQL（生产）
-- 说明: 本 SQL 兼容 SQLite 语法，MySQL 环境需微调
-- ============================================================

-- ============================================================
-- 1. 用户与权限
-- ============================================================

-- 角色表
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(32) NOT NULL UNIQUE,        -- 角色编码: admin/teacher/student/purchaser/cs/dispatcher/warehouse/driver
    name VARCHAR(64) NOT NULL,                -- 角色名称
    description VARCHAR(256),                 -- 角色描述
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,     -- 用户名/学号
    password_hash VARCHAR(256) NOT NULL,      -- 密码哈希（bcrypt）
    real_name VARCHAR(64) NOT NULL,           -- 真实姓名
    role_id INTEGER NOT NULL,                 -- 角色ID
    group_id INTEGER,                         -- 分组ID（多人协作模式用，可为空）
    email VARCHAR(128),
    phone VARCHAR(20),
    status VARCHAR(16) DEFAULT 'active',      -- active/inactive
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- 分组表（多人协作模式）
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name VARCHAR(64) NOT NULL,          -- 分组名称，如"第1组"
    scene_id INTEGER,                         -- 关联的教学场景
    status VARCHAR(16) DEFAULT 'active',      -- active/completed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. 基础数据
-- ============================================================

-- 供应商表
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) NOT NULL,               -- 供应商名称
    contact VARCHAR(64),                      -- 联系人
    phone VARCHAR(20),                        -- 联系电话
    address VARCHAR(256),                     -- 地址
    rating DECIMAL(2,1) DEFAULT 0.0,          -- 评分（1.0-5.0）
    status VARCHAR(16) DEFAULT 'active',      -- active/inactive
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 客户表
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) NOT NULL,               -- 客户名称
    contact VARCHAR(64),                      -- 联系人
    phone VARCHAR(20),                        -- 联系电话
    address VARCHAR(256),                     -- 地址
    credit_level VARCHAR(16) DEFAULT 'normal',-- credit_level: normal/good/vip
    status VARCHAR(16) DEFAULT 'active',      -- active/inactive
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 车辆表
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_no VARCHAR(20) NOT NULL UNIQUE,     -- 车牌号
    type VARCHAR(32) NOT NULL,                -- 车型: 小型/中型/大型/冷藏
    capacity_weight DECIMAL(8,2),              -- 载重（吨）
    capacity_volume DECIMAL(8,2),              -- 容积（立方米）
    status VARCHAR(16) DEFAULT 'idle',        -- idle/in_transport/maintenance
    driver_id INTEGER,                        -- 当前绑定司机
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

-- 司机表
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) NOT NULL,                -- 司机姓名
    phone VARCHAR(20),                        -- 联系电话
    license_no VARCHAR(32),                   -- 驾照号
    license_type VARCHAR(16),                 -- 驾照类型: A1/A2/B1/B2
    status VARCHAR(16) DEFAULT 'available',   -- available/on_road/off_duty
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 商品分类表
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) NOT NULL,                -- 分类名称
    parent_id INTEGER,                        -- 父分类ID（支持多级）
    sort_order INTEGER DEFAULT 0,             -- 排序
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- 商品表
CREATE TABLE goods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku VARCHAR(64) NOT NULL UNIQUE,          -- SKU编码
    name VARCHAR(128) NOT NULL,               -- 商品名称
    spec VARCHAR(128),                        -- 规格型号
    unit VARCHAR(16) NOT NULL,                -- 计量单位: 个/箱/吨/立方米
    category_id INTEGER,                      -- 分类ID
    min_stock INTEGER DEFAULT 0,              -- 最低库存预警值
    max_stock INTEGER DEFAULT 99999,          -- 最高库存预警值
    purchase_price DECIMAL(10,2),             -- 采购参考价
    selling_price DECIMAL(10,2),              -- 销售参考价
    status VARCHAR(16) DEFAULT 'active',      -- active/inactive
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 仓库表
CREATE TABLE warehouses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) NOT NULL,                -- 仓库名称
    address VARCHAR(256),                     -- 仓库地址
    type VARCHAR(32) DEFAULT 'normal',        -- normal/cold/dangerous
    total_locations INTEGER DEFAULT 0,        -- 总货位数
    used_locations INTEGER DEFAULT 0,         -- 已用货位数
    status VARCHAR(16) DEFAULT 'active',      -- active/inactive
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 库区表
CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_id INTEGER NOT NULL,            -- 所属仓库ID
    zone_code VARCHAR(16) NOT NULL,           -- 库区编码: A/B/C
    zone_name VARCHAR(64) NOT NULL,           -- 库区名称
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
);

-- 货位表
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id INTEGER NOT NULL,                 -- 所属库区ID
    loc_code VARCHAR(32) NOT NULL,            -- 货位编码: A-01-01
    capacity_weight DECIMAL(8,2),             -- 最大承重
    capacity_volume DECIMAL(8,2),             -- 最大容积
    status VARCHAR(16) DEFAULT 'empty',       -- empty/occupied/full
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);

-- ============================================================
-- 3. 采购管理
-- ============================================================

-- 采购申请表
CREATE TABLE purchase_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    req_no VARCHAR(32) NOT NULL UNIQUE,       -- 申请单号: PR-20260501001
    applicant_id INTEGER NOT NULL,            -- 申请人ID
    goods_id INTEGER NOT NULL,                -- 商品ID
    quantity INTEGER NOT NULL,                -- 申请数量
    est_unit_price DECIMAL(10,2),             -- 期望单价
    est_total_price DECIMAL(12,2),            -- 期望总价
    reason VARCHAR(512),                      -- 申请原因
    urgency VARCHAR(16) DEFAULT 'normal',     -- normal/urgent/critical
    status VARCHAR(16) DEFAULT 'pending',     -- pending/approved/rejected/cancelled
    reviewer_id INTEGER,                      -- 审批人ID
    review_comment VARCHAR(512),              -- 审批意见
    reviewed_at DATETIME,                     -- 审批时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES users(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 采购订单表
CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_no VARCHAR(32) NOT NULL UNIQUE,        -- 采购订单号: PO-20260501001
    request_id INTEGER NOT NULL,              -- 关联采购申请ID
    supplier_id INTEGER NOT NULL,             -- 供应商ID
    total_amount DECIMAL(12,2) NOT NULL,      -- 订单总金额
    expected_date DATE,                       -- 期望到货日期
    status VARCHAR(16) DEFAULT 'pending',     -- pending/confirmed/shipped/partial_received/completed/cancelled
    operator_id INTEGER,                      -- 操作人ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES purchase_requests(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);

-- 采购订单明细表
CREATE TABLE purchase_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER NOT NULL,                   -- 采购订单ID
    goods_id INTEGER NOT NULL,                -- 商品ID
    ordered_qty INTEGER NOT NULL,             -- 订购数量
    unit_price DECIMAL(10,2) NOT NULL,        -- 单价
    subtotal DECIMAL(12,2) NOT NULL,          -- 小计
    received_qty INTEGER DEFAULT 0,           -- 已到货数量
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id)
);

-- 采购收货/验收表
CREATE TABLE purchase_receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER NOT NULL,                   -- 关联采购订单ID
    inbound_order_id INTEGER,                 -- 关联入库单ID（验收通过后生成）
    received_qty INTEGER NOT NULL,            -- 本次到货数量
    quality_status VARCHAR(16) DEFAULT 'qualified', -- qualified/unqualified/partial
    quality_note VARCHAR(512),                -- 质检说明
    receiver_id INTEGER NOT NULL,             -- 验收人ID
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (inbound_order_id) REFERENCES inbound_orders(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

-- ============================================================
-- 4. 运输管理
-- ============================================================

-- 运输订单表
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(32) NOT NULL UNIQUE,     -- 订单号: T-20260501001
    customer_id INTEGER NOT NULL,             -- 客户ID
    origin VARCHAR(256) NOT NULL,             -- 发货地
    destination VARCHAR(256) NOT NULL,        -- 目的地
    goods_name VARCHAR(128),                  -- 货物名称
    goods_id INTEGER,                         -- 关联商品ID
    weight DECIMAL(8,2),                      -- 重量（千克）
    volume DECIMAL(8,2),                      -- 体积（立方米）
    quantity INTEGER,                         -- 件数
    status VARCHAR(16) DEFAULT 'pending',     -- pending/approved/dispatched/in_transit/arrived/signed/completed/cancelled
    vehicle_id INTEGER,                       -- 分配车辆ID
    driver_id INTEGER,                        -- 分配司机ID
    freight_amount DECIMAL(10,2),             -- 运费金额
    plan_departure DATETIME,                  -- 计划发车时间
    plan_arrival DATETIME,                    -- 计划到达时间
    actual_departure DATETIME,                -- 实际发车时间
    actual_arrival DATETIME,                  -- 实际到达时间
    signee_name VARCHAR(64),                  -- 签收人
    signee_phone VARCHAR(20),                 -- 签收人电话
    remark VARCHAR(512),                      -- 备注
    group_id INTEGER,                         -- 分组ID（多人协作模式）
    operator_id INTEGER,                      -- 操作人ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);

-- 运输跟踪记录表
CREATE TABLE transport_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,                -- 运输订单ID
    status VARCHAR(32) NOT NULL,              -- 状态: departed/in_transit/rest/arrived/signed
    location VARCHAR(256),                    -- 当前位置
    description VARCHAR(512),                 -- 描述
    recorded_by INTEGER,                      -- 记录人ID（通常是司机）
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (recorded_by) REFERENCES users(id)
);

-- ============================================================
-- 5. 仓储管理
-- ============================================================

-- 入库单表
CREATE TABLE inbound_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(32) NOT NULL UNIQUE,     -- 入库单号: IN-20260501001
    warehouse_id INTEGER NOT NULL,            -- 目标仓库ID
    source_type VARCHAR(32) NOT NULL,         -- 来源类型: purchase/return/transfer
    source_id INTEGER,                        -- 来源单据ID（采购订单/退货单/调拨单）
    status VARCHAR(16) DEFAULT 'pending',     -- pending/inspecting/shelving/completed/cancelled
    total_items INTEGER DEFAULT 0,            -- 总品类数
    operator_id INTEGER,                      -- 操作人ID
    inspected_at DATETIME,                    -- 验收时间
    completed_at DATETIME,                    -- 完成时间
    remark VARCHAR(512),
    group_id INTEGER,                         -- 分组ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (operator_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

-- 入库明细表
CREATE TABLE inbound_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inbound_id INTEGER NOT NULL,              -- 入库单ID
    goods_id INTEGER NOT NULL,                -- 商品ID
    planned_qty INTEGER NOT NULL,             -- 计划入库数量
    actual_qty INTEGER,                       -- 实际入库数量
    location_id INTEGER,                      -- 上架货位ID
    batch_no VARCHAR(64),                     -- 批次号
    production_date DATE,                     -- 生产日期
    expiry_date DATE,                         -- 有效期
    status VARCHAR(16) DEFAULT 'pending',     -- pending/shelved/completed
    FOREIGN KEY (inbound_id) REFERENCES inbound_orders(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- 出库单表
CREATE TABLE outbound_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(32) NOT NULL UNIQUE,     -- 出库单号: OUT-20260501001
    warehouse_id INTEGER NOT NULL,            -- 源仓库ID
    dest_type VARCHAR(32) NOT NULL,           -- 目的类型: sales/transfer/loss
    dest_id INTEGER,                          -- 目标单据ID（销售订单/调拨单）
    status VARCHAR(16) DEFAULT 'pending',     -- pending/picking/packing/shipped/completed/cancelled
    total_items INTEGER DEFAULT 0,            -- 总品类数
    operator_id INTEGER,                      -- 操作人ID
    completed_at DATETIME,                    -- 完成时间
    remark VARCHAR(512),
    group_id INTEGER,                         -- 分组ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (operator_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

-- 出库明细表
CREATE TABLE outbound_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outbound_id INTEGER NOT NULL,             -- 出库单ID
    goods_id INTEGER NOT NULL,                -- 商品ID
    planned_qty INTEGER NOT NULL,             -- 计划出库数量
    actual_qty INTEGER,                       -- 实际出库数量
    location_id INTEGER,                      -- 拣货货位ID
    batch_no VARCHAR(64),                     -- 批次号（先进先出）
    status VARCHAR(16) DEFAULT 'pending',     -- pending/picked/shipped
    FOREIGN KEY (outbound_id) REFERENCES outbound_orders(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- ============================================================
-- 6. 库存管理
-- ============================================================

-- 库存表（当前库存快照）
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_id INTEGER NOT NULL,            -- 仓库ID
    location_id INTEGER NOT NULL,             -- 货位ID
    goods_id INTEGER NOT NULL,                -- 商品ID
    batch_no VARCHAR(64),                     -- 批次号
    quantity INTEGER NOT NULL DEFAULT 0,      -- 当前数量
    available_qty INTEGER NOT NULL DEFAULT 0, -- 可用数量（减去锁定）
    production_date DATE,                     -- 生产日期
    expiry_date DATE,                         -- 有效期
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id)
);

-- 库存变动流水表
CREATE TABLE inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_id INTEGER NOT NULL,            -- 仓库ID
    location_id INTEGER,                      -- 货位ID
    goods_id INTEGER NOT NULL,                -- 商品ID
    batch_no VARCHAR(64),                     -- 批次号
    change_type VARCHAR(32) NOT NULL,         -- 变动类型: inbound/outbound/transfer/adjust/loss
    change_qty INTEGER NOT NULL,              -- 变动数量（正=增加，负=减少）
    balance_qty INTEGER NOT NULL,             -- 变动后结存数量
    ref_type VARCHAR(32),                     -- 关联单据类型: inbound_order/outbound_order/adjust_order
    ref_id INTEGER,                           -- 关联单据ID
    operator_id INTEGER,                      -- 操作人ID
    remark VARCHAR(256),                      -- 备注
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);

-- 盘点任务表
CREATE TABLE stocktake_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_no VARCHAR(32) NOT NULL UNIQUE,      -- 盘点单号: ST-20260501001
    warehouse_id INTEGER NOT NULL,            -- 盘点仓库
    status VARCHAR(16) DEFAULT 'pending',     -- pending/counting/reconciling/completed
    operator_id INTEGER,                      -- 盘点人
    remark VARCHAR(512),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (operator_id) REFERENCES users(id)
);

-- 盘点明细表
CREATE TABLE stocktake_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,                 -- 盘点任务ID
    location_id INTEGER NOT NULL,             -- 货位ID
    goods_id INTEGER NOT NULL,                -- 商品ID
    system_qty INTEGER NOT NULL,              -- 系统数量
    actual_qty INTEGER,                       -- 实盘数量
    diff_qty INTEGER,                         -- 差异数量（实盘-系统）
    reason VARCHAR(256),                      -- 差异原因
    status VARCHAR(16) DEFAULT 'pending',     -- pending/counted/confirmed
    FOREIGN KEY (task_id) REFERENCES stocktake_tasks(id),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (goods_id) REFERENCES goods(id)
);

-- ============================================================
-- 7. 教学辅助
-- ============================================================

-- 教学场景表
CREATE TABLE teaching_scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) NOT NULL,                -- 场景名称
    description VARCHAR(512),                 -- 场景描述
    difficulty VARCHAR(16) DEFAULT 'normal',  -- easy/normal/hard
    initial_data JSON,                        -- 初始数据配置（库存、车辆等）
    events_config JSON,                       -- 突发事件配置
    scoring_rules JSON,                       -- 评分规则配置
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 突发事件表
CREATE TABLE injected_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,                         -- 目标分组（NULL=全局）
    scene_id INTEGER,                         -- 关联场景
    event_type VARCHAR(32) NOT NULL,          -- 事件类型: vehicle_breakdown/supplier_delay/quality_issue/surge_orders
    event_data JSON,                          -- 事件详细数据
    trigger_time DATETIME,                    -- 触发时间
    status VARCHAR(16) DEFAULT 'pending',     -- pending/triggered/resolved
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (scene_id) REFERENCES teaching_scenes(id)
);

-- 操作日志表
CREATE TABLE operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                 -- 操作人ID
    group_id INTEGER,                         -- 分组ID
    action VARCHAR(64) NOT NULL,              -- 操作类型: create/update/delete/approve/reject
    module VARCHAR(32) NOT NULL,              -- 模块: purchase/transport/warehouse/inventory
    ref_type VARCHAR(32),                     -- 关联对象类型
    ref_id INTEGER,                           -- 关联对象ID
    old_value TEXT,                           -- 变更前值（JSON）
    new_value TEXT,                           -- 变更后值（JSON）
    ip_address VARCHAR(45),                   -- IP地址
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

-- 评分记录表
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                 -- 学生ID
    group_id INTEGER,                         -- 分组ID（单人模式为空）
    scene_id INTEGER,                         -- 关联场景
    total_score DECIMAL(5,2) DEFAULT 0,       -- 总分
    process_score DECIMAL(5,2) DEFAULT 0,     -- 流程分
    accuracy_score DECIMAL(5,2) DEFAULT 0,    -- 准确性分
    efficiency_score DECIMAL(5,2) DEFAULT 0,  -- 效率分
    detail TEXT,                              -- 评分详情（JSON）
    scored_at DATETIME,                       -- 评分时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (scene_id) REFERENCES teaching_scenes(id)
);

-- ============================================================
-- 8. 索引（提升常用查询性能）
-- ============================================================

CREATE INDEX idx_purchase_requests_status ON purchase_requests(status);
CREATE INDEX idx_purchase_requests_applicant ON purchase_requests(applicant_id);
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_vehicle ON orders(vehicle_id);
CREATE INDEX idx_orders_driver ON orders(driver_id);
CREATE INDEX idx_orders_group ON orders(group_id);
CREATE INDEX idx_transport_records_order ON transport_records(order_id);
CREATE INDEX idx_inbound_orders_status ON inbound_orders(status);
CREATE INDEX idx_inbound_orders_warehouse ON inbound_orders(warehouse_id);
CREATE INDEX idx_outbound_orders_status ON outbound_orders(status);
CREATE INDEX idx_outbound_orders_warehouse ON outbound_orders(warehouse_id);
CREATE INDEX idx_inventory_goods ON inventory(goods_id);
CREATE INDEX idx_inventory_warehouse ON inventory(warehouse_id);
CREATE INDEX idx_inventory_location ON inventory(location_id);
CREATE INDEX idx_inventory_transactions_goods ON inventory_transactions(goods_id);
CREATE INDEX idx_inventory_transactions_time ON inventory_transactions(created_at);
CREATE INDEX idx_operation_logs_user ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_time ON operation_logs(created_at);
CREATE INDEX idx_scores_user ON scores(user_id);

-- ============================================================
-- 9. 初始数据
-- ============================================================

-- 初始角色
INSERT INTO roles (code, name, description) VALUES
('admin', '系统管理员', '管理系统的所有功能和数据'),
('teacher', '教师', '创建教学场景、监控学生进度、评分'),
('student', '学生', '参与学习任务的学生'),
('purchaser', '采购专员', '负责采购申请和供应商管理'),
('customer_service', '客服', '负责接单和客户沟通'),
('dispatcher', '调度员', '负责车辆调度和路线规划'),
('warehouse_keeper', '仓库管理员', '负责出入库和库存管理'),
('driver', '司机', '负责运输执行');

-- ============================================================
-- END
-- ============================================================
