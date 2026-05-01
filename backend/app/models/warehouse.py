from app import db
from .base import BaseModel


class Warehouse(BaseModel):
    """仓库表"""
    __tablename__ = 'warehouses'

    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(256))
    type = db.Column(db.String(32), default='normal')  # normal/cold/dangerous
    total_locations = db.Column(db.Integer, default=0)
    used_locations = db.Column(db.Integer, default=0)
    status = db.Column(db.String(16), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'type': self.type,
            'total_locations': self.total_locations,
            'used_locations': self.used_locations,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Zone(BaseModel):
    """库区表"""
    __tablename__ = 'zones'

    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    zone_code = db.Column(db.String(16), nullable=False)
    zone_name = db.Column(db.String(64), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'zone_code': self.zone_code,
            'zone_name': self.zone_name,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Location(BaseModel):
    """货位表"""
    __tablename__ = 'locations'

    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)
    loc_code = db.Column(db.String(32), nullable=False)
    capacity_weight = db.Column(db.Numeric(8, 2))
    capacity_volume = db.Column(db.Numeric(8, 2))
    status = db.Column(db.String(16), default='empty')  # empty/occupied/full

    def to_dict(self):
        return {
            'id': self.id,
            'zone_id': self.zone_id,
            'loc_code': self.loc_code,
            'capacity_weight': float(self.capacity_weight) if self.capacity_weight else None,
            'capacity_volume': float(self.capacity_volume) if self.capacity_volume else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
