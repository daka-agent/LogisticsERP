"""Flask 应用工厂函数"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from app.config import Config

# 初始化扩展（不绑定具体app）
db = SQLAlchemy()
login_manager = LoginManager()

# 导入 SocketIO 实例（在 extensions.py 中创建）
from app.extensions import socketio


def create_app(config_class=Config):
    """Flask 应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

    # 初始化 SocketIO（必须在 app 创建后）
    socketio.init_app(app, cors_allowed_origins='*')

    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.api.purchase import bp as purchase_bp
    app.register_blueprint(purchase_bp, url_prefix='/api')

    from app.api.transport import bp as transport_bp
    app.register_blueprint(transport_bp, url_prefix='/api')

    from app.api.warehouse import bp as warehouse_bp
    app.register_blueprint(warehouse_bp, url_prefix='/api')

    from app.api.inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/api')

    from app.api.collab import bp as collab_bp
    app.register_blueprint(collab_bp, url_prefix='/api')

    from app.api.teaching import bp as teaching_bp
    app.register_blueprint(teaching_bp, url_prefix='/api')

    from app.api.logs import bp as logs_bp
    app.register_blueprint(logs_bp, url_prefix='/api')

    from app.api.scores import bp as scores_bp
    app.register_blueprint(scores_bp, url_prefix='/api')

    from app.api.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/api')

    from app.api.export import bp as export_bp
    app.register_blueprint(export_bp, url_prefix='/api')

    from app.api.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api')

    from app.api.finance import bp as finance_bp
    app.register_blueprint(finance_bp, url_prefix='/api')

    from app.api.contracts import bp as contracts_bp
    app.register_blueprint(contracts_bp)

    # 启动时自动初始化预设教学场景（若不存在）
    try:
        from app.api.teaching import init_preset_scenes
        with app.app_context():
            init_preset_scenes()
    except Exception:
        pass  # 表尚未创建时静默跳过

    # 注册 socket 事件处理
    from app.socket import init_socket
    init_socket(socketio)

    # 健康检查接口
    @app.route('/api/health')
    def health():
        return {'code': 200, 'message': 'ok', 'data': {'version': '2.0.0'}}

    return app


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login 加载用户回调"""
    from app.models.user import User
    return User.query.get(int(user_id))
