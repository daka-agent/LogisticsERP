from app import db
from .base import BaseModel


class Supplier(BaseModel):
    """供应商表"""
    __tablename__ = 'suppliers'

    name = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(256))
    rating = db.Column(db.Numeric(2, 1), default=0.0)  # 1.0-5.0
    status = db.Column(db.String(16), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'phone': self.phone,
            'address': self.address,
            'rating': float(self.rating) if self.rating else 0.0,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
