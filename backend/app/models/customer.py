from app import db
from .base import BaseModel


class Customer(BaseModel):
    """客户表"""
    __tablename__ = 'customers'

    name = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(256))
    credit_level = db.Column(db.String(16), default='normal')  # normal/good/vip
    status = db.Column(db.String(16), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'phone': self.phone,
            'address': self.address,
            'credit_level': self.credit_level,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
