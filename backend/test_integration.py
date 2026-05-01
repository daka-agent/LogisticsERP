#!/usr/bin/env python3
"""补充测试：验证 transport / warehouse / inventory 的日志+评分集成"""
import sys, traceback
sys.path.insert(0, '.')

import requests

BASE = 'http://localhost:5000/api'
passed = 0
failed = 0
errors = []


def test(name, method, url, data=None, expect_code=200):
    global passed, failed, errors
    try:
        if method == 'GET':
            r = s.get(f'{BASE}{url}', params=data)
        elif method == 'POST':
            r = s.post(f'{BASE}{url}', json=data)
        elif method == 'PUT':
            r = s.put(f'{BASE}{url}', json=data)
        elif method == 'DELETE':
            r = s.delete(f'{BASE}{url}')
        else:
            r = s.get(f'{BASE}{url}')
        j = r.json()
        if j.get('code') == expect_code:
            passed += 1
            print(f'  PASS: {name}', flush=True)
        else:
            failed += 1
            msg = f'{name} - code={j.get("code")} msg={j.get("message")}'
            errors.append(msg)
            print(f'  FAIL: {msg}', flush=True)
        return j
    except Exception as e:
        failed += 1
        errors.append(f'{name} - {e}')
        print(f'  ERROR: {name} - {e}', flush=True)
        return {}


s = requests.Session()

# 登录
print('\n===== 补充测试：日志+评分集成 =====', flush=True)
test('登录', 'POST', '/auth/login', {'username': 'admin', 'password': 'admin123'})

# ===== 1. 运输模块集成测试 =====
print('\n--- 运输模块日志+评分 ---', flush=True)

# 创建运输订单
res = test('创建运输订单', 'POST', '/orders', {
    'customer_id': 1, 'origin': '上海', 'destination': '北京',
    'goods_name': '测试商品', 'weight': 100, 'volume': 2
})
order_id = res.get('data', {}).get('id')

if order_id:
    test('审核通过运输订单', 'PUT', f'/orders/{order_id}/approve')

# 验证日志记录
res = test('查询运输日志', 'GET', '/operation-logs', {'module': 'transport_order'})
items = res.get('data', {}).get('items', [])
if len(items) >= 2:
    passed += 1
    print(f'  PASS: 运输日志记录 {len(items)}条 (create+approve)', flush=True)
else:
    failed += 1
    print(f'  FAIL: 运输日志记录 期望>=2 实际={len(items)}', flush=True)

# 调度运输订单
if order_id:
    res = test('调度运输订单', 'PUT', f'/orders/{order_id}/dispatch', {
        'vehicle_id': 1, 'driver_id': 1
    })

# 驳回测试（新创建一个订单来驳回）
res2 = test('创建运输订单(驳回测试)', 'POST', '/orders', {
    'customer_id': 1, 'origin': '广州', 'destination': '深圳',
    'goods_name': '驳回测试', 'weight': 50
})
order_id2 = res2.get('data', {}).get('id')
if order_id2:
    test('驳回运输订单', 'PUT', f'/orders/{order_id2}/reject', {'comment': '测试驳回'})

# 状态更新
if order_id:
    test('更新运输状态(in_transit)', 'PUT', f'/orders/{order_id}/status', {'status': 'in_transit'})
    test('更新运输状态(arrived)', 'PUT', f'/orders/{order_id}/status', {'status': 'arrived'})
    test('更新运输状态(signed)', 'PUT', f'/orders/{order_id}/status', {'status': 'signed'})
    test('更新运输状态(completed)', 'PUT', f'/orders/{order_id}/status', {'status': 'completed'})

# 添加跟踪记录
if order_id:
    test('添加运输跟踪记录', 'POST', '/transport-records', {
        'order_id': order_id, 'status': 'in_transit',
        'location': '南京', 'description': '途经南京'
    })

# 验证完整日志
res = test('查询运输完整日志', 'GET', '/operation-logs', {'module': 'transport_order'})
items = res.get('data', {}).get('items', [])
if len(items) >= 6:
    passed += 1
    print(f'  PASS: 运输完整日志 {len(items)}条', flush=True)
else:
    failed += 1
    print(f'  FAIL: 运输完整日志 期望>=6 实际={len(items)}', flush=True)


# ===== 2. 仓储模块集成测试 =====
print('\n--- 仓储模块日志+评分 ---', flush=True)

# 创建入库单
res = test('创建入库单', 'POST', '/inbound', {
    'warehouse_id': 1,
    'source_type': 'purchase',
    'remark': '测试入库',
    'items': [{'goods_id': 1, 'planned_qty': 20, 'batch_no': 'B20260501'}]
})
inbound_id = res.get('data', {}).get('id')

# 入库上架
if inbound_id:
    res = test('入库上架', 'POST', f'/inbound/{inbound_id}/shelve', {
        'items': [{'id': 1, 'actual_qty': 20, 'location_id': 1}]
    })

# 验证入库日志
res = test('查询入库日志', 'GET', '/operation-logs', {'module': 'inbound_order'})
items = res.get('data', {}).get('items', [])
if len(items) >= 2:
    passed += 1
    print(f'  PASS: 入库日志记录 {len(items)}条', flush=True)
