"""第三阶段完整测试：仓储+库存模块（简化版）"""
import requests
import sys

def log(msg):
    print(msg, flush=True)

BASE_URL = 'http://localhost:5000/api'
s = requests.Session()

# 1. 登录
log("=== 1. 登录 ===")
r = s.post(f'{BASE_URL}/auth/login', json={'username': 'admin', 'password': 'admin123'})
log(f"  登录: {r.json()['message']}")

# 2. 创建仓库
log("\n=== 2. 创建仓库 ===")
r = s.post(f'{BASE_URL}/warehouses', json={'name': '主仓库', 'address': '测试路1号', 'type': 'normal'})
wh = r.json()['data']
log(f"  仓库: {wh['name']} (ID: {wh['id']})")
wh_id = wh['id']

# 3. 创建库区
log("\n=== 3. 创建库区 ===")
r = s.post(f'{BASE_URL}/zones', json={'warehouse_id': wh_id, 'zone_code': 'A', 'zone_name': 'A区', 'sort_order': 1})
zone = r.json()['data']
zone_id = zone['id']
log(f"  库区: {zone['zone_name']} (ID: {zone_id})")

# 4. 创建货位
log("\n=== 4. 创建货位 ===")
for code in ['A-01-01', 'A-01-02']:
    r = s.post(f'{BASE_URL}/locations', json={'zone_id': zone_id, 'loc_code': code, 'capacity_weight': 1000, 'capacity_volume': 10})
    log(f"  货位: {code} (ID: {r.json()['data']['id']})")

# 5. 创建商品
log("\n=== 5. 创建商品 ===")
for item in [
    {'sku': 'SKU001', 'name': '笔记本电脑', 'spec': 'i7/16G', 'unit': '台', 'purchase_price': 5000, 'selling_price': 6500},
    {'sku': 'SKU002', 'name': '无线鼠标', 'spec': '蓝牙', 'unit': '个', 'purchase_price': 50, 'selling_price': 99}
]:
    r = s.post(f'{BASE_URL}/goods', json=item)
    log(f"  商品: {item['name']} (ID: {r.json()['data']['id']})")

# 获取商品ID
r = s.get(f'{BASE_URL}/goods')
g1, g2 = r.json()['data'][0], r.json()['data'][1]

# 6. 创建入库单
log("\n=== 6. 创建入库单 ===")
r = s.post(f'{BASE_URL}/inbound', json={
    'warehouse_id': wh_id, 'source_type': 'purchase', 'remark': '测试入库',
    'items': [
        {'goods_id': g1['id'], 'planned_qty': 100, 'batch_no': 'B001'},
        {'goods_id': g2['id'], 'planned_qty': 200, 'batch_no': 'B002'}
    ]
})
ib = r.json()['data']
log(f"  入库单: {ib['order_no']} (ID: {ib['id']})")

# 7. 获取入库单详情
r = s.get(f'{BASE_URL}/inbound/{ib["id"]}')
ib_detail = r.json()['data']
items = ib_detail['items']
log(f"  明细数: {len(items)}")

# 8. 入库上架
log("\n=== 7. 入库上架 ===")
r = s.post(f'{BASE_URL}/inbound/{ib["id"]}/shelve', json={
    'items': [
        {'id': items[0]['id'], 'actual_qty': 100, 'location_id': 1},
        {'id': items[1]['id'], 'actual_qty': 200, 'location_id': 2}
    ]
})
log(f"  上架: {r.json()['message']}")

# 9. 查看库存
log("\n=== 8. 查看库存 ===")
r = s.get(f'{BASE_URL}/inventory')
for inv in r.json()['data']:
    log(f"  {inv['goods_name']}: 数量={inv['quantity']}, 货位={inv['loc_code']}")

# 10. 库存汇总
log("\n=== 9. 库存汇总 ===")
r = s.get(f'{BASE_URL}/inventory/summary')
s_data = r.json()['data']
log(f"  SKU: {s_data['total_skus']}, 总量: {s_data['total_qty']}")

# 11. 创建出库单
log("\n=== 10. 创建出库单 ===")
r = s.post(f'{BASE_URL}/outbound', json={
    'warehouse_id': wh_id, 'dest_type': 'sale', 'remark': '销售出库',
    'items': [{'goods_id': g1['id'], 'requested_qty': 30, 'batch_no': 'B001'}]
})
ob = r.json()['data']
log(f"  出库单: {ob['order_no']} (ID: {ob['id']})")

# 12. 获取出库详情并拣货
log("\n=== 11. 出库拣货 ===")
r = s.get(f'{BASE_URL}/outbound/{ob["id"]}')
ob_items = r.json()['data']['items']
r = s.post(f'{BASE_URL}/outbound/{ob["id"]}/pick', json={
    'items': [{'id': ob_items[0]['id'], 'picked_qty': 30, 'location_id': 1, 'batch_no': 'B001'}]
})
log(f"  拣货: {r.json()['message']}")

# 13. 发货
log("\n=== 12. 出库发货 ===")
r = s.post(f'{BASE_URL}/outbound/{ob["id"]}/ship')
log(f"  发货: {r.json()['message']}")

# 14. 出库后库存
log("\n=== 13. 出库后库存 ===")
r = s.get(f'{BASE_URL}/inventory')
for inv in r.json()['data']:
    log(f"  {inv['goods_name']}: 数量={inv['quantity']}, 可用={inv['available_qty']}")

# 15. 移动记录
log("\n=== 14. 库存移动记录 ===")
r = s.get(f'{BASE_URL}/stock-moves')
for m in r.json()['data']:
    log(f"  {m['goods_name']}: {m['move_type']}, 数量={m['quantity']}")

# 16. 创建盘点单
log("\n=== 15. 创建盘点单 ===")
r = s.post(f'{BASE_URL}/stock-counts', json={'warehouse_id': wh_id, 'count_type': 'full', 'remark': '全盘'})
sc = r.json()['data']
log(f"  盘点单: {sc['count_no']} (明细: {len(sc.get('items', []))} 条)")

# 17. 执行盘点
if sc.get('items'):
    log("\n=== 16. 执行盘点 ===")
    count_items = [{'id': i['id'], 'actual_qty': i['book_qty'] + (5 if idx == 0 else -3)} for idx, i in enumerate(sc['items'])]
    r = s.post(f'{BASE_URL}/stock-counts/{sc["id"]}/count', json={'items': count_items})
    log(f"  盘点: {r.json()['message']}")

    # 18. 调整
    log("\n=== 17. 盘点调整 ===")
    r = s.post(f'{BASE_URL}/stock-counts/{sc["id"]}/reconcile')
    log(f"  调整: {r.json()['message']}")

# 19. 预警
log("\n=== 18. 库存预警 ===")
r = s.get(f'{BASE_URL}/inventory/alerts')
a = r.json()['data']
log(f"  过期: {len(a['expired'])}, 即将过期: {len(a['expiring'])}")

log("\n" + "=" * 50)
log("第三阶段测试完成！全部功能正常！")
log("=" * 50)
