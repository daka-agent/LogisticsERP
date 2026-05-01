#!/usr/bin/env python3
"""Flask 应用启动文件（支持 SocketIO）"""
from app import create_app, db
from app.extensions import socketio
from app.models import User, Role, OperationLog, Score  # 确保模型被加载

app = create_app()


def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        print("数据库表已创建")


if __name__ == '__main__':
    init_db()  # 启动前先创建表
    print("启动 SocketIO 服务器...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
