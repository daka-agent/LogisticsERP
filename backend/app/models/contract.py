"""
合同管理数据模型

包含采购合同(PurchaseContract)和运输合同(TransportContract)两个模型。
合同从已审批通过的采购订单/运输订单生成，含审批流。
"""
from datetime import date, datetime
from app import db
from app.models.base import BaseModel


class PurchaseContract(BaseModel):
    """采购合同模型

    从已审批通过的采购订单生成，需经过审批流程后生效。
    合同生效后指导后续的到货验收和财务结算。
    """
    __tablename__ = 'purchase_contracts'

    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(50), unique=True, nullable=False, comment='合同编号 PC-YYYYMMDDNNN')
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False, comment='关联采购订单ID')
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, comment='关联供应商ID')
    sign_date = db.Column(db.Date, comment='签订日期')
    start_date = db.Column(db.Date, comment='生效日期')
    end_date = db.Column(db.Date, comment='终止日期')
    total_amount = db.Column(db.Float, default=0.0, comment='合同总金额')
    payment_terms = db.Column(db.String(200), comment='付款条款')
    delivery_terms = db.Column(db.String(200), comment='交货条款')
    status = db.Column(db.String(20), default='draft', nullable=False, comment='状态')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='审批人ID')
    review_comment = db.Column(db.Text, comment='审批意见')
    reviewed_at = db.Column(db.DateTime, comment='审批时间')
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='操作人ID')

    # 状态常量
    STATUS_DRAFT = 'draft'          # 草稿（刚从订单生成）
    STATUS_PENDING = 'pending'       # 待审批
    STATUS_APPROVED = 'approved'     # 审批通过（未生效）
    STATUS_REJECTED = 'rejected'     # 审批驳回
    STATUS_ACTIVE = 'active'         # 生效（已签订）
    STATUS_COMPLETED = 'completed'   # 已完成
    STATUS_TERMINATED = 'terminated' # 已终止

    # 关联关系
    purchase_order = db.relationship('PurchaseOrder', backref='contract', lazy=True, uselist=False)
    supplier = db.relationship('Supplier', backref='purchase_contracts', lazy=True)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_purchase_contracts', lazy=True)
    operator = db.relationship('User', foreign_keys=[operator_id], backref='operated_purchase_contracts', lazy=True)

    def to_dict(self):
        data = super().to_dict()
        data['po_no'] = self.purchase_order.po_no if self.purchase_order else None
        data['supplier_name'] = self.supplier.name if self.supplier else None
        data['reviewer_name'] = self.reviewer.real_name if self.reviewer else None
        data['review_comment'] = self.review_comment
        data['operator_name'] = self.operator.real_name if self.operator else None
        # 格式化日期字段
        for key in ['sign_date', 'start_date', 'end_date']:
            if data.get(key):
                data[key] = data[key].isoformat() if hasattr(data[key], 'isoformat') else data[key]
        return data


class TransportContract(BaseModel):
    """运输合同模型

    从已审批通过的运输订单生成，需经过审批流程后生效。
    合同生效后指导后续的调度、运输和签收操作。
    """
    __tablename__ = 'transport_contracts'

    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(50), unique=True, nullable=False, comment='合同编号 TC-YYYYMMDDNNN')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, comment='关联运输订单ID')
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, comment='关联客户ID')
    sign_date = db.Column(db.Date, comment='签订日期')
    start_date = db.Column(db.Date, comment='生效日期')
    end_date = db.Column(db.Date, comment='终止日期')
    freight_amount = db.Column(db.Float, default=0.0, comment='运费金额')
    payment_terms = db.Column(db.String(200), comment='付款条款')
    transport_terms = db.Column(db.String(200), comment='运输条款')
    status = db.Column(db.String(20), default='draft', nullable=False, comment='状态')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='审批人ID')
    review_comment = db.Column(db.Text, comment='审批意见')
    reviewed_at = db.Column(db.DateTime, comment='审批时间')
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='操作人ID')

    # 状态常量（同 PurchaseContract）
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_TERMINATED = 'terminated'

    # 关联关系
    transport_order = db.relationship('Order', backref='contract', lazy=True, uselist=False)
    customer = db.relationship('Customer', backref='transport_contracts', lazy=True)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_transport_contracts', lazy=True)
    operator = db.relationship('User', foreign_keys=[operator_id], backref='operated_transport_contracts', lazy=True)

    def to_dict(self):
        data = super().to_dict()
        data['order_no'] = self.transport_order.order_no if self.transport_order else None
        data['customer_name'] = self.customer.name if self.customer else None
        data['reviewer_name'] = self.reviewer.real_name if self.reviewer else None
        data['review_comment'] = self.review_comment
        data['operator_name'] = self.operator.real_name if self.operator else None
        # 格式化日期字段
        for key in ['sign_date', 'start_date', 'end_date']:
            if data.get(key):
                data[key] = data[key].isoformat() if hasattr(data[key], 'isoformat') else data[key]
        return data
