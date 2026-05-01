#!/usr/bin/env python3
"""简化版集成测试 - 验证所有模块的日志+评分集成"""
import requests, sys

BASE = 'http://localhost:5001/api'
s = requests.Session()

print('===== 集成测试 =====', flush=True)

# 1. 登录
r = s.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin123'})
assert r.json().get('code') == 200, 'Login failed'
print('PASS: 登录', flush=True)

# 2. 运输模块
print('\n--- 运输 ---', flush=True)
r = s.post(f'{BASE}/orders', json={'customer_id': 1, 'origin': 'SH', 'destination': 'BJ', 'goods_name': 'test', 'weight': 100, 'volume': 2})
order_id = r.json()['data']['id']
print(f'PASS: 创建运输订单 id={order_id}', flush=True)

s.put(f'{BASE}/orders/{order_id}/approve')
print('PASS: 审批', flush=True)

s.put(f'{BASE}/orders/{order_id}/dispatch', json={'vehicle_id': 1, 'driver_id': 1})
print('PASS: 调度', flush=True)

for status in ['in_transit', 'arrived', 'signed', 'completed']:
    r = s.put(f'{BASE}/orders/{order_id}/status', json={'status': status})
    assert r.json().get('code') == 200, f'status {status} failed: {r.json()}'
    print(f'PASS: 状态->{status}', flush=True)

# 3. 仓储模块 - 入库
print('\n--- 入库 ---', flush=True)
r = s.post(f'{BASE}/inbound', json={
    'warehouse_id': 1, 'source_type': 'purchase', 'remark': 'test',
    'items': [{'goods_id': 1, 'planned_qty': 20, 'batch_no': 'B001'}]
})
inbound_id = r.json()['data']['id']
print(f'PASS: 创建入库单 id={inbound_id}', flush=True)

r = s.get(f'{BASE}/inbound/{inbound_id}')
items = r.json()['data']['items']
item_id = items[0]['id'] if items else None
print(f'PASS: 获取入库单详情 item_id={item_id}', flush=True)

if item_id:
    r = s.post(f'{BASE}/inbound/{inbound_id}/shelve', json={
        'items': [{'id': item_id, 'actual_qty': 20, 'location_id': 1}]
    })
    assert r.json().get('code') == 200, f'shelve failed: {r.json()}'
    print('PASS: 上架', flush=True)

# 4. 仓储模块 - 出库
print('\n--- 出库 ---', flush=True)
r = s.post(f'{BASE}/outbound', json={
    'warehouse_id': 1, 'dest_type': 'sale', 'remark': 'test',
    'items': [{'goods_id': 1, 'requested_qty': 5, 'batch_no': 'B001'}]
})
d = r.json()
print(f'create outbound: code={d.get("code")} data_keys={list(d.get("data", {}).keys()) if d.get("data") else "None"}', flush=True)
outbound_id = d.get('data', {}).get('id')
print(f'PASS: 创建出库单 id={outbound_id}', flush=True)

if not outbound_id:
    print('FAIL: outbound_id is None', flush=True)
    sys.exit(1)

r = s.get(f'{BASE}/outbound/{outbound_id}')
d = r.json()
items = d.get('data', {}).get('items', [])
print(f'outbound items count: {len(items)}', flush=True)
out_item_id = items[0]['id'] if items else None
print(f'out_item_id: {out_item_id}', flush=True)

if out_item_id:
    r = s.post(f'{BASE}/outbound/{outbound_id}/pick', json={
        'items': [{'id': out_item_id, 'picked_qty': 5, 'location_id': 1, 'batch_no': 'B001'}]
    })
    print(f'PASS: 拣货 code={r.json().get("code")}', flush=True)
    if r.json().get('code') == 200:
        r = s.post(f'{BASE}/outbound/{outbound_id}/ship')
        print(f'PASS: 发货 code={r.json().get("code")}', flush=True)

# 5. 库存盘点
print('\n--- 盘点 ---', flush=True)
r = s.post(f'{BASE}/stock-counts', json={'warehouse_id': 1, 'count_type': 'partial', 'remark': 'test'})
count_id = r.json()['data']['id']
print(f'PASS: 创建盘点单 id={count_id}', flush=True)

r = s.get(f'{BASE}/stock-counts/{count_id}')
count_items = r.json()['data']['items']
if count_items:
    count_data = [{'id': ci['id'], 'actual_qty': ci.get('book_qty', 20)} for ci in count_items]
    r = s.post(f'{BASE}/stock-counts/{count_id}/count', json={'items': count_data})
    print(f'PASS: 执行盘点 code={r.json().get("code")}', flush=True)
    r = s.post(f'{BASE}/stock-counts/{count_id}/reconcile')
    print(f'PASS: 盘点调整 code={r.json().get("code")}', flush=True)

# 6. 验证日志
print('\n--- 验证 ---', flush=True)
r = s.get(f'{BASE}/operation-logs')
all_items = r.json()['data']['items']
modules = set(i['module'] for i in all_items)
print(f'PASS: 总日志 {len(all_items)} 条, 覆盖模块: {modules}', flush=True)

# 7. 验证评分
r = s.get(f'{BASE}/scores/user/1')
score_data = r.json()['data']
print(f'PASS: 个人评分 total={score_data.get("total")} ops={score_data.get("operation_count")}', flush=True)

r = s.get(f'{BASE}/scores/all')
detail = r.json()['data']['items']
score_modules = set(d['module'] for d in detail)
print(f'PASS: 评分覆盖 {len(score_modules)} 个模块: {score_modules}', flush=True)

print('\n===== ALL TESTS PASSED =====', flush=True)
