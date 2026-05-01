from app import db
from .base import BaseModel


class Group(BaseModel):
    """分组表（多人协作模式）"""
    __tablename__ = 'groups'

    group_name = db.Column(db.String(64), nullable=False)
    scene_id = db.Column(db.Integer, db.ForeignKey('teaching_scenes.id'))
    status = db.Column(db.String(16), default='active')  # active/completed

    def to_dict(self):
        return {
            'id': self.id,
            'group_name': self.group_name,
            'scene_id': self.scene_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
