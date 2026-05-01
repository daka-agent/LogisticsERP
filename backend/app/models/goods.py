from app import db
from .base import BaseModel


class Category(BaseModel):
    """商品分类表"""
    __tablename__ = 'categories'

    name = db.Column(db.String(64), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Goods(BaseModel):
    """商品表"""
    __tablename__ = 'goods'

    sku = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    spec = db.Column(db.String(128))
    unit = db.Column(db.String(16), nullable=False)  # 个/箱/吨/立方米
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    min_stock = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, default=99999)
    purchase_price = db.Column(db.Numeric(10, 2))
    selling_price = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(16), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'spec': self.spec,
            'unit': self.unit,
            'category_id': self.category_id,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'purchase_price': float(self.purchase_price) if self.purchase_price else None,
            'selling_price': float(self.selling_price) if self.selling_price else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
