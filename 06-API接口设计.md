# 物流教学软件 - API 接口设计

> 版本：v1.0 | 日期：2026-05-01
> 基础URL：`/api`
> 认证方式：Session（Flask-Login）
> 响应格式：`{ "code": 200, "message": "success", "data": { ... } }`

---

## 通用约定

### 响应格式

```json
{
  "code": 200,        // 200=成功, 400=参数错误, 401=未登录, 403=无权限, 404=不存在, 500=服务器错误
  "message": "success",
  "data": {}
}
```

### 分页参数（列表接口通用）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| per_page | int | 20 | 每页条数 |
| sort_by | string | created_at | 排序字段 |
| sort_order | string | desc | 排序方向：asc/desc |

### 分页响应格式

```json
{
  "code": 200,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
}
```

---

## 1. 认证接口

### POST /api/auth/login
用户登录

**请求体：**
```json
{
  "username": "2024001",
  "password": "123456",
  "role": "student"        // student / teacher
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "2024001",
    "real_name": "张三",
    "role": "student",
    "group_id": null
  }
}
```

### POST /api/auth/logout
退出登录

### GET /api/auth/me
获取当前用户信息

---

## 2. 基础数据接口

### 2.1 供应商

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/suppliers | 供应商列表 | 登录用户 |
| POST | /api/suppliers | 新增供应商 | 采购专员/教师/管理员 |
| GET | /api/suppliers/:id | 供应商详情 | 登录用户 |
| PUT | /api/suppliers/:id | 编辑供应商 | 采购专员/教师/管理员 |
| DELETE | /api/suppliers/:id | 删除供应商 | 教师/管理员 |

**POST /api/suppliers 请求体：**
```json
{
  "name": "华南包装材料有限公司",
  "contact": "李经理",
  "phone": "13800138001",
  "address": "广东省广州市白云区"
}
```

### 2.2 客户

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/customers | 客户列表 | 登录用户 |
| POST | /api/customers | 新增客户 | 客服/教师/管理员 |
| GET | /api/customers/:id | 客户详情 | 登录用户 |
| PUT | /api/customers/:id | 编辑客户 | 客服/教师/管理员 |
| DELETE | /api/customers/:id | 删除客户 | 教师/管理员 |

### 2.3 车辆

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/vehicles | 车辆列表（支持按状态筛选） | 登录用户 |
| POST | /api/vehicles | 新增车辆 | 调度员/教师/管理员 |
| GET | /api/vehicles/:id | 车辆详情 | 登录用户 |
| PUT | /api/vehicles/:id | 编辑车辆 | 调度员/教师/管理员 |

### 2.4 司机

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/drivers | 司机列表（支持按状态筛选） | 登录用户 |
| POST | /api/drivers | 新增司机 | 调度员/教师/管理员 |
| GET | /api/drivers/:id | 司机详情 | 登录用户 |
| PUT | /api/drivers/:id | 编辑司机 | 调度员/教师/管理员 |

### 2.5 商品

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/goods | 商品列表 | 登录用户 |
| POST | /api/goods | 新增商品 | 教师/管理员 |
| GET | /api/goods/:id | 商品详情 | 登录用户 |
| PUT | /api/goods/:id | 编辑商品 | 教师/管理员 |
| DELETE | /api/goods/:id | 删除商品 | 教师/管理员 |

### 2.6 仓库 / 库区 / 货位

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/warehouses | 仓库列表 | 登录用户 |
| POST | /api/warehouses | 新增仓库 | 教师/管理员 |
| PUT | /api/warehouses/:id | 编辑仓库 | 教师/管理员 |
| GET | /api/warehouses/:id/zones | 某仓库下的库区列表 | 登录用户 |
| POST | /api/zones | 新增库区 | 仓库管理员/教师/管理员 |
| PUT | /api/zones/:id | 编辑库区 | 仓库管理员/教师/管理员 |
| GET | /api/zones/:id/locations | 某库区下的货位列表 | 登录用户 |
| POST | /api/locations | 新增货位 | 仓库管理员/教师/管理员 |
| PUT | /api/locations/:id | 编辑货位（如修改状态） | 仓库管理员/教师/管理员 |

