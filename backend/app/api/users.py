"""用户管理 API（仅管理员可用）"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.role import Role
from app.utils.permissions import admin_required

bp = Blueprint('users', __name__)


@bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """获取用户列表"""
    role_code = request.args.get('role_code')
    status = request.args.get('status')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = User.query

    if role_code:
        role = Role.query.filter_by(code=role_code).first()
        if role:
            query = query.filter_by(role_id=role.id)
    if status:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            db.or_(
                User.username.contains(keyword),
                User.real_name.contains(keyword)
            )
        )

    query = query.order_by(User.created_at.desc())
    total = query.count()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': [u.to_dict() for u in pagination.items],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)
    data = user.to_dict()
    # 附加角色信息
    if user.role:
        data['role'] = user.role.to_dict()
    return jsonify({'code': 200, 'message': 'success', 'data': data})


@bp.route('/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    """创建用户"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('real_name'):
        return jsonify({'code': 400, 'message': '用户名和姓名不能为空', 'data': None})

    if not data.get('password'):
        return jsonify({'code': 400, 'message': '密码不能为空', 'data': None})

    # 检查用户名唯一性
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code': 400, 'message': '用户名已存在', 'data': None})

    # 获取角色
    role_code = data.get('role_code', 'student')
    role = Role.query.filter_by(code=role_code).first()
    if not role:
        return jsonify({'code': 400, 'message': f'角色 {role_code} 不存在', 'data': None})

    user = User(
        username=data['username'],
        real_name=data['real_name'],
        role_id=role.id,
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        status=data.get('status', 'active')
    )
    user.password = data['password']

    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 200, 'message': '用户创建成功', 'data': user.to_dict()})


@bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)

    # 禁止修改自己的角色
    if user.id == current_user.id and request.get_json().get('role_code'):
        return jsonify({'code': 400, 'message': '不能修改自己的角色', 'data': None})

    data = request.get_json()

    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'status' in data:
        user.status = data['status']

    # 角色变更
    if 'role_code' in data:
        role = Role.query.filter_by(code=data['role_code']).first()
        if not role:
            return jsonify({'code': 400, 'message': f'角色 {data["role_code"]} 不存在', 'data': None})
        user.role_id = role.id

    db.session.commit()

    return jsonify({'code': 200, 'message': '用户信息已更新', 'data': user.to_dict()})


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """禁用用户（软删除）"""
    if user_id == current_user.id:
        return jsonify({'code': 400, 'message': '不能禁用自己的账号', 'data': None})

    user = User.query.get_or_404(user_id)
    user.status = 'inactive'
    db.session.commit()

    return jsonify({'code': 200, 'message': '用户已禁用', 'data': None})


@bp.route('/users/<int:user_id>/reset-password', methods=['PUT'])
@login_required
@admin_required
def reset_password(user_id):
    """重置用户密码"""
    data = request.get_json()

    if not data or not data.get('password'):
        return jsonify({'code': 400, 'message': '新密码不能为空', 'data': None})

    user = User.query.get_or_404(user_id)
    user.password = data['password']
    db.session.commit()

    return jsonify({'code': 200, 'message': '密码已重置', 'data': None})


@bp.route('/users/roles', methods=['GET'])
@login_required
@admin_required
def get_roles():
    """获取所有角色列表"""
    roles = Role.query.order_by(Role.id).all()
    return jsonify({'code': 200, 'message': 'success', 'data': [r.to_dict() for r in roles]})
