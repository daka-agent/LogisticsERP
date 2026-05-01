from app import db
from .base import BaseModel


class Role(BaseModel):
    """角色表"""
    __tablename__ = 'roles'

    code = db.Column(db.String(32), unique=True, nullable=False)  # admin/teacher/student/purchaser/cs/dispatcher/warehouse/driver
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))

    # 关系
    users = db.relationship('User', backref='role', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
