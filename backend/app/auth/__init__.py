from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码不能为空', 'data': None}), 200

    user = User.query.filter_by(username=data['username']).first()

    if user is None or not user.verify_password(data['password']):
        return jsonify({'code': 401, 'message': '用户名或密码错误', 'data': None}), 200

    if user.status != 'active':
        return jsonify({'code': 403, 'message': '账号已被禁用', 'data': None}), 200

    login_user(user)

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': user.to_dict()
    }), 200


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """退出登录"""
    logout_user()
    return jsonify({'code': 200, 'message': 'success', 'data': None}), 200


@bp.route('/me', methods=['GET'])
@login_required
def me():
    """获取当前登录用户信息"""
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': current_user.to_dict()
    }), 200
