#!/usr/bin/env python3
"""种子数据脚本 - 初始化角色、用户和业务数据"""
from app import create_app, db
from app.models import Role, User
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.goods import Category, Goods
from app.models.warehouse import Warehouse, Zone, Location
from decimal import Decimal

app = create_app()

with app.app_context():
    # 先创建所有表
    db.create_all()
    print("数据库表已创建")

    # ===== 1. 角色 =====
    roles_data = [
        {'code': 'admin', 'name': '系统管理员', 'description': '管理系统的所有功能和数据'},
        {'code': 'teacher', 'name': '教师', 'description': '创建教学场景、监控学生进度、评分'},
        {'code': 'student', 'name': '学生', 'description': '参与学习任务的学生'},
        {'code': 'purchaser', 'name': '采购专员', 'description': '负责采购申请和供应商管理'},
        {'code': 'customer_service', 'name': '客服', 'description': '负责接单和客户沟通'},
        {'code': 'dispatcher', 'name': '调度员', 'description': '负责车辆调度和路线规划'},
        {'code': 'warehouse_keeper', 'name': '仓库管理员', 'description': '负责出入库和库存管理'},
        {'code': 'driver', 'name': '司机', 'description': '负责运输执行'},
    ]

    for role_data in roles_data:
        if not Role.query.filter_by(code=role_data['code']).first():
            role = Role(**role_data)
            db.session.add(role)
            print(f"创建角色: {role_data['name']}")

    db.session.commit()
    print("角色数据初始化完成")

    # ===== 2. 用户 =====
    admin_role = Role.query.filter_by(code='admin').first()
    teacher_role = Role.query.filter_by(code='teacher').first()
    student_role = Role.query.filter_by(code='student').first()
    purchaser_role = Role.query.filter_by(code='purchaser').first()
    cs_role = Role.query.filter_by(code='customer_service').first()
    dispatcher_role = Role.query.filter_by(code='dispatcher').first()
    warehouse_role = Role.query.filter_by(code='warehouse_keeper').first()
    driver_role = Role.query.filter_by(code='driver').first()

    users_data = [
        ('admin', '系统管理员', admin_role, 'admin123'),
        ('teacher01', '张老师', teacher_role, '123456'),
        ('student01', '学生甲', student_role, '123456'),
        ('student02', '学生乙', student_role, '123456'),
        ('purchaser01', '采购员小李', purchaser_role, '123456'),
        ('cs01', '客服小王', cs_role, '123456'),
        ('dispatcher01', '调度员老赵', dispatcher_role, '123456'),
        ('keeper01', '仓管员小陈', warehouse_role, '123456'),
        ('driver01', '司机小刘', driver_role, '123456'),
    ]

    for username, real_name, role, pwd in users_data:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, real_name=real_name, role_id=role.id, status='active')
            user.password = pwd
            db.session.add(user)
            print(f"创建用户: {username} / {pwd}")

    db.session.commit()
    print("用户数据初始化完成")

    # ===== 3. 供应商 =====
    suppliers_data = [
        ('华东供应链有限公司', '李经理', '021-5555-1001', '上海市浦东新区供应链路88号', 4.5),
        ('南方物流科技有限公司', '王总监', '020-5555-2002', '广州市天河区科技园99号', 4.8),
        ('北方商贸集团', '赵部长', '010-5555-3003', '北京市朝阳区商贸大厦12层', 4.2),
        ('中原材料供应商', '孙经理', '0371-5555-4004', '郑州市高新区材料城A区', 4.0),
        ('西部仓储物流中心', '周主任', '028-5555-5005', '成都市青白江区物流港6号', 4.6),
    ]

    for name, contact, phone, address, rating in suppliers_data:
        if not Supplier.query.filter_by(name=name).first():
            s = Supplier(name=name, contact=contact, phone=phone,
                         address=address, rating=Decimal(str(rating)))
            db.session.add(s)
            print(f"创建供应商: {name}")

    db.session.commit()
    print("供应商数据初始化完成")

    # ===== 4. 客户 =====
    customers_data = [
        ('优品零售集团', '陈经理', '021-8888-1001', '上海市静安区南京路1266号', 'vip'),
        ('恒通电子科技', '林总', '0755-8888-2002', '深圳市南山区科技园大厦', 'good'),
        ('绿源食品加工厂', '吴主管', '0571-8888-3003', '杭州市余杭区食品工业园', 'normal'),
        ('金达建材有限公司', '郑经理', '023-8888-4004', '重庆市九龙坡区建材城B栋', 'normal'),
        ('宝康医药连锁', '黄采购', '020-8888-5005', '广州市越秀区医药广场3层', 'good'),
    ]

    for name, contact, phone, address, credit in customers_data:
        if not Customer.query.filter_by(name=name).first():
            c = Customer(name=name, contact=contact, phone=phone,
                         address=address, credit_level=credit)
            db.session.add(c)
            print(f"创建客户: {name}")

    db.session.commit()
    print("客户数据初始化完成")

    # ===== 5. 车辆 =====
    vehicles_data = [
        ('沪A12345', '中型', 10.0, 30.0, 'idle'),
        ('沪B23456', '大型', 20.0, 60.0, 'idle'),
        ('沪C34567', '冷藏', 8.0, 25.0, 'idle'),
        ('粤D45678', '中型', 10.0, 30.0, 'idle'),
        ('京E56789', '大型', 25.0, 80.0, 'idle'),
    ]

    for plate_no, v_type, weight, volume, status in vehicles_data:
        if not Vehicle.query.filter_by(plate_no=plate_no).first():
            v = Vehicle(plate_no=plate_no, type=v_type,
                        capacity_weight=Decimal(str(weight)),
                        capacity_volume=Decimal(str(volume)),
                        status=status)
            db.session.add(v)
            print(f"创建车辆: {plate_no}")

    db.session.commit()
    print("车辆数据初始化完成")

    # ===== 6. 司机 =====
    drivers_data = [
        ('刘大伟', '13800001001', 'A2', 'A2', 'available'),
        ('张志强', '13800002002', 'A1', 'A1', 'available'),
        ('王建国', '13800003003', 'B2', 'B2', 'available'),
        ('李文斌', '13800004004', 'A2', 'A2', 'available'),
        ('陈国强', '13800005005', 'A1', 'A1', 'available'),
    ]

    for name, phone, license_no, license_type, status in drivers_data:
        if not Driver.query.filter_by(name=name).first():
            d = Driver(name=name, phone=phone, license_no=license_no,
                       license_type=license_type, status=status)
            db.session.add(d)
            print(f"创建司机: {name}")

    db.session.commit()
    print("司机数据初始化完成")

    # ===== 7. 商品分类 =====
    categories_data = [
        ('电子元件', None, 1),
        ('食品原料', None, 2),
        ('建筑材料', None, 3),
        ('医疗器械', None, 4),
        ('日用消费品', None, 5),
        ('芯片', 1, 1),
        ('电阻电容', 1, 2),
        ('面粉', 2, 1),
        ('调味料', 2, 2),
    ]

    for name, parent_id, sort_order in categories_data:
        if not Category.query.filter_by(name=name).first():
            c = Category(name=name, parent_id=parent_id, sort_order=sort_order)
            db.session.add(c)
            print(f"创建分类: {name}")

    db.session.commit()
    print("商品分类初始化完成")

    # ===== 8. 商品 =====
    goods_data = [
        ('SKU001', 'CPU处理器', 'i7-13700K', '个', 1, 5, 50, 2000.00, 2800.00, 5),
        ('SKU002', '内存条', 'DDR5 16GB', '个', 1, 10, 100, 200.00, 350.00, 20),
        ('SKU003', '高筋面粉', '25kg/袋', '袋', 3, 20, 500, 80.00, 120.00, 50),
        ('SKU004', '酱油', '1.9L桶装', '箱', 4, 30, 200, 25.00, 45.00, 100),
        ('SKU005', '水泥', 'P.O 42.5 50kg/袋', '袋', 3, 50, 1000, 18.00, 30.00, 200),
        ('SKU006', '体温计', '电子款', '个', 4, 10, 200, 15.00, 35.00, 30),
        ('SKU007', '口罩', '医用N95', '箱', 4, 50, 500, 50.00, 98.00, 80),
        ('SKU008', '洗衣液', '2kg瓶装', '箱', 5, 20, 300, 30.00, 55.00, 60),
    ]

    for sku, name, spec, unit, cat_id, min_stock, max_stock, purchase, selling, safe_stock in goods_data:
        if not Goods.query.filter_by(sku=sku).first():
            g = Goods(sku=sku, name=name, spec=spec, unit=unit,
                      category_id=cat_id, min_stock=min_stock, max_stock=max_stock,
                      purchase_price=Decimal(str(purchase)),
                      selling_price=Decimal(str(selling)),
                      status='active')
            db.session.add(g)
            print(f"创建商品: {sku} - {name}")

    db.session.commit()
    print("商品数据初始化完成")

    # ===== 9. 仓库+库区+货位 =====
    warehouses_data = [
        ('上海总仓', '上海市闵行区物流园区88号', 'normal'),
        ('广州分仓', '广州市白云区物流大道56号', 'normal'),
        ('北京冷链仓', '北京市大兴区冷链物流中心', 'cold'),
    ]

    for name, address, w_type in warehouses_data:
        if not Warehouse.query.filter_by(name=name).first():
            w = Warehouse(name=name, address=address, type=w_type,
                          total_locations=0, used_locations=0)
            db.session.add(w)
            print(f"创建仓库: {name}")

    db.session.commit()
    print("仓库数据初始化完成")

    # 为上海总仓创建库区和货位
    sh_wh = Warehouse.query.filter_by(name='上海总仓').first()
    if sh_wh:
        zones_data = [
            ('A', 'A区-电子元件区', 1),
            ('B', 'B区-食品区', 2),
            ('C', 'C区-建材区', 3),
        ]
        for code, z_name, sort_order in zones_data:
            zone = Zone(warehouse_id=sh_wh.id, zone_code=code, zone_name=z_name, sort_order=sort_order)
            db.session.add(zone)
            print(f"创建库区: {sh_wh.name} - {z_name}")
        db.session.flush()

        # 为每个库区创建货位
        loc_count = 0
        zones = Zone.query.filter_by(warehouse_id=sh_wh.id).all()
        for zone in zones:
            for i in range(1, 6):
                loc = Location(
                    zone_id=zone.id,
                    loc_code=f'{zone.zone_code}-{i:02d}',
                    capacity_weight=Decimal('2.00'),
                    capacity_volume=Decimal('5.00'),
                    status='empty'
                )
                db.session.add(loc)
                loc_count += 1
        sh_wh.total_locations = loc_count
        print(f"创建 {loc_count} 个货位")

    # 为广州分仓创建库区
    gz_wh = Warehouse.query.filter_by(name='广州分仓').first()
    if gz_wh:
        for code, z_name, sort_order in [('A', 'A区-日用百货区', 1), ('B', 'B区-食品区', 2)]:
            zone = Zone(warehouse_id=gz_wh.id, zone_code=code, zone_name=z_name, sort_order=sort_order)
            db.session.add(zone)
            print(f"创建库区: {gz_wh.name} - {z_name}")
        db.session.flush()
        loc_count = 0
        zones = Zone.query.filter_by(warehouse_id=gz_wh.id).all()
        for zone in zones:
            for i in range(1, 4):
                loc = Location(
                    zone_id=zone.id,
                    loc_code=f'{zone.zone_code}-{i:02d}',
                    capacity_weight=Decimal('2.00'),
                    capacity_volume=Decimal('5.00'),
                    status='empty'
                )
                db.session.add(loc)
                loc_count += 1
        gz_wh.total_locations = loc_count
        print(f"创建 {loc_count} 个货位")

    db.session.commit()
    print("库区货位数据初始化完成")

    print("\n种子数据初始化完成！")
    print("===== 数据统计 =====")
    print(f"  角色: {Role.query.count()}个")
    print(f"  用户: {User.query.count()}个")
    print(f"  供应商: {Supplier.query.count()}个")
    print(f"  客户: {Customer.query.count()}个")
    print(f"  车辆: {Vehicle.query.count()}辆")
    print(f"  司机: {Driver.query.count()}名")
    print(f"  商品分类: {Category.query.count()}个")
    print(f"  商品: {Goods.query.count()}个")
    print(f"  仓库: {Warehouse.query.count()}个")
    print(f"  库区: {Zone.query.count()}个")
    print(f"  货位: {Location.query.count()}个")
