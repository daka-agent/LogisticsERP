"""评分管理 API"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.utils.scoring import calculate_group_score, calculate_user_score, score_operation
from app.models.collab import Score, OperationLog
from app.models.user import User
from app.models.group import Group
from sqlalchemy import func

bp = Blueprint('scores', __name__)


@bp.route('/scores/group/<int:group_id>', methods=['GET'])
@login_required
def get_group_score(group_id):
    """获取小组评分"""
    result = calculate_group_score(group_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result})


@bp.route('/scores/user/<int:user_id>', methods=['GET'])
@login_required
def get_user_score(user_id):
    """获取个人评分"""
    group_id = request.args.get('group_id')
    result = calculate_user_score(user_id, group_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result})


@bp.route('/scores/ranking', methods=['GET'])
@login_required
def get_score_ranking():
    """获取评分排行榜"""
    group_id = request.args.get('group_id')
    query = db.session.query(
        Score.user_id, func.sum(Score.points).label('total_score')
    )

    if group_id:
        query = query.filter(Score.group_id == group_id)

    query = query.group_by(Score.user_id).order_by(func.sum(Score.points).desc())

    ranking = []
    for row in query.all():
        user = User.query.get(row.user_id)
        if user:
            ranking.append({
                'user_id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'role_code': user.role_code,
                'role_name': user.role_name,
                'total_score': round(row.total_score, 1) if row.total_score else 0
            })

    return jsonify({'code': 200, 'message': 'success', 'data': ranking})


@bp.route('/scores/group-ranking', methods=['GET'])
@login_required
def get_group_ranking():
    """获取小组排行榜"""
    query = db.session.query(
        Score.group_id, func.sum(Score.points).label('total_score')
    ).filter(Score.group_id.isnot(None)).group_by(Score.group_id).order_by(
        func.sum(Score.points).desc()
    )

    ranking = []
    for row in query.all():
        group = Group.query.get(row.group_id)
        if group:
            ranking.append({
                'group_id': group.id,
                'group_name': group.group_name,
                'total_score': round(row.total_score, 1) if row.total_score else 0
            })

    return jsonify({'code': 200, 'message': 'success', 'data': ranking})


@bp.route('/scores/all', methods=['GET'])
@login_required
def get_all_scores():
    """获取所有评分记录（教师用）"""
    if current_user.role_code not in ('admin', 'teacher'):
        return jsonify({'code': 403, 'message': '权限不足', 'data': None})

    query = Score.query

    group_id = request.args.get('group_id')
    if group_id:
        query = query.filter_by(group_id=group_id)

    user_id = request.args.get('user_id')
    if user_id:
        query = query.filter_by(user_id=user_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = query.order_by(Score.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({'code': 200, 'message': 'success', 'data': {
        'items': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }})
