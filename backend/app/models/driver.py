from app import db
from .base import BaseModel


class Driver(BaseModel):
    """司机表"""
    __tablename__ = 'drivers'

    name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20))
    license_no = db.Column(db.String(32))
    license_type = db.Column(db.String(16))  # A1/A2/B1/B2
    status = db.Column(db.String(16), default='available')  # available/on_road/off_duty

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'license_no': self.license_no,
            'license_type': self.license_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
