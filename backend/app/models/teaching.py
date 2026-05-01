from app import db
from .base import BaseModel


class TeachingScene(BaseModel):
    """教学场景表"""
    __tablename__ = 'teaching_scenes'

    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(512))
    difficulty = db.Column(db.String(16), default='normal')  # easy/normal/hard
    initial_data = db.Column(db.JSON)  # 初始数据配置
    events_config = db.Column(db.JSON)  # 突发事件配置
    scoring_rules = db.Column(db.JSON)  # 评分规则配置

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'difficulty': self.difficulty,
            'initial_data': self.initial_data,
            'events_config': self.events_config,
            'scoring_rules': self.scoring_rules,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