---

## 3. 采购管理接口

### 3.1 采购申请

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/purchase-requests | 申请列表（支持状态筛选） | 登录用户 |
| POST | /api/purchase-requests | 创建采购申请 | 采购专员 |
| GET | /api/purchase-requests/:id | 申请详情 | 登录用户 |
| PUT | /api/purchase-requests/:id/approve | 审批通过 | 教师/管理员 |
| PUT | /api/purchase-requests/:id/reject | 审批驳回 | 教师/管理员 |

**POST /api/purchase-requests 请求体：**
```json
{
  "goods_id": 1,
  "quantity": 500,
  "est_unit_price": 30.00,
  "reason": "库存不足，最低库存线为200箱，当前仅剩50箱",
  "urgency": "normal"              // normal / urgent / critical
}
```

### 3.2 采购订单

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/purchase-orders | 采购订单列表 | 登录用户 |
| POST | /api/purchase-orders | 创建采购订单 | 采购专员 |
| GET | /api/purchase-orders/:id | 订单详情（含明细） | 登录用户 |
| PUT | /api/purchase-orders/:id/confirm | 确认订单 | 采购专员 |
| PUT | /api/purchase-orders/:id/status | 更新状态 | 采购专员/仓库管理员 |

**POST /api/purchase-orders 请求体：**
```json
{
  "request_id": 1,
  "supplier_id": 2,
  "items": [
    { "goods_id": 1, "quantity": 500, "unit_price": 28.00 }
  ],
  "expected_date": "2026-05-15"
}
```

### 3.3 到货验收

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/purchase-receipts | 创建验收记录 | 仓库管理员 |
| GET | /api/purchase-receipts | 验收记录列表 | 登录用户 |

**POST /api/purchase-receipts 请求体：**
```json
{
  "po_id": 1,
  "items": [
    {
      "goods_id": 1,
      "ordered_qty": 500,
      "received_qty": 498,
      "quality_status": "qualified",    // qualified / unqualified / partial
      "quality_note": "2箱外包装破损，做退货处理"
    }
  ]
}
```

**说明：** 验收通过的商品自动生成入库单（source_type=purchase），验收数量即为入库数量。

---

## 4. 运输管理接口

### 4.1 运输订单

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/orders | 运输订单列表（支持多条件筛选） | 登录用户 |
| POST | /api/orders | 创建运输订单 | 客服 |
| GET | /api/orders/:id | 订单详情 | 登录用户 |
| PUT | /api/orders/:id/approve | 审核通过 | 调度员 |
| PUT | /api/orders/:id/reject | 审核驳回 | 调度员 |
| PUT | /api/orders/:id/dispatch | 车辆调度 | 调度员 |
| PUT | /api/orders/:id/status | 更新订单状态 | 司机/客服 |

**POST /api/orders 请求体：**
```json
{
  "customer_id": 1,
  "origin": "广州市白云区太和镇",
  "destination": "深圳市南山区科技园",
  "goods_id": 3,
  "goods_name": "电子元件",
  "weight": 2500,
  "volume": 12.5,
  "quantity": 50,
  "remark": "易碎品，轻拿轻放"
}
```

**PUT /api/orders/:id/dispatch 请求体：**
```json
{
  "vehicle_id": 3,
  "driver_id": 5,
  "plan_departure": "2026-05-02 08:00",
  "plan_arrival": "2026-05-02 14:00"
}
```

### 4.2 运输跟踪

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/transport-records | 添加跟踪记录 | 司机 |
| GET | /api/transport-records | 跟踪记录列表（按order_id筛选） | 登录用户 |

**POST /api/transport-records 请求体：**
```json
{
  "order_id": 1,
  "status": "in_transit",
  "location": "广深高速K50路段",
  "description": "正常行驶中"
}
```

