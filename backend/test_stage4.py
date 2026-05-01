#!/usr/bin/env python3
"""第四阶段集成测试脚本"""
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


# 创建 session
s = requests.Session()

# 登录
print('\n===== 第四阶段集成测试 =====', flush=True)
test('登录', 'POST', '/auth/login', {'username': 'admin', 'password': 'admin123'})

# ===== 教学场景管理 =====
print('\n--- 教学场景管理 ---', flush=True)
res = test('获取场景列表', 'GET', '/scenes')
scenes = res.get('data', [])
count = len(scenes)
if count >= 5:
    passed += 1
    print(f'  PASS: 预设场景数量 {count}个', flush=True)
else:
    failed += 1
    print(f'  FAIL: 预设场景数量 期望>=5 实际={count}', flush=True)

res = test('创建场景', 'POST', '/scenes', {
    'name': '测试场景A', 'description': '测试', 'difficulty': 'easy',
    'events_config': [{'type': 'test', 'description': 'test', 'trigger': 'manual'}],
    'scoring_rules': {'time_limit_minutes': 30, 'full_score': 80}
})
scene_id = res.get('data', {}).get('id')

if scene_id:
    test('获取场景详情', 'GET', f'/scenes/{scene_id}')
    test('更新场景', 'PUT', f'/scenes/{scene_id}', {'description': '已更新'})
    test('删除场景', 'DELETE', f'/scenes/{scene_id}')

# ===== 协作房间 =====
print('\n--- 协作房间 ---', flush=True)
res = test('创建房间', 'POST', '/rooms', {'group_name': '测试组X', 'scene_id': 1})
room_id = res.get('data', {}).get('id')

if room_id:
    test('获取房间列表', 'GET', '/rooms')
    test('获取房间详情', 'GET', f'/rooms/{room_id}')
    test('获取房间进度', 'GET', f'/rooms/{room_id}/progress')
    test('离开房间', 'POST', f'/rooms/{room_id}/leave')
    test('关闭房间', 'POST', f'/rooms/{room_id}/close')

# ===== 突发事件 =====
print('\n--- 突发事件 ---', flush=True)
# 先创建一个活跃房间来注入事件
res = test('创建活跃房间', 'POST', '/rooms', {'group_name': '事件测试组'})
active_room_id = res.get('data', {}).get('id')

res = test('获取事件类型', 'GET', '/events/types')
evt_types = res.get('data', [])
if len(evt_types) >= 6:
    passed += 1
    print(f'  PASS: 事件类型 {len(evt_types)}个', flush=True)
else:
    failed += 1
    print(f'  FAIL: 事件类型 期望>=6 实际={len(evt_types)}', flush=True)

if active_room_id:
    test('注入事件', 'POST', '/events/inject', {
        'group_id': active_room_id,
        'event_type': 'vehicle_breakdown',
        'description': '车辆故障测试'
    })

# ===== 操作日志 =====
print('\n--- 操作日志 ---', flush=True)
test('查询日志', 'GET', '/operation-logs')
test('日志统计', 'GET', '/operation-logs/stats')

# ===== 评分系统 =====
print('\n--- 评分系统 ---', flush=True)
if active_room_id:
    res = test('小组评分', 'GET', f'/scores/group/{active_room_id}')
    data = res.get('data', {})
    if 'total' in data and 'operation_score' in data:
        passed += 1
        print(f'  PASS: 评分数据格式正确', flush=True)
    else:
        failed += 1
        print(f'  FAIL: 评分数据格式异常', flush=True)

test('个人评分', 'GET', '/scores/user/1')
test('评分排行', 'GET', '/scores/ranking')
test('小组排行', 'GET', '/scores/group-ranking')
test('评分明细', 'GET', '/scores/all')

# ===== 业务操作日志+评分集成 =====
print('\n--- 业务操作(日志+评分) ---', flush=True)
res = test('创建采购申请', 'POST', '/purchase-requests', {'goods_id': 1, 'quantity': 10})
pr_id = res.get('data', {}).get('id')

if pr_id:
    # 审批
    test('审批采购申请', 'PUT', f'/purchase-requests/{pr_id}/approve', {'comment': '同意'})

# 查询操作日志（应该有创建+审批记录）
res = test('查询采购日志', 'GET', '/operation-logs', {'module': 'purchase_request'})
items = res.get('data', {}).get('items', [])
if len(items) >= 2:
    passed += 1
    print(f'  PASS: 操作日志记录 {len(items)}条', flush=True)
else:
    failed += 1
    print(f'  FAIL: 操作日志记录 期望>=2 实际={len(items)}', flush=True)

# 查询用户评分（应该有得分）
res = test('查询用户评分', 'GET', '/scores/user/1')
total = res.get('data', {}).get('total', 0)
if total > 0:
    passed += 1
    print(f'  PASS: 用户评分 total={total}', flush=True)
else:
    failed += 1
    print(f'  FAIL: 用户评分为0', flush=True)

# ===== 结果 =====
print(f'\n===== 测试结果: {passed} 通过, {failed} 失败 =====', flush=True)
if errors:
    print('失败项:', flush=True)
    for e in errors:
        print(f'  - {e}', flush=True)
