"""简单调试"""
import requests
import traceback

BASE_URL = 'http://localhost:5000/api'
s = requests.Session()

try:
    # 登录
    r = s.post(f'{BASE_URL}/auth/login', json={'username': 'admin', 'password': 'admin123'})
    print(f"1. 登录: OK")

    # 获取zones
    r = s.get(f'{BASE_URL}/warehouses/1/zones')
    print(f"2. zones: {r.status_code} {r.text[:200]}")

    # 获取locations
    r = s.get(f'{BASE_URL}/zones/1/locations')
    print(f"3. locations: {r.status_code} {r.text[:200]}")

    # 尝试拣货
    r = s.post(f'{BASE_URL}/outbound/2/pick', json={
        'items': [{
            'id': 2,
            'picked_qty': 10,
            'location_id': 1,
            'batch_no': 'BATCH001'
        }]
    })
    print(f"4. pick: {r.status_code} {r.text[:500]}")

except Exception as e:
    traceback.print_exc()