**可用状态：** `departed` / `in_transit` / `rest` / `arrived` / `unloading` / `signed`

### 4.3 运费计算

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/orders/:id/freight | 查看运费明细 | 登录用户 |
| PUT | /api/orders/:id/settle | 确认运费结算 | 客服/教师 |

---

## 5. 仓储管理接口

### 5.1 入库管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/inbound-orders | 入库单列表 | 登录用户 |
| POST | /api/inbound-orders | 创建入库单 | 仓库管理员 |
| GET | /api/inbound-orders/:id | 入库单详情（含明细） | 登录用户 |
| PUT | /api/inbound-orders/:id/inspect | 验收入库 | 仓库管理员 |
| PUT | /api/inbound-orders/:id/shelve | 确认上架（增加库存） | 仓库管理员 |
| PUT | /api/inbound-orders/:id/cancel | 取消入库单 | 仓库管理员 |

**PUT /api/inbound-orders/:id/shelve 请求体：**
```json
{
  "items": [
    {
      "inbound_item_id": 1,
      "actual_qty": 498,
      "location_id": 15,
      "batch_no": "B20260501001",
      "production_date": "2026-04-20",
      "expiry_date": null
    }
  ]
}
```

### 5.2 出库管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/outbound-orders | 出库单列表 | 登录用户 |
| POST | /api/outbound-orders | 创建出库单（自动分配库存） | 仓库管理员 |
| GET | /api/outbound-orders/:id | 出库单详情 | 登录用户 |
| PUT | /api/outbound-orders/:id/pick | 确认拣货 | 仓库管理员 |
| PUT | /api/outbound-orders/:id/ship | 确认发货（扣减库存） | 仓库管理员 |

### 5.3 库内作业

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/inventory/transfer | 移库操作 | 仓库管理员 |

**POST /api/inventory/transfer 请求体：**
```json
{
  "items": [
    {
      "inventory_id": 1,
      "from_location_id": 15,
      "to_location_id": 22,
      "quantity": 100
    }
  ]
}
```

---

## 6. 库存管理接口

### 6.1 库存查询

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/inventory | 库存列表（多条件查询） | 登录用户 |
| GET | /api/inventory/alerts | 库存预警列表 | 登录用户 |
| GET | /api/inventory/transactions | 库存变动流水 | 登录用户 |

**GET /api/inventory 查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| warehouse_id | int | 按仓库筛选 |
| goods_id | int | 按商品筛选 |
| sku | string | 按SKU搜索 |
| name | string | 按商品名搜索 |
| low_stock | bool | true=仅显示库存不足的商品 |
| high_stock | bool | true=仅显示库存偏高的商品 |

### 6.2 盘点管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/stocktake-tasks | 盘点任务列表 | 登录用户 |
| POST | /api/stocktake-tasks | 创建盘点任务 | 仓库管理员 |
| GET | /api/stocktake-tasks/:id | 盘点详情（含差异） | 登录用户 |
| PUT | /api/stocktake-tasks/:id/count | 录入实盘数据 | 仓库管理员 |
| PUT | /api/stocktake-tasks/:id/confirm | 确认盘点（调整库存） | 仓库管理员 |

### 6.3 库存报表

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/reports/inventory/turnover | 库存周转率 | 教师/管理员 |
| GET | /api/reports/inventory/stagnant | 呆滞库存分析 | 教师/管理员 |
| GET | /api/reports/inventory/summary | 库存汇总 | 教师/管理员 |

---

## 7. 多人协作接口（WebSocket）

### 7.1 房间管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/rooms | 房间列表 | 登录用户 |
| POST | /api/rooms | 创建房间 | 教师 |
| GET | /api/rooms/:id | 房间详情（含角色分配） | 登录用户 |
| POST | /api/rooms/:id/join | 加入房间（选择角色） | 学生 |
| POST | /api/rooms/:id/leave | 离开房间 | 学生 |
| POST | /api/rooms/:id/start | 开始协作 | 教师 |
| POST | /api/rooms/:id/end | 结束协作 | 教师 |

