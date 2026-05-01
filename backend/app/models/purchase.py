from app import db
from .base import BaseModel


class PurchaseRequest(BaseModel):
    """采购申请表"""
    __tablename__ = 'purchase_requests'

    req_no = db.Column(db.String(32), unique=True, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    est_unit_price = db.Column(db.Numeric(10, 2))
    est_total_price = db.Column(db.Numeric(12, 2))
    reason = db.Column(db.String(512))
    urgency = db.Column(db.String(16), default='normal')  # normal/urgent/critical
    status = db.Column(db.String(16), default='pending')  # pending/approved/rejected/cancelled
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_comment = db.Column(db.String(512))
    reviewed_at = db.Column(db.DateTime)

    # 关系
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='purchase_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_requests')
    goods = db.relationship('Goods', backref='purchase_requests')
    order = db.relationship('PurchaseOrder', backref='request', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'req_no': self.req_no,
            'applicant_id': self.applicant_id,
            'applicant_name': self.applicant.real_name if self.applicant else None,
            'goods_id': self.goods_id,
            'goods_name': self.goods.name if self.goods else None,
            'goods_sku': self.goods.sku if self.goods else None,
            'quantity': self.quantity,
            'est_unit_price': float(self.est_unit_price) if self.est_unit_price else None,
            'est_total_price': float(self.est_total_price) if self.est_total_price else None,
            'reason': self.reason,
            'urgency': self.urgency,
            'status': self.status,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.real_name if self.reviewer else None,
            'review_comment': self.review_comment,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'has_order': self.order is not None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PurchaseOrder(BaseModel):
    """采购订单表"""
    __tablename__ = 'purchase_orders'

    po_no = db.Column(db.String(32), unique=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    expected_date = db.Column(db.Date)
    status = db.Column(db.String(16), default='pending')  # pending/confirmed/shipped/partial_received/completed/cancelled
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    supplier = db.relationship('Supplier', backref='purchase_orders')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='purchase_orders')
    items = db.relationship('PurchaseOrderItem', backref='order', lazy='dynamic')
    receipts = db.relationship('PurchaseReceipt', backref='purchase_order', lazy='dynamic')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'po_no': self.po_no,
            'request_id': self.request_id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'status': self.status,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items.all()]
        return data


class PurchaseOrderItem(BaseModel):
    """采购订单明细表"""
    __tablename__ = 'purchase_order_items'

    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    ordered_qty = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    received_qty = db.Column(db.Integer, default=0)

    # 关系
    goods = db.relationship('Goods', backref='order_items')

    def to_dict(self):
        return {
            'id': self.id,
            'po_id': self.po_id,
            'goods_id': self.goods_id,
            'goods_name': self.goods.name if self.goods else None,
            'goods_sku': self.goods.sku if self.goods else None,
            'ordered_qty': self.ordered_qty,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal),
            'received_qty': self.received_qty
        }


class PurchaseReceipt(BaseModel):
    """采购收货/验收表"""
    __tablename__ = 'purchase_receipts'

    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    inbound_order_id = db.Column(db.Integer, db.ForeignKey('inbound_orders.id'))
    received_qty = db.Column(db.Integer, nullable=False)
    quality_status = db.Column(db.String(16), default='qualified')  # qualified/unqualified/partial
    quality_note = db.Column(db.String(512))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    received_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 关系
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='receipts')

    def to_dict(self):
        return {
            'id': self.id,
            'po_id': self.po_id,
            'inbound_order_id': self.inbound_order_id,
            'received_qty': self.received_qty,
            'quality_status': self.quality_status,
            'quality_note': self.quality_note,
            'receiver_id': self.receiver_id,
            'receiver_name': self.receiver.real_name if self.receiver else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
