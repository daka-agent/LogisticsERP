#!/usr/bin/env python3
"""第二阶段API测试脚本（无自定义函数版）"""
import requests, json

BASE = 'http://localhost:5000'
s = requests.Session()

# 1. 登录
print('=== 登录 ===')
r = s.post(f'{BASE}/api/auth/login', json={'username':'admin','password':'admin123'})
print(r.status_code, r.text[:200])

# 2. 创建商品
print('\n=== 创建商品 ===')
r = s.post(f'{BASE}/api/goods', json={'sku':'B001','name':'瓦楞纸箱','unit':'个','purchase_price':4.50})
print(r.status_code)
if r.status_code == 200:
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    goods_id = r.json()['data']['id']
else:
    print(r.text[:300])
    goods_id = None

if goods_id:
    # 3. 创建采购申请
    print('\n=== 创建采购申请 ===')
    r = s.post(f'{BASE}/api/purchase-requests', json={
        'goods_id': goods_id,
        'quantity': 500,
        'est_unit_price': 4.50,
        'reason': '库存不足，需要补货'
    })
    print(r.status_code)
    if r.status_code == 200:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
        pr_id = r.json()['data']['id']
    else:
        print(r.text[:300])
        pr_id = None

    if pr_id:
        # 4. 审批
        print('\n=== 审批采购申请 ===')
        r = s.put(f'{BASE}/api/purchase-requests/{pr_id}/approve', json={'comment':'同意'})
        print(r.status_code)
        if r.status_code == 200:
            print(json.dumps(r.json(), ensure_ascii=False, indent=2))

print('\n=== 测试完成 ===')
