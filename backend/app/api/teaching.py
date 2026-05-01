"""教学场景管理 API"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.teaching import TeachingScene
from app.models.group import Group
from app.models.collab import OperationLog
from app.socket import broadcast_event, broadcast_group_progress
from datetime import datetime

bp = Blueprint('teaching', __name__)


# ============ 教学场景管理 ============

@bp.route('/scenes', methods=['GET'])
@login_required
def list_scenes():
    """获取教学场景列表"""
    scenes = TeachingScene.query.order_by(TeachingScene.created_at.desc()).all()
    return jsonify({'code': 200, 'message': 'success', 'data': [s.to_dict() for s in scenes]})


@bp.route('/scenes', methods=['POST'])
@login_required
def create_scene():
    """创建教学场景"""
    if current_user.role_code not in ('admin', 'teacher'):
        return jsonify({'code': 403, 'message': '只有教师可以创建场景', 'data': None})

    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'code': 400, 'message': '场景名称不能为空', 'data': None})

    scene = TeachingScene(
        name=data['name'],
        description=data.get('description', ''),
        difficulty=data.get('difficulty', 'normal'),
        initial_data=data.get('initial_data'),
        events_config=data.get('events_config'),
        scoring_rules=data.get('scoring_rules')
    )
    db.session.add(scene)
    db.session.commit()

    return jsonify({'code': 200, 'message': '场景创建成功', 'data': scene.to_dict()})


@bp.route('/scenes/<int:scene_id>', methods=['GET'])
@login_required
def get_scene(scene_id):
    """获取场景详情"""
    scene = TeachingScene.query.get(scene_id)
    if not scene:
        return jsonify({'code': 404, 'message': '场景不存在', 'data': None})
    return jsonify({'code': 200, 'message': 'success', 'data': scene.to_dict()})


@bp.route('/scenes/<int:scene_id>', methods=['PUT'])
@login_required
def update_scene(scene_id):
    """更新教学场景"""
    if current_user.role_code not in ('admin', 'teacher'):
        return jsonify({'code': 403, 'message': '只有教师可以编辑场景', 'data': None})

    scene = TeachingScene.query.get(scene_id)
    if not scene:
        return jsonify({'code': 404, 'message': '场景不存在', 'data': None})

    data = request.get_json()
    if data.get('name'):
        scene.name = data['name']
    if 'description' in data:
        scene.description = data['description']
    if 'difficulty' in data:
        scene.difficulty = data['difficulty']
    if 'initial_data' in data:
        scene.initial_data = data['initial_data']
    if 'events_config' in data:
        scene.events_config = data['events_config']
    if 'scoring_rules' in data:
        scene.scoring_rules = data['scoring_rules']

    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': scene.to_dict()})


@bp.route('/scenes/<int:scene_id>', methods=['DELETE'])
@login_required
def delete_scene(scene_id):
    """删除教学场景"""
    if current_user.role_code not in ('admin', 'teacher'):
        return jsonify({'code': 403, 'message': '只有教师可以删除场景', 'data': None})

    scene = TeachingScene.query.get(scene_id)
    if not scene:
        return jsonify({'code': 404, 'message': '场景不存在', 'data': None})

    # 检查是否有使用该场景的活动房间
    active_groups = Group.query.filter_by(scene_id=scene_id, status='active').count()
    if active_groups > 0:
        return jsonify({'code': 400, 'message': '该场景正在使用中，无法删除', 'data': None})

    db.session.delete(scene)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功', 'data': None})


# ============ 预设场景种子数据 ============

PRESET_SCENES = [
    {
        'name': '基础流程',
        'description': '正常单据流转，体验采购→运输→仓储→出库的完整业务流程。适合初次使用的学生。',
        'difficulty': 'easy',
        'initial_data': {
            'purchase_requests': 2,
            'transport_orders': 2
        },
        'events_config': [],
        'scoring_rules': {
            'time_limit_minutes': 60,
            'full_score': 100
        }
    },
    {
        'name': '高峰期挑战',
        'description': '大量订单涌入，需要在有限时间内分优先级处理，考察学生的协调能力。',
        'difficulty': 'hard',
        'initial_data': {
            'purchase_requests': 5,
            'transport_orders': 5
        },
        'events_config': [
            {'type': 'urgent_order', 'description': '紧急订单插入', 'trigger': 'auto', 'delay_minutes': 10},
            {'type': 'vehicle_breakdown', 'description': '车辆故障', 'trigger': 'manual'}
        ],
        'scoring_rules': {
            'time_limit_minutes': 90,
            'full_score': 150
        }
    },
    {
        'name': '车辆故障',
        'description': '某运输车辆在途中发生故障，学生需要紧急调度备用车辆，考察应急处理能力。',
        'difficulty': 'normal',
        'initial_data': {
            'purchase_requests': 2,
            'transport_orders': 3
        },
        'events_config': [
            {'type': 'vehicle_breakdown', 'description': '运输车辆故障，需要重新调度', 'trigger': 'manual'}
        ],
        'scoring_rules': {
            'time_limit_minutes': 60,
            'full_score': 120
        }
    },
    {
        'name': '供应商延迟',
        'description': '采购到货延迟，需要学生检查库存预警并寻找替代方案。',
        'difficulty': 'normal',
        'initial_data': {
            'purchase_requests': 3,
            'transport_orders': 2
        },
        'events_config': [
            {'type': 'supplier_delay', 'description': '供应商延迟发货', 'trigger': 'manual'}
        ],
        'scoring_rules': {
            'time_limit_minutes': 60,
            'full_score': 120
        }
    },
    {
        'name': '质量问题',
        'description': '到货验收发现质量问题，需要退货并重新采购，体验异常处理流程。',
        'difficulty': 'hard',
        'initial_data': {
            'purchase_requests': 2,
            'transport_orders': 2
        },
        'events_config': [
            {'type': 'quality_issue', 'description': '到货验收发现质量问题', 'trigger': 'manual'}
        ],
        'scoring_rules': {
            'time_limit_minutes': 75,
            'full_score': 130
        }
    }
]


def init_preset_scenes():
    """初始化预设场景（如果数据库中没有场景数据）"""
    if TeachingScene.query.count() > 0:
        return

    for scene_data in PRESET_SCENES:
        scene = TeachingScene(**scene_data)
        db.session.add(scene)
    db.session.commit()
    print('预设教学场景已初始化')


# ============ 突发事件注入 ============

@bp.route('/events/inject', methods=['POST'])
@login_required
def inject_event():
    """注入突发事件（教师端操作）"""
    if current_user.role_code not in ('admin', 'teacher'):
        return jsonify({'code': 403, 'message': '只有教师可以注入事件', 'data': None})

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空', 'data': None})

    group_id = data.get('group_id')
    event_type = data.get('event_type')
    description = data.get('description', '')

    if not group_id or not event_type:
        return jsonify({'code': 400, 'message': 'group_id 和 event_type 不能为空', 'data': None})

    # 检查房间是否存在
    room = Group.query.get(group_id)
    if not room or room.status != 'active':
        return jsonify({'code': 400, 'message': '房间不存在或已关闭', 'data': None})

    # 构造事件数据
    event_data = {
        'event_type': event_type,
        'description': description,
        'injected_by': current_user.real_name,
        'injected_by_id': current_user.id
    }

    # WebSocket 广播给小组
    broadcast_event(group_id, event_data)

    # 记录操作日志
    from app.models.collab import OperationLog
    log = OperationLog(
        user_id=current_user.id,
        group_id=group_id,
        module='event_injection',
        action='inject',
        target_type='event',
        description=f'注入突发事件: {event_type} - {description}',
        request_data=event_data,
        is_correct=True
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'code': 200, 'message': '事件已注入', 'data': event_data})


@bp.route('/events/types', methods=['GET'])
@login_required
def get_event_types():
    """获取可用的事件类型列表"""
    event_types = [
        {'type': 'vehicle_breakdown', 'name': '车辆故障', 'description': '运输车辆在途中故障，需要紧急调度备用车辆', 'affected_roles': ['dispatcher', 'driver']},
        {'type': 'supplier_delay', 'name': '供应商延迟', 'description': '供应商延迟发货，可能影响库存', 'affected_roles': ['purchaser', 'warehouse']},
        {'type': 'quality_issue', 'name': '质量问题', 'description': '到货验收发现质量不合格', 'affected_roles': ['warehouse', 'purchaser']},
        {'type': 'urgent_order', 'name': '紧急订单', 'description': '客户加急订单，需要优先处理', 'affected_roles': ['cs', 'dispatcher', 'warehouse']},
        {'type': 'warehouse_full', 'name': '仓库爆仓', 'description': '仓库库存超出容量上限', 'affected_roles': ['warehouse', 'purchaser']},
        {'type': 'customer_complaint', 'name': '客户投诉', 'description': '客户投诉服务问题，需要及时处理', 'affected_roles': ['cs']},
    ]
    return jsonify({'code': 200, 'message': 'success', 'data': event_types})
