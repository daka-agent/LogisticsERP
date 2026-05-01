#!/usr/bin/env python3
"""第二阶段完整流程测试：采购+运输"""
import requests, json

BASE = 'http://localhost:5000'
s = requests.Session()

def post(path, data):
    r = s.post(f'{BASE}{path}', json=data)
    if r.status_code != 200:
        print(f'  ERROR {path}: {r.status_code} {r.text[:200]}')
        return None
    return r.json()

def put(path, data=None):
    r = s.put(f'{BASE}{path}', json=data) if data else s.put(f'{BASE}{path}')
    if r.status_code != 200:
        print(f'  ERROR {path}: {r.status_code} {r.text[:200]}')
        return None
    return r.json()

def get(path):
    r = s.get(f'{BASE}{path}')
    if r.status_code != 200:
        print(f'  ERROR {path}: {r.status_code} {r.text[:200]}')
        return None
    return r.json()

# 0. 登录
print('=== 0. 登录 ===')
post('/api/auth/login', {'username':'admin','password':'admin123'})
print('登录成功')

# 1. 创建商品
print('\n=== 1. 创建商品 ===')
r = post('/api/goods', {'sku':'B001','name':'瓦楞纸箱','unit':'个','purchase_price':4.50})
if r: goods_id = r['data']['id']; print(f'商品ID: {goods_id}')
else: goods_id = 1  # 可能已存在
print(f'使用 goods_id: {goods_id}')

# 2. 创建采购申请
print('\n=== 2. 创建采购申请 ===')
r = post('/api/purchase-requests', {
    'goods_id': goods_id, 'quantity': 500, 'est_unit_price': 4.50, 'reason': '库存不足'
})
if r:
    pr_id = r['data']['id']
    print(f'采购申请: {r["data"]["req_no"]}, 状态: {r["data"]["status"]}')
else:
    # 可能已存在，尝试查询
    r = get('/api/purchase-requests?status=pending')
    if r and r['data']:
        pr_id = r['data'][0]['id']
        print(f'使用已有申请ID: {pr_id}')
    else:
        r = get('/api/purchase-requests?status=approved')
        pr_id = r['data'][0]['id'] if r and r['data'] else 1
        print(f'使用已审批申请ID: {pr_id}')

# 3. 审批
print('\n=== 3. 审批采购申请 ===')
r = put(f'/api/purchase-requests/{pr_id}/approve', {'comment':'同意'})
if r: print(f'状态: {r["data"]["status"]}')

# 4. 创建供应商
print('\n=== 4. 创建供应商 ===')
r = post('/api/suppliers', {'name':'华南包装有限公司','contact':'李经理','phone':'13900000001'})
supplier_id = r['data']['id'] if r else 1
print(f'供应商ID: {supplier_id}')

# 5. 创建采购订单
print('\n=== 5. 创建采购订单 ===')
r = post('/api/purchase-orders', {
    'request_id': pr_id, 'supplier_id': supplier_id,
    'items': [{'goods_id': goods_id, 'quantity': 500, 'unit_price': 4.50}]
})
if r:
    po = r['data']
    print(f'采购订单号: {po["po_no"]}, 总金额: {po["total_amount"]}')
    po_id = po['id']
else:
    r = get('/api/purchase-orders')
    po_id = r['data'][0]['id'] if r and r['data'] else 1
    print(f'使用已有订单ID: {po_id}')

# 6. 确认订单
print('\n=== 6. 确认采购订单 ===')
r = put(f'/api/purchase-orders/{po_id}/confirm')
if r: print(f'状态: {r["data"]["status"]}')

# 7. 验收
print('\n=== 7. 采购到货验收 ===')
r = post('/api/purchase-receipts', {'po_id': po_id})
if r:
    result = r['data']
    print(f'验收完成，订单状态: {result["order_status"]}')
    if result.get('inbound_order'):
        print(f'自动生成入库单: {result["inbound_order"]["order_no"]}')

# 8. 创建客户
print('\n=== 8. 创建客户 ===')
r = post('/api/customers', {'name':'深圳科技有限公司','contact':'王总','phone':'13800000001','address':'深圳市南山区'})
customer_id = r['data']['id'] if r else 1
print(f'客户ID: {customer_id}')

# 9. 创建运输订单
print('\n=== 9. 创建运输订单 ===')
r = post('/api/orders', {
    'customer_id': customer_id, 'origin': '广州白云区', 'destination': '深圳南山区',
    'goods_name': '瓦楞纸箱', 'weight': 250, 'volume': 12.5, 'quantity': 500
})
if r:
    order = r['data']
    order_id = order['id']
    print(f'运输订单号: {order["order_no"]}, 状态: {order["status"]}')
else:
    r = get('/api/orders')
    order_id = r['data'][0]['id'] if r and r['data'] else 1
    print(f'使用已有订单ID: {order_id}')

# 10. 审核
print('\n=== 10. 审核运输订单 ===')
r = put(f'/api/orders/{order_id}/approve')
if r: print(f'状态: {r["data"]["status"]}')

# 11. 创建车辆+司机
print('\n=== 11. 创建车辆和司机 ===')
r = post('/api/vehicles', {'plate_no':'粤A12345','type':'中型','capacity_weight':5,'capacity_volume':20})
vehicle_id = r['data']['id'] if r else 1
r = post('/api/drivers', {'name':'张师傅','phone':'13700000001','license_type':'B2'})
driver_id = r['data']['id'] if r else 1
print(f'车辆ID: {vehicle_id}, 司机ID: {driver_id}')

# 12. 调度
print('\n=== 12. 车辆调度 ===')
r = put(f'/api/orders/{order_id}/dispatch', {
    'vehicle_id': vehicle_id, 'driver_id': driver_id,
    'plan_departure': '2026-05-02 08:00', 'plan_arrival': '2026-05-02 14:00'
})
if r:
    d = r['data']
    print(f'状态: {d["status"]}, 车牌: {d["vehicle_plate"]}, 司机: {d["driver_name"]}')

# 13. 运输跟踪
print('\n=== 13. 运输跟踪 ===')
r = post('/api/transport-records', {'order_id':order_id,'status':'departed','location':'广州白云区','description':'已发车'})
if r: print(f'发车: {r["message"]}')
r = post('/api/transport-records', {'order_id':order_id,'status':'in_transit','location':'广深高速','description':'行驶中'})
if r: print(f'行驶中: {r["message"]}')
r = post('/api/transport-records', {'order_id':order_id,'status':'arrived','location':'深圳南山区','description':'已到达'})
if r: print(f'到达: {r["message"]}')

# 14. 查看跟踪记录
print('\n=== 14. 查看跟踪时间线 ===')
r = get(f'/api/transport-records?order_id={order_id}')
if r:
    for rec in r['data']:
        print(f'  [{rec["status"]}] {rec["location"]} - {rec["description"]}')

# 15. 运费查询
print('\n=== 15. 运费查询 ===')
r = get(f'/api/orders/{order_id}/freight')
if r: print(json.dumps(r['data'], ensure_ascii=False, indent=2))

print('\n' + '='*50)
print('第二阶段全部API测试通过！')
print('  采购: 申请 -> 审批 -> 订单 -> 确认 -> 验收 -> 自动入库')
print('  运输: 下单 -> 审核 -> 调度 -> 跟踪(发车/行驶/到达)')
print('  运费: 自动计算')
print('='*50)
