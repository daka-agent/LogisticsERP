"""财务结算相关模型：应付账款、应收账款"""
from app import db
from .base import BaseModel


class AccountsPayable(BaseModel):
    """应付账款表 - 基于采购订单生成"""
    __tablename__ = 'accounts_payable'

    payable_no = db.Column(db.String(32), unique=True, nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(12, 2), default=0)
    remaining_amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(16), default='pending')
    # pending/partial_paid/paid/cancelled
    due_date = db.Column(db.Date)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    purchase_order = db.relationship('PurchaseOrder', backref='accounts_payable')
    supplier = db.relationship('Supplier', backref='accounts_payable')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='payables')
    payments = db.relationship('PayablePayment', backref='accounts_payable', lazy='dynamic')

    def to_dict(self, include_payments=False):
        data = {
            'id': self.id,
            'payable_no': self.payable_no,
            'po_id': self.po_id,
            'po_no': self.purchase_order.po_no if self.purchase_order else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'remaining_amount': float(self.remaining_amount) if self.remaining_amount else 0,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'group_id': self.group_id,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_payments:
            data['payments'] = [p.to_dict() for p in self.payments.all()]
        return data


class PayablePayment(BaseModel):
    """应付账款付款记录表"""
    __tablename__ = 'payable_payments'

    payable_id = db.Column(db.Integer, db.ForeignKey('accounts_payable.id'), nullable=False)
    payment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(16), default='bank_transfer')
    # cash/bank_transfer/check/other
    payment_date = db.Column(db.Date, nullable=False)
    remark = db.Column(db.String(512))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 关系
    operator = db.relationship('User', foreign_keys=[operator_id], backref='payable_payments')

    def to_dict(self):
        return {
            'id': self.id,
            'payable_id': self.payable_id,
            'payment_amount': float(self.payment_amount) if self.payment_amount else 0,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'remark': self.remark,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AccountsReceivable(BaseModel):
    """应收账款表 - 基于运输订单生成"""
    __tablename__ = 'accounts_receivable'

    receivable_no = db.Column(db.String(32), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    received_amount = db.Column(db.Numeric(12, 2), default=0)
    remaining_amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(16), default='pending')
    # pending/partial_received/received/cancelled
    due_date = db.Column(db.Date)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    transport_order = db.relationship('Order', backref='accounts_receivable')
    customer = db.relationship('Customer', backref='accounts_receivable')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='receivables')
    payments = db.relationship('ReceivablePayment', backref='accounts_receivable', lazy='dynamic')

    def to_dict(self, include_payments=False):
        data = {
            'id': self.id,
            'receivable_no': self.receivable_no,
            'order_id': self.order_id,
            'order_no': self.transport_order.order_no if self.transport_order else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'received_amount': float(self.received_amount) if self.received_amount else 0,
            'remaining_amount': float(self.remaining_amount) if self.remaining_amount else 0,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'group_id': self.group_id,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_payments:
            data['payments'] = [p.to_dict() for p in self.payments.all()]
        return data


class ReceivablePayment(BaseModel):
    """应收账款收款记录表"""
    __tablename__ = 'receivable_payments'

    receivable_id = db.Column(db.Integer, db.ForeignKey('accounts_receivable.id'), nullable=False)
    payment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(16), default='bank_transfer')
    # cash/bank_transfer/check/other
    payment_date = db.Column(db.Date, nullable=False)
    remark = db.Column(db.String(512))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 关系
    operator = db.relationship('User', foreign_keys=[operator_id], backref='receivable_payments')

    def to_dict(self):
        return {
            'id': self.id,
            'receivable_id': self.receivable_id,
            'payment_amount': float(self.payment_amount) if self.payment_amount else 0,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'remark': self.remark,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
