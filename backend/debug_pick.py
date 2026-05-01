"""调试出库拣货"""
import requests

BASE_URL = 'http://localhost:5000/api'
s = requests.Session()

# 登录
r = s.post(f'{BASE_URL}/auth/login', json={'username': 'admin', 'password': 'admin123'})
print(f"登录: {r.json()['message']}")

# 获取出库单列表
r = s.get(f'{BASE_URL}/outbound')
outbounds = r.json()['data']
if outbounds:
    ob = outbounds[0]
    print(f"出库单: {ob['order_no']}, 状态: {ob['status']}")

    # 获取详情
    r = s.get(f'{BASE_URL}/outbound/{ob["id"]}')
    detail = r.json()['data']
    print(f"详情: {detail}")

    # 获取库存
    r = s.get(f'{BASE_URL}/inventory')
    inventory = r.json()['data']
    print(f"\n库存:")
    for inv in inventory:
        print(f"  - {inv['goods_name']}: 数量={inv['quantity']}, 可用={inv['available_qty']}, 货位={inv['loc_code']}, 批次={inv['batch_no']}, 仓库={inv['warehouse_id']}")

    # 获取货位
    r = s.get(f'{BASE_URL}/warehouses/1/zones')
    zones = r.json()['data']
    for zone in zones:
        r = s.get(f'{BASE_URL}/zones/{zone["id"]}/locations')
        locs = r.json()['data']
        for loc in locs:
            print(f"  货位: {loc['loc_code']} (ID: {loc['id']})")

    # 尝试拣货
    if ob['status'] == 'pending':
        items = detail.get('items', [])
        if items:
            item = items[0]
            pick_data = {
                'items': [{
                    'id': item['id'],
                    'picked_qty': 10,
                    'location_id': 1,
                    'batch_no': 'BATCH001'
                }]
            }
            print(f"\n拣货请求: {pick_data}")
            r = s.post(f'{BASE_URL}/outbound/{ob["id"]}/pick', json=pick_data)
            print(f"状态码: {r.status_code}")
            print(f"响应: {r.text}")