**POST /api/rooms 请求体：**
```json
{
  "room_name": "第1组 - 基础流程练习",
  "scene_id": 1,
  "max_members": 5
}
```

**POST /api/rooms/:id/join 请求体：**
```json
{
  "role_code": "purchaser"    // purchaser / customer_service / dispatcher / warehouse_keeper / driver
}
```

### 7.2 WebSocket 事件

**客户端 → 服务端：**

| 事件名 | 数据 | 说明 |
|--------|------|------|
| `join_room` | `{ "room_id": 1 }` | 加入 WebSocket 房间 |
| `leave_room` | `{ "room_id": 1 }` | 离开 WebSocket 房间 |

**服务端 → 客户端（广播）：**

| 事件名 | 数据 | 说明 |
|--------|------|------|
| `order_created` | `{ "order": {...} }` | 新订单创建 |
| `order_status_changed` | `{ "order_id": 1, "old_status": "pending", "new_status": "dispatched", "operator": "调度员" }` | 订单状态变更 |
| `todo_notification` | `{ "role": "warehouse_keeper", "message": "新入库单待验收", "ref_id": 5 }` | 待办任务通知 |
| `event_injected` | `{ "event_type": "vehicle_breakdown", "data": {...} }` | 突发事件通知 |
| `member_joined` | `{ "user_name": "张三", "role": "driver" }` | 成员加入房间 |
| `member_left` | `{ "user_name": "张三", "role": "driver" }` | 成员离开房间 |
| `room_started` | `{ "scene_name": "基础流程练习" }` | 协作开始 |
| `room_ended` | `{ "scores": {...} }` | 协作结束 |

---

## 8. 教师后台接口

### 8.1 教学场景

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/teaching-scenes | 场景列表 | 教师 |
| POST | /api/teaching-scenes | 创建场景 | 教师 |
| PUT | /api/teaching-scenes/:id | 编辑场景 | 教师 |
| DELETE | /api/teaching-scenes/:id | 删除场景 | 教师 |

### 8.2 事件注入

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/events/inject | 注入突发事件 | 教师 |

**POST /api/events/inject 请求体：**
```json
{
  "group_id": 1,
  "event_type": "vehicle_breakdown",     // vehicle_breakdown / supplier_delay / quality_issue / surge_orders
  "data": {
    "vehicle_id": 3,
    "description": "粤A12345在广深高速K50处发动机故障"
  }
}
```

### 8.3 进度与评分

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/teacher/groups-progress | 各组进度概览 | 教师 |
| GET | /api/teacher/groups/:id/detail | 某组详细进度 | 教师 |
| GET | /api/teacher/scores | 成绩列表 | 教师 |
| GET | /api/teacher/scores/export | 导出成绩（Excel） | 教师 |
| GET | /api/teacher/operation-logs | 操作日志列表 | 教师 |
| GET | /api/teacher/operation-logs/:user_id | 某学生的操作日志 | 教师 |

---

## 9. 统计与报表接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/reports/dashboard | 仪表盘汇总数据 | 登录用户 |
| GET | /api/reports/purchase/summary | 采购汇总 | 教师/管理员 |
| GET | /api/reports/transport/summary | 运输汇总 | 教师/管理员 |
| GET | /api/reports/warehouse/utilization | 仓库利用率 | 教师/管理员 |
| GET | /api/reports/student/:id/score | 某学生评分详情 | 教师 |

**GET /api/reports/dashboard 响应示例：**
```json
{
  "code": 200,
  "data": {
    "pending_orders": 5,
    "in_transit": 3,
    "today_completed": 12,
    "low_stock_items": 4,
    "warehouse_utilization": 0.72,
    "current_score": 85
  }
}
```

---

*接口文档版本：v1.0 | 最后更新：2026-05-01*
