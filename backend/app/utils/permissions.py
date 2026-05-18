"""
RBAC 权限工具模块

提供 role_required 装饰器用于后端 API 权限控制，
以及 ROLE_PERMISSIONS 常量定义供前后端共用。

设计原则：
- admin 角色拥有所有权限（在装饰器中自动放行）
- teacher 角色拥有所有权限（教师需要全面控制）
- student 角色在教学练习模式下拥有大部分读写权限
- 业务角色（purchaser/dispatcher/warehouse_keeper 等）按职责分配权限
"""

from functools import wraps
from flask import jsonify
from flask_login import current_user


# ============================================================
# 权限常量定义 — 每个权限代码对应一组允许的角色
# 格式: 'module:action' -> set of allowed role codes
# admin 和 teacher 自动拥有所有权限，不需要在此列出
# ============================================================

ROLE_PERMISSIONS = {
    # --- 采购管理 ---
    'purchase:create': {'purchaser', 'student'},
    'purchase:approve': {'purchaser'},
    'purchase:reject': {'purchaser'},

    # --- 运输管理 ---
    'transport:create': {'customer_service', 'dispatcher', 'driver', 'student'},
    'transport:approve': {'dispatcher'},
    'transport:reject': {'dispatcher'},
    'transport:dispatch': {'dispatcher'},
    'transport:status_update': {'driver', 'dispatcher', 'student'},
    'transport:pod_sign': {'driver', 'dispatcher', 'student'},
    'transport:complete': {'driver', 'dispatcher', 'student'},

    # --- 仓储管理 ---
    'warehouse:create_inbound': {'warehouse_keeper', 'student'},
    'warehouse:create_outbound': {'warehouse_keeper', 'student'},
    'warehouse:inspect': {'warehouse_keeper'},
    'warehouse:shelve': {'warehouse_keeper'},
    'warehouse:pick': {'warehouse_keeper'},
    'warehouse:ship': {'warehouse_keeper'},

    # --- 库存管理 ---
    'inventory:view': {'warehouse_keeper', 'purchaser', 'dispatcher', 'customer_service', 'student'},
    'stockcount:create': {'warehouse_keeper', 'student'},
    'stockcount:count': {'warehouse_keeper', 'student'},
    'stockcount:reconcile': {'warehouse_keeper'},

    # --- 合同管理 ---
    'contract:create_purchase': {'purchaser', 'student'},
    'contract:approve_purchase': {'purchaser'},
    'contract:create_transport': {'customer_service', 'dispatcher', 'student'},
    'contract:approve_transport': {'dispatcher'},
    'contract:terminate': set(),  # 仅 admin（在装饰器中处理）

    # --- 财务管理 ---
    'finance:view': {'purchaser', 'customer_service', 'student'},
    'finance:pay': {'purchaser'},
    'finance:receive': {'customer_service'},

    # --- 基础数据 ---
    'supplier:manage': {'purchaser', 'student'},
    'customer:manage': {'customer_service', 'student'},
    'goods:manage': {'student'},
    'warehouse_data:manage': {'warehouse_keeper', 'student'},
    'vehicle:manage': {'dispatcher', 'student'},
    'driver:manage': {'dispatcher', 'student'},

    # --- 教师/管理功能 ---
    'teaching:manage': {'teacher'},
    'score:view_all': {'teacher'},
    'collab:close_room': {'teacher'},
    'report:view': {'teacher'},
    'export:data': {'teacher'},
    'user:manage': set(),  # 仅 admin
}

# admin 和 teacher 自动拥有的所有权限的角色列表
SUPER_ROLES = {'admin', 'teacher'}


def _has_permission(role_code, permission_code):
    """检查指定角色是否拥有某项权限"""
    if role_code in SUPER_ROLES:
        return True
    allowed_roles = ROLE_PERMISSIONS.get(permission_code, set())
    return role_code in allowed_roles


def _has_any_role(role_code, allowed_roles):
    """检查指定角色是否在允许的角色列表中"""
    if role_code in SUPER_ROLES:
        return True
    return role_code in allowed_roles


def role_required(*allowed_roles):
    """
    角色权限装饰器

    用法：
        @role_required('admin', 'purchaser')
        def approve_purchase(id):
            ...

    逻辑：
        - admin 和 teacher 角色自动放行
        - 其他角色检查是否在 allowed_roles 中
        - 未登录用户由 Flask-Login 的 login_required 处理（应先于本装饰器）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    'code': 401,
                    'message': '请先登录',
                    'data': None
                }), 200

            if not _has_any_role(current_user.role_code, set(allowed_roles)):
                return jsonify({
                    'code': 403,
                    'message': '无操作权限',
                    'data': None
                }), 200

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(permission_code):
    """
    细粒度权限装饰器（基于权限代码）

    用法：
        @permission_required('purchase:approve')
        def approve_purchase(id):
            ...

    逻辑：
        - admin 和 teacher 角色自动放行
        - 其他角色检查 ROLE_PERMISSIONS 中该权限代码对应的角色集合
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    'code': 401,
                    'message': '请先登录',
                    'data': None
                }), 200

            if not _has_permission(current_user.role_code, permission_code):
                return jsonify({
                    'code': 403,
                    'message': '无操作权限',
                    'data': None
                }), 200

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """快捷装饰器：仅允许 admin 角色"""
    @wraps(f)
    @role_required('admin')
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def get_user_permissions(role_code):
    """
    获取指定角色的所有权限代码列表（供前端使用）

    Args:
        role_code: 角色代码

    Returns:
        list[str]: 该角色拥有的所有权限代码
    """
    if role_code in SUPER_ROLES:
        return list(ROLE_PERMISSIONS.keys())
    return [code for code, roles in ROLE_PERMISSIONS.items() if role_code in roles]


def get_role_menu_permissions(role_code):
    """
    获取指定角色的菜单可见性配置（供前端 Layout.vue 使用）

    Returns:
        dict: 菜单权限配置
    """
    is_super = role_code in SUPER_ROLES
    is_student = role_code == 'student'

    # 教学模式下 student 可以看到所有菜单
    if is_super or is_student:
        return {
            'suppliers': True,
            'customers': True,
            'goods': True,
            'warehouses': True,
            'vehicles': True,
            'drivers': True,
            'purchase': True,
            'transport': True,
            'warehouse': True,
            'inventory': True,
            'reports': is_super,  # 报表仅 admin/teacher
            'contracts': True,
            'finance': True,
            'collab': True,
            'teacher': is_super,  # 教师后台仅 admin/teacher
            'alerts': True,
            'help': True,
            'users': is_super,  # 用户管理仅 admin
        }

    # 业务角色按职责显示菜单
    return {
        'suppliers': role_code == 'purchaser',
        'customers': role_code in ('customer_service', 'dispatcher'),
        'goods': True,  # 所有角色可查看商品
        'warehouses': role_code == 'warehouse_keeper',
        'vehicles': role_code == 'dispatcher',
        'drivers': role_code == 'dispatcher',
        'purchase': role_code == 'purchaser',
        'transport': role_code in ('customer_service', 'dispatcher', 'driver'),
        'warehouse': role_code == 'warehouse_keeper',
        'inventory': role_code == 'warehouse_keeper',
        'reports': False,
        'contracts': role_code in ('purchaser', 'customer_service'),
        'finance': role_code in ('purchaser', 'customer_service'),
        'collab': True,
        'teacher': False,
        'alerts': True,
        'help': True,
        'users': False,
    }
