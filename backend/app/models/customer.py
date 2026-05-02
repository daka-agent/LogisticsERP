from app import db
from .base import BaseModel


class Customer(BaseModel):
    """客户表"""
    __tablename__ = 'customers'

    customer_no = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    level = db.Column(db.String(16), default='normal')  # vip/normal/potential
    contact_person = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(128))
    address = db.Column(db.String(256))
    settlement_type = db.Column(db.String(16))  # monthly/spot/credit
    credit_limit = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(16), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_no': self.customer_no,
            'name': self.name,
            'level': self.level,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'settlement_type': self.settlement_type,
            'credit_limit': self.credit_limit,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
