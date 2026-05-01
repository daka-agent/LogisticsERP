from app import db
from .base import BaseModel


class Vehicle(BaseModel):
    """车辆表"""
    __tablename__ = 'vehicles'

    plate_no = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(32), nullable=False)  # 小型/中型/大型/冷藏
    capacity_weight = db.Column(db.Numeric(8, 2))  # 载重（吨）
    capacity_volume = db.Column(db.Numeric(8, 2))  # 容积（立方米）
    status = db.Column(db.String(16), default='idle')  # idle/in_transport/maintenance
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'plate_no': self.plate_no,
            'type': self.type,
            'capacity_weight': float(self.capacity_weight) if self.capacity_weight else None,
            'capacity_volume': float(self.capacity_volume) if self.capacity_volume else None,
            'status': self.status,
            'driver_id': self.driver_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
