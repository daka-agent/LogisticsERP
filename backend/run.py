#!/usr/bin/env python3
"""后端服务启动文件（SocketIO模式）"""
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print("="*50)
    print("物流教学软件后端服务")
    print("="*50)
    print(f"调试模式: {app.config.get('DEBUG', False)}")
    print(f"数据库: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')}")
    print("="*50)
    
    # 使用 SocketIO 启动（支持 WebSocket）
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True  # 开发环境允许自动重载
    )
