"""操作日志 API"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.collab import OperationLog

bp = Blueprint('logs', __name__)


@bp.route('/operation-logs', methods=['GET'])
@login_required
def list_logs():
    """获取操作日志列表"""
    query = OperationLog.query

    # 按用户过滤
    user_id = request.args.get('user_id')
    if user_id:
        query = query.filter_by(user_id=user_id)

    # 按小组过滤
    group_id = request.args.get('group_id')
    if group_id:
        query = query.filter_by(group_id=group_id)

    # 按模块过滤
    module = request.args.get('module')
    if module:
        query = query.filter_by(module=module)

    # 按操作类型过滤
    action = request.args.get('action')
    if action:
        query = query.filter_by(action=action)

    # 按是否正确过滤
    is_correct = request.args.get('is_correct')
    if is_correct is not None:
        query = query.filter_by(is_correct=is_correct == 'true')

    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    pagination = query.order_by(OperationLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({'code': 200, 'message': 'success', 'data': {
        'items': [l.to_dict() for l in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }})


@bp.route('/operation-logs/stats', methods=['GET'])
@login_required
def log_stats():
    """获取操作日志统计"""
    from sqlalchemy import func

    group_id = request.args.get('group_id')
    query = OperationLog.query
    if group_id:
        query = query.filter_by(group_id=group_id)

    # 按模块统计
    module_stats = db.session.query(
        OperationLog.module, func.count(OperationLog.id)
    ).group_by(OperationLog.module).all()

    # 按用户统计
    user_stats = db.session.query(
        OperationLog.user_id, func.count(OperationLog.id)
    ).group_by(OperationLog.user_id).all()

    # 正确率
    total = query.count()
    correct = query.filter_by(is_correct=True).count()
    error_rate = round((total - correct) / total * 100, 1) if total > 0 else 0

    # 时间分布（按小时）
    hour_stats = db.session.query(
        func.strftime('%H', OperationLog.created_at), func.count(OperationLog.id)
    ).group_by(func.strftime('%H', OperationLog.created_at)).all() if total > 0 else []

    return jsonify({'code': 200, 'message': 'success', 'data': {
        'total': total,
        'correct': correct,
        'error_rate': error_rate,
        'module_stats': [{'module': m, 'count': c} for m, c in module_stats],
        'user_stats': [{'user_id': u, 'count': c} for u, c in user_stats],
        'hour_stats': [{'hour': h, 'count': c} for h, c in hour_stats]
    }})


def log_operation(user_id, group_id, module, action, target_type=None, target_id=None,
                  description=None, request_data=None, response_data=None,
                  ip_address=None, duration_ms=None, is_correct=True):
    """记录操作日志的辅助函数"""
    log = OperationLog(
        user_id=user_id,
        group_id=group_id,
        module=module,
        action=action,
        target_type=target_type,
        target_id=target_id,
        description=description,
        request_data=request_data,
        response_data=response_data,
        ip_address=ip_address,
        duration_ms=duration_ms,
        is_correct=is_correct
    )
    db.session.add(log)
    return log
