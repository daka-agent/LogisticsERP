from app import db
from .base import BaseModel


class InboundOrder(BaseModel):
    """入库单表"""
    __tablename__ = 'inbound_orders'

    order_no = db.Column(db.String(32), unique=True, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    source_type = db.Column(db.String(32), nullable=False)  # purchase/return/transfer
    source_id = db.Column(db.Integer)  # 来源单据ID
    status = db.Column(db.String(16), default='pending')
    # pending/inspecting/shelving/completed/cancelled
    total_items = db.Column(db.Integer, default=0)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    inspected_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    remark = db.Column(db.String(512))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    # 关系
    warehouse = db.relationship('Warehouse', backref='inbound_orders')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='inbound_orders')
    items = db.relationship('InboundItem', backref='inbound_order', lazy='dynamic')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'order_no': self.order_no,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'status': self.status,
            'total_items': self.total_items,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'inspected_at': self.inspected_at.isoformat() if self.inspected_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'remark': self.remark,
            'group_id': self.group_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items.all()]
        return data


class InboundItem(BaseModel):
    """入库明细表"""
    __tablename__ = 'inbound_items'

    inbound_id = db.Column(db.Integer, db.ForeignKey('inbound_orders.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    planned_qty = db.Column(db.Integer, nullable=False)
    actual_qty = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    batch_no = db.Column(db.String(64))
    production_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(16), default='pending')  # pending/shelved/completed

    # 关系
    goods = db.relationship('Goods', backref='inbound_items')
    location = db.relationship('Location', backref='inbound_items')

    def to_dict(self):
        return {
            'id': self.id,
            'inbound_id': self.inbound_id,
            'goods_id': self.goods_id,
            'goods_name': self.goods.name if self.goods else None,
            'goods_sku': self.goods.sku if self.goods else None,
            'planned_qty': self.planned_qty,
            'actual_qty': self.actual_qty,
            'location_id': self.location_id,
            'loc_code': self.location.loc_code if self.location else None,
            'batch_no': self.batch_no,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
