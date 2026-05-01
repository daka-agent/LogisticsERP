"""协作房间管理 API"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.collab import OperationLog, Score
from app.models.group import Group
from app.models.user import User
from app.models.role import Role
from app.models.teaching import TeachingScene
from app.socket import broadcast_group_progress
from datetime import datetime

bp = Blueprint('collab', __name__)


# ============ 房间管理 ============

@bp.route('/rooms', methods=['GET'])
@login_required
def list_rooms():
    """获取房间列表"""
    query = Group.query.filter_by(status='active')

    # 按场景过滤
    scene_id = request.args.get('scene_id')
    if scene_id:
        query = query.filter_by(scene_id=scene_id)

    rooms = query.order_by(Group.created_at.desc()).all()
    result = []
    for room in rooms:
        room_dict = room.to_dict()
        # 添加成员列表
        members = User.query.filter_by(group_id=room.id).all()
        room_dict['members'] = [{
            'id': m.id,
            'username': m.username,
            'real_name': m.real_name,
            'role_code': m.role_code,
            'role_name': m.role_name
        } for m in members]
        room_dict['member_count'] = len(members)
        # 添加场景信息
        if room.scene_id:
            scene = TeachingScene.query.get(room.scene_id)
            room_dict['scene'] = scene.to_dict() if scene else None
        result.append(room_dict)

    return jsonify({'code': 200, 'message': 'success', 'data': result})


@bp.route('/rooms', methods=['POST'])
@login_required
def create_room():
    """创建协作房间"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空', 'data': None})

    group_name = data.get('group_name')
    scene_id = data.get('scene_id')

    if not group_name:
        return jsonify({'code': 400, 'message': '房间名称不能为空', 'data': None})

    # 检查场景是否存在
    if scene_id:
        scene = TeachingScene.query.get(scene_id)
        if not scene:
            return jsonify({'code': 404, 'message': '教学场景不存在', 'data': None})

    # 创建房间
    room = Group(
        group_name=group_name,
        scene_id=scene_id,
        status='active'
    )
    db.session.add(room)
    db.session.flush()  # 获取 room.id

    # 创建者自动加入房间
    current_user.group_id = room.id
    db.session.commit()

    result = room.to_dict()
    result['members'] = [{
        'id': current_user.id,
        'username': current_user.username,
        'real_name': current_user.real_name,
        'role_code': current_user.role_code,
        'role_name': current_user.role_name
    }]
    result['member_count'] = 1

    return jsonify({'code': 200, 'message': '房间创建成功', 'data': result})


@bp.route('/rooms/<int:room_id>/join', methods=['POST'])
@login_required
def join_room(room_id):
    """加入协作房间"""
    room = Group.query.get(room_id)
    if not room:
        return jsonify({'code': 404, 'message': '房间不存在', 'data': None})

    if room.status != 'active':
        return jsonify({'code': 400, 'message': '房间已关闭', 'data': None})

    if current_user.group_id:
        return jsonify({'code': 400, 'message': '您已在其他房间中，请先退出当前房间', 'data': None})

    # 检查房间人数
    current_members = User.query.filter_by(group_id=room_id).count()
    if current_members >= 6:
        return jsonify({'code': 400, 'message': '房间已满（最多6人）', 'data': None})

    data = request.get_json() or {}
    role_id = data.get('role_id')

    # 分配角色
    if role_id:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'code': 404, 'message': '角色不存在', 'data': None})
        current_user.role_id = role_id

    current_user.group_id = room_id
    db.session.commit()

    # 广播成员变化
    members = User.query.filter_by(group_id=room_id).all()
    broadcast_group_progress(room_id, {
        'event': 'member_joined',
        'member_count': len(members),
        'member': {
            'id': current_user.id,
            'real_name': current_user.real_name,
            'role_code': current_user.role_code
        }
    })

    result = room.to_dict()
    result['members'] = [{
        'id': m.id,
        'username': m.username,
        'real_name': m.real_name,
        'role_code': m.role_code,
        'role_name': m.role_name
    } for m in members]
    result['member_count'] = len(members)

    return jsonify({'code': 200, 'message': '加入成功', 'data': result})


@bp.route('/rooms/<int:room_id>/leave', methods=['POST'])
@login_required
def leave_room(room_id):
    """离开协作房间"""
    room = Group.query.get(room_id)
    if not room:
        return jsonify({'code': 404, 'message': '房间不存在', 'data': None})

    if current_user.group_id != room_id:
        return jsonify({'code': 400, 'message': '您不在此房间中', 'data': None})

    current_user.group_id = None
    db.session.commit()

    # 广播成员变化
    members = User.query.filter_by(group_id=room_id).all()
    broadcast_group_progress(room_id, {
        'event': 'member_left',
        'member_count': len(members)
    })

    return jsonify({'code': 200, 'message': '已离开房间', 'data': None})


@bp.route('/rooms/<int:room_id>/close', methods=['POST'])
@login_required
def close_room(room_id):
    """关闭协作房间（教师操作）"""
    if current_user.role_code not in ('admin', 'teacher'):
        return jsonify({'code': 403, 'message': '只有教师和管理员可以关闭房间', 'data': None})

    room = Group.query.get(room_id)
    if not room:
        return jsonify({'code': 404, 'message': '房间不存在', 'data': None})

    room.status = 'completed'
    db.session.commit()

    return jsonify({'code': 200, 'message': '房间已关闭', 'data': room.to_dict()})


@bp.route('/rooms/<int:room_id>', methods=['GET'])
@login_required
def get_room(room_id):
    """获取房间详情"""
    room = Group.query.get(room_id)
    if not room:
        return jsonify({'code': 404, 'message': '房间不存在', 'data': None})

    result = room.to_dict()
    members = User.query.filter_by(group_id=room_id).all()
    result['members'] = [{
        'id': m.id,
        'username': m.username,
        'real_name': m.real_name,
        'role_code': m.role_code,
        'role_name': m.role_name
    } for m in members]
    result['member_count'] = len(members)

    # 添加场景信息
    if room.scene_id:
        scene = TeachingScene.query.get(room.scene_id)
        result['scene'] = scene.to_dict() if scene else None

    return jsonify({'code': 200, 'message': 'success', 'data': result})


@bp.route('/rooms/<int:room_id>/progress', methods=['GET'])
@login_required
def get_room_progress(room_id):
    """获取房间进度（各模块操作统计）"""
    from sqlalchemy import func

    # 统计各模块的操作数
    logs = OperationLog.query.filter_by(group_id=room_id).all()

    module_stats = {}
    for log in logs:
        if log.module not in module_stats:
            module_stats[log.module] = {'total': 0, 'correct': 0}
        module_stats[log.module]['total'] += 1
        if log.is_correct:
            module_stats[log.module]['correct'] += 1

    # 获取成员操作数
    member_stats = {}
    member_logs = db.session.query(
        OperationLog.user_id, func.count(OperationLog.id)
    ).filter_by(group_id=room_id).group_by(OperationLog.user_id).all()

    for user_id, count in member_logs:
        user = User.query.get(user_id)
        member_stats[user_id] = {
            'user_id': user_id,
            'real_name': user.real_name if user else '未知',
            'operation_count': count
        }

    # 获取最新操作
    recent_logs = OperationLog.query.filter_by(group_id=room_id).order_by(
        OperationLog.created_at.desc()
    ).limit(10).all()

    return jsonify({'code': 200, 'message': 'success', 'data': {
        'module_stats': module_stats,
        'member_stats': list(member_stats.values()),
        'recent_operations': [l.to_dict() for l in recent_logs],
        'total_operations': len(logs)
    }})
