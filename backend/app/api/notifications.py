"""通知 API - 站内消息 CRUD"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification
from app.utils.notification_helper import send_notification

bp = Blueprint('notifications', __name__)


@bp.route('/notifications', methods=['GET'])
@login_required
def list_notifications():
    """获取当前用户的通知列表（分页 + 筛选）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    notif_type = request.args.get('type', '', type=str)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'

    query = Notification.query.filter_by(user_id=current_user.id)

    if notif_type:
        query = query.filter_by(type=notif_type)
    if unread_only:
        query = query.filter_by(is_read=False)

    query = query.order_by(Notification.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'message': 'ok',
        'data': {
            'items': [n.to_dict() for n in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'unread_count': Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        }
    })


@bp.route('/notifications/unread-count', methods=['GET'])
@login_required
def unread_count():
    """获取当前用户未读通知数量"""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({
        'code': 200,
        'message': 'ok',
        'data': {'count': count}
    })


@bp.route('/notifications/<int:nid>/read', methods=['PUT'])
@login_required
def mark_read(nid):
    """标记通知为已读"""
    notification = Notification.query.filter_by(id=nid, user_id=current_user.id).first()
    if not notification:
        return jsonify({'code': 404, 'message': '通知不存在'}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({'code': 200, 'message': 'ok', 'data': notification.to_dict()})


@bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    """将当前用户所有通知标记为已读"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()

    return jsonify({'code': 200, 'message': 'ok', 'data': None})


@bp.route('/notifications/<int:nid>', methods=['DELETE'])
@login_required
def delete_notification(nid):
    """删除通知"""
    notification = Notification.query.filter_by(id=nid, user_id=current_user.id).first()
    if not notification:
        return jsonify({'code': 404, 'message': '通知不存在'}), 404

    db.session.delete(notification)
    db.session.commit()

    return jsonify({'code': 200, 'message': 'ok', 'data': None})
