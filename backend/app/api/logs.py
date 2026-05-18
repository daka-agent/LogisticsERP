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


@bp.route('/operation-logs/replay', methods=['GET'])
@login_required
def replay_logs():
    """学生操作回放：返回某学生的完整操作时间线和统计"""
    from sqlalchemy import func, distinct

    user_id = request.args.get('user_id', type=int)
    group_id = request.args.get('group_id', type=int)

    if not user_id:
        return jsonify({'code': 400, 'message': '请指定学生ID (user_id)'}), 400

    # 基础查询
    query = OperationLog.query.filter_by(user_id=user_id)
    if group_id:
        query = query.filter_by(group_id=group_id)

    all_logs = query.order_by(OperationLog.created_at.asc()).all()

    if not all_logs:
        return jsonify({'code': 200, 'message': 'success', 'data': {
            'user_id': user_id,
            'total': 0,
            'correct_count': 0,
            'error_count': 0,
            'accuracy_rate': 0,
            'module_coverage': [],
            'module_stats': [],
            'timeline': []
        }})

    # 统计
    total = len(all_logs)
    correct_count = sum(1 for l in all_logs if l.is_correct)
    error_count = total - correct_count
    accuracy_rate = round(correct_count / total * 100, 1) if total > 0 else 0

    # 模块覆盖
    covered_modules = set(l.module for l in all_logs)
    all_known_modules = [
        'purchase_request', 'purchase_order', 'transport_order',
        'inbound_order', 'outbound_order', 'stock_count',
        'finance', 'contract', 'customer'
    ]
    module_coverage = [
        {
            'module': m,
            'label': _module_label(m),
            'covered': m in covered_modules,
            'operation_count': sum(1 for l in all_logs if l.module == m)
        }
        for m in all_known_modules
    ]

    # 模块统计
    module_stats_rows = db.session.query(
        OperationLog.module, func.count(OperationLog.id),
        func.sum(func.cast(OperationLog.is_correct, db.Integer))
    ).filter_by(user_id=user_id)
    if group_id:
        module_stats_rows = module_stats_rows.filter_by(group_id=group_id)
    module_stats_rows = module_stats_rows.group_by(OperationLog.module).all()

    module_stats = [
        {
            'module': m,
            'label': _module_label(m),
            'count': c,
            'correct': int(correct) if correct else 0
        }
        for m, c, correct in module_stats_rows
    ]

    # 时间线（按时间正序，包含详细数据）
    timeline = [l.to_dict() for l in all_logs]

    # 计算时间跨度
    first_time = all_logs[0].created_at
    last_time = all_logs[-1].created_at
    duration_minutes = round(
        (last_time - first_time).total_seconds() / 60, 1
    ) if first_time and last_time else 0

    # 耗时分析（按模块）
    from collections import defaultdict
    module_time = defaultdict(float)
    for i, log in enumerate(all_logs):
        if log.duration_ms:
            module_time[log.module] += log.duration_ms / 1000  # 转为秒

    time_analysis = [
        {'module': _module_label(m), 'total_seconds': round(t, 1)}
        for m, t in module_time.items()
    ]

    return jsonify({'code': 200, 'message': 'success', 'data': {
        'user_id': user_id,
        'user_name': all_logs[0].user.real_name if all_logs[0].user else None,
        'total': total,
        'correct_count': correct_count,
        'error_count': error_count,
        'accuracy_rate': accuracy_rate,
        'module_coverage': module_coverage,
        'module_stats': module_stats,
        'timeline': timeline,
        'time_span': {
            'first': first_time.isoformat() if first_time else None,
            'last': last_time.isoformat() if last_time else None,
            'duration_minutes': duration_minutes
        },
        'time_analysis': time_analysis
    }})


@bp.route('/operation-logs/<int:log_id>', methods=['GET'])
@login_required
def get_log_detail(log_id):
    """获取单条操作日志详情（含完整 request/response 数据）"""
    log = OperationLog.query.get_or_404(log_id)
    return jsonify({'code': 200, 'message': 'success', 'data': log.to_dict()})


def _module_label(module):
    """模块名中文映射"""
    labels = {
        'purchase_request': '采购申请',
        'purchase_order': '采购订单',
        'transport_order': '运输订单',
        'inbound_order': '入库管理',
        'outbound_order': '出库管理',
        'stock_count': '库存盘点',
        'finance': '财务管理',
        'contract': '合同管理',
        'customer': '客户管理',
        'event_injection': '事件注入',
        'transport_exception': '运输异常',
    }
    return labels.get(module, module)


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