else:
    failed += 1
    print(f'  FAIL: 入库日志记录 期望>=2 实际={len(items)}', flush=True)

# 创建出库单
res = test('创建出库单', 'POST', '/outbound', {
    'warehouse_id': 1,
    'dest_type': 'sale',
    'remark': '测试出库',
    'items': [{'goods_id': 1, 'requested_qty': 5, 'batch_no': 'B20260501'}]
})
outbound_id = res.get('data', {}).get('id')

# 出库拣货
if outbound_id:
    res_pick = test('出库拣货', 'POST', f'/outbound/{outbound_id}/pick', {
        'items': [{'id': 1, 'picked_qty': 5, 'location_id': 1, 'batch_no': 'B20260501'}]
    })
    # 如果拣货成功，继续发货
    if res_pick.get('code') == 200:
        test('出库发货', 'POST', f'/outbound/{outbound_id}/ship')

# 验证出库日志
res = test('查询出库日志', 'GET', '/operation-logs', {'module': 'outbound_order'})
items = res.get('data', {}).get('items', [])
if len(items) >= 2:
    passed += 1
    print(f'  PASS: 出库日志记录 {len(items)}条', flush=True)
else:
    failed += 1
    print(f'  FAIL: 出库日志记录 期望>=2 实际={len(items)}', flush=True)


# ===== 3. 库存盘点模块集成测试 =====
print('\n--- 库存盘点模块日志+评分 ---', flush=True)

# 创建盘点单
res = test('创建盘点单', 'POST', '/stock-counts', {
    'warehouse_id': 1,
    'count_type': 'partial',
    'remark': '测试盘点'
})
count_id = res.get('data', {}).get('id')

# 执行盘点
if count_id:
    # 先获取盘点单详情找到items
    res_detail = test('获取盘点详情', 'GET', f'/stock-counts/{count_id}')
    count_items = res_detail.get('data', {}).get('items', [])
    if count_items:
        count_data = []
        for ci in count_items:
            count_data.append({'id': ci['id'], 'actual_qty': ci.get('book_qty', 20)})
        test('执行盘点', 'POST', f'/stock-counts/{count_id}/count', {'items': count_data})
        test('盘点调整', 'POST', f'/stock-counts/{count_id}/reconcile')

# 验证盘点日志
res = test('查询盘点日志', 'GET', '/operation-logs', {'module': 'stock_count'})
items = res.get('data', {}).get('items', [])
if len(items) >= 3:
    passed += 1
    print(f'  PASS: 盘点日志记录 {len(items)}条', flush=True)
else:
    failed += 1
    print(f'  FAIL: 盘点日志记录 期望>=3 实际={len(items)}', flush=True)


# ===== 4. 综合验证 =====
print('\n--- 综合验证 ---', flush=True)

# 查询所有日志
res = test('查询全部日志', 'GET', '/operation-logs')
items = res.get('data', {}).get('items', [])
if len(items) >= 10:
    passed += 1
    print(f'  PASS: 全部日志 {len(items)}条', flush=True)
else:
    failed += 1
    print(f'  FAIL: 全部日志 期望>=10 实际={len(items)}', flush=True)

# 查询日志统计
res = test('日志统计', 'GET', '/operation-logs/stats')
stats = res.get('data', {})
if stats.get('module_stats'):
    module_names = [m.get('module') for m in stats['module_stats']]
    expected_modules = ['purchase_request', 'transport_order', 'inbound_order', 'outbound_order', 'stock_count']
    found = [m for m in expected_modules if m in module_names]
    if len(found) >= 4:
        passed += 1
        print(f'  PASS: 日志统计覆盖模块 {len(found)}/{len(expected_modules)}: {found}', flush=True)
    else:
        failed += 1
        print(f'  FAIL: 日志统计覆盖不足 期望>=4 实际={len(found)}: {found}', flush=True)
else:
    failed += 1
    print(f'  FAIL: 日志统计数据格式异常', flush=True)

# 查询评分（应该有大量得分）
res = test('查询个人评分', 'GET', '/scores/user/1')
total = res.get('data', {}).get('total', 0)
op_count = res.get('data', {}).get('operation_count', 0)
if total > 50:
    passed += 1
    print(f'  PASS: 个人总评分 {total}分，操作数 {op_count}', flush=True)
else:
    failed += 1
    print(f'  FAIL: 个人总评分偏低 期望>50 实际={total}', flush=True)

# 查询评分明细（应覆盖多个模块）
res = test('查询评分明细', 'GET', '/scores/all')
detail_items = res.get('data', {}).get('items', [])
modules_in_scores = set(d.get('module') for d in detail_items)
if len(modules_in_scores) >= 5:
    passed += 1
    print(f'  PASS: 评分明细覆盖 {len(modules_in_scores)}个模块: {modules_in_scores}', flush=True)
else:
    failed += 1
    print(f'  FAIL: 评分明细覆盖不足 期望>=5 实际={len(modules_in_scores)}: {modules_in_scores}', flush=True)


# ===== 结果 =====
print(f'\n===== 测试结果: {passed} 通过, {failed} 失败 =====', flush=True)
if errors:
    print('失败项:', flush=True)
    for e in errors:
        print(f'  - {e}', flush=True)
