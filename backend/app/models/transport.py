from app import db
from .base import BaseModel


class Order(BaseModel):
    """运输订单表"""
    __tablename__ = 'orders'

    order_no = db.Column(db.String(32), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    origin = db.Column(db.String(256), nullable=False)
    destination = db.Column(db.String(256), nullable=False)
    goods_name = db.Column(db.String(128))
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    weight = db.Column(db.Numeric(8, 2))       # 千克
    volume = db.Column(db.Numeric(8, 2))       # 立方米
    quantity = db.Column(db.Integer)            # 件数
    status = db.Column(db.String(16), default='pending')
    # pending/approved/dispatched/in_transit/arrived/signed/completed/cancelled
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    freight_amount = db.Column(db.Numeric(10, 2))
    plan_departure = db.Column(db.DateTime)
    plan_arrival = db.Column(db.DateTime)
    actual_departure = db.Column(db.DateTime)
    actual_arrival = db.Column(db.DateTime)
    signee_name = db.Column(db.String(64))
    signee_phone = db.Column(db.String(20))
    remark = db.Column(db.String(512))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    customer = db.relationship('Customer', backref='orders')
    goods = db.relationship('Goods', backref='orders')
    vehicle = db.relationship('Vehicle', backref='orders')
    driver = db.relationship('Driver', backref='orders')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='orders')
    transport_records = db.relationship('TransportRecord', backref='order', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'origin': self.origin,
            'destination': self.destination,
            'goods_name': self.goods_name,
            'goods_id': self.goods_id,
            'weight': float(self.weight) if self.weight else None,
            'volume': float(self.volume) if self.volume else None,
            'quantity': self.quantity,
            'status': self.status,
            'vehicle_id': self.vehicle_id,
            'vehicle_plate': self.vehicle.plate_no if self.vehicle else None,
            'driver_id': self.driver_id,
            'driver_name': self.driver.name if self.driver else None,
            'freight_amount': float(self.freight_amount) if self.freight_amount else None,
            'plan_departure': self.plan_departure.isoformat() if self.plan_departure else None,
            'plan_arrival': self.plan_arrival.isoformat() if self.plan_arrival else None,
            'actual_departure': self.actual_departure.isoformat() if self.actual_departure else None,
            'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
            'signee_name': self.signee_name,
            'signee_phone': self.signee_phone,
            'remark': self.remark,
            'group_id': self.group_id,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TransportRecord(BaseModel):
    """运输跟踪记录表"""
    __tablename__ = 'transport_records'

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    # departed/in_transit/rest/arrived/unloading/signed
    location = db.Column(db.String(256))
    description = db.Column(db.String(512))
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    recorded_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 关系
    recorder = db.relationship('User', foreign_keys=[recorded_by], backref='transport_records')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'status': self.status,
            'location': self.location,
            'description': self.description,
            'recorded_by': self.recorded_by,
            'recorder_name': self.recorder.real_name if self.recorder else None,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
