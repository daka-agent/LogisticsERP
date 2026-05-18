"""通知模型 - 站内消息持久化存储"""
from app import db
from app.models.base import BaseModel


class Notification(BaseModel):
    """站内通知"""
    __tablename__ = 'notifications'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False, index=True,
                     comment='通知类型: approval/todo/system/alert/event/message')
    title = db.Column(db.String(200), nullable=False, comment='通知标题')
    content = db.Column(db.Text, default='', comment='通知内容')
    reference_type = db.Column(db.String(50), default='',
                                comment='关联类型: purchase_request/transport_order/contract/...')
    reference_id = db.Column(db.Integer, default=None,
                              comment='关联ID')
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True,
                          comment='发送人ID，系统通知为NULL')
    is_read = db.Column(db.Boolean, default=False, index=True, comment='是否已读')

    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    sender = db.relationship('User', foreign_keys=[sender_id])

    def to_dict(self):
        result = super().to_dict()
        result['sender_name'] = self.sender.real_name if self.sender else '系统'
        return result
