"""协作管理相关模型：操作日志、评分"""
from app import db
from .base import BaseModel


class OperationLog(BaseModel):
    """操作日志表"""
    __tablename__ = 'operation_logs'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    module = db.Column(db.String(32), nullable=False)  # purchase_request/purchase_order/transport_order/inbound/outbound/stock_count
    action = db.Column(db.String(32), nullable=False)   # create/approve/reject/confirm/cancel/...
    target_type = db.Column(db.String(32))              # 操作对象类型
    target_id = db.Column(db.Integer)                    # 操作对象ID
    description = db.Column(db.String(512))              # 操作描述
    request_data = db.Column(db.JSON)                    # 请求数据（快照）
    response_data = db.Column(db.JSON)                   # 响应数据（快照）
    ip_address = db.Column(db.String(64))                # 客户端IP
    duration_ms = db.Column(db.Integer)                  # 操作耗时（毫秒）
    is_correct = db.Column(db.Boolean, default=True)     # 操作是否正确

    # 关系
    user = db.relationship('User', backref='operation_logs', lazy='select')
    group = db.relationship('Group', backref='operation_logs', lazy='select')

    def to_dict(self):
        result = super().to_dict()
        if self.user:
            result['user_name'] = self.user.real_name
            result['username'] = self.user.username
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            result['updated_at'] = self.updated_at.isoformat()
        return result


class Score(BaseModel):
    """评分记录表"""
    __tablename__ = 'scores'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    module = db.Column(db.String(32), nullable=False)    # 模块名
    action = db.Column(db.String(32), nullable=False)    # 操作名
    points = db.Column(db.Float, default=0)              # 得分（正数加分，负数扣分）
    is_correct = db.Column(db.Boolean, default=True)     # 操作是否正确
    extra_data = db.Column(db.JSON)                      # 额外数据

    # 关系
    user = db.relationship('User', backref='scores', lazy='select')
    group = db.relationship('Group', backref='scores', lazy='select')

    def to_dict(self):
        result = super().to_dict()
        if self.user:
            result['user_name'] = self.user.real_name
            result['username'] = self.user.username
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        return result
