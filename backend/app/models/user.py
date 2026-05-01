import bcrypt
from flask_login import UserMixin
from app import db
from .base import BaseModel


class User(BaseModel, UserMixin):
    """用户表"""
    __tablename__ = 'users'

    username = db.Column(db.String(64), unique=True, nullable=False)
    _password_hash = db.Column('password_hash', db.String(256), nullable=False)
    real_name = db.Column(db.String(64), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    email = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(16), default='active')  # active/inactive

    # 关系
    group = db.relationship('Group', backref='members', lazy='select')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, plaintext):
        """设置密码（自动哈希）"""
        self._password_hash = bcrypt.hashpw(
            plaintext.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def verify_password(self, plaintext):
        """验证密码"""
        return bcrypt.checkpw(
            plaintext.encode('utf-8'),
            self._password_hash.encode('utf-8')
        )

    @property
    def role_code(self):
        return self.role.code if self.role else None

    @property
    def role_name(self):
        return self.role.name if self.role else None

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'role_id': self.role_id,
            'role_code': self.role_code,
            'role_name': self.role_name,
            'group_id': self.group_id,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        # 不返回密码哈希
        return data
