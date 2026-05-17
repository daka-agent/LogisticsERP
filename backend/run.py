#!/usr/bin/env python3
"""后端服务启动文件（SocketIO模式）"""
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print("="*55)
    print("  大卡@物流系统模拟仿真 — 后端服务")
    print("="*55)
    print(f"  调试模式  : {app.config.get('DEBUG', False)}")
    print(f"  访问地址  : http://localhost:5000")
    print(f"  前端地址  : http://localhost:5173")
    print("="*55)
    print("  提示：首次启动将自动初始化账号和基础数据，无需手动配置")
    print("="*55)
    
    # 使用 SocketIO 启动（支持 WebSocket）
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True  # 开发环境允许自动重载
    )
