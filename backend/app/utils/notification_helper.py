"""通知辅助函数 - 创建通知 + WebSocket 实时推送"""
from app import db
from app.models.notification import Notification


def send_notification(user_id, type, title, content,
                      reference_type=None, reference_id=None, sender_id=None):
    """
    创建持久化通知并通过 WebSocket 实时推送。

    参数:
        user_id:       接收人用户ID
        type:          通知类型 (approval/todo/system/alert/event/message)
        title:         通知标题
        content:       通知内容
        reference_type: 关联类型（可选）
        reference_id:   关联ID（可选）
        sender_id:     发送人ID（可选，系统通知为None）

    返回:
        Notification 实例
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        content=content,
        reference_type=reference_type or '',
        reference_id=reference_id,
        sender_id=sender_id,
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()

    # WebSocket 实时推送
    _push_notification(notification)

    return notification


def _push_notification(notification):
    """通过 WebSocket 推送新通知到用户房间"""
    try:
        from app.socket import _safe_emit
        _safe_emit('new_notification', {
            'id': notification.id,
            'type': notification.type,
            'title': notification.title,
            'content': notification.content,
            'reference_type': notification.reference_type,
            'reference_id': notification.reference_id,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat() if notification.created_at else None
        }, room=f'user_{notification.user_id}')
    except Exception:
        pass  # WebSocket 不可用时静默降级


def notify_role_users(role_code, type, title, content,
                      reference_type=None, reference_id=None, sender_id=None):
    """
    给指定角色的所有用户发送通知。

    参数:
        role_code:      角色代码 (如 'admin', 'teacher', 'purchaser')
        type:           通知类型
        title:          通知标题
        content:        通知内容
        reference_type: 关联类型（可选）
        reference_id:   关联ID（可选）
        sender_id:      发送人ID（可选）
    """
    from app.models.user import User
    from app.models.role import Role

    role = Role.query.filter_by(code=role_code).first()
    if not role:
        return

    users = User.query.filter_by(role_id=role.id, status='active').all()
    count = 0
    for user in users:
        send_notification(user.id, type, title, content,
                          reference_type=reference_type,
                          reference_id=reference_id,
                          sender_id=sender_id)
        count += 1
    return count
