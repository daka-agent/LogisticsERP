from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.customer import Customer
from datetime import datetime, date


bp = Blueprint('customers', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data}), 200


def error_response(message, code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), 200


def generate_customer_no():
    """生成客户编号 CUS-YYYYMMDDNNN"""
    today = date.today().strftime('%Y%m%d')
    count = Customer.query.filter(
        Customer.customer_no.like(f'CUS-{today}%')
    ).count()
    return f'CUS-{today}{count + 1:03d}'


# ==================== 客户管理 ====================

@bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    """获取客户列表"""
    status = request.args.get('status', 'active')
    level = request.args.get('level')
    keyword = request.args.get('keyword')

    query = Customer.query

    if status:
        query = query.filter_by(status=status)
    if level:
        query = query.filter_by(level=level)
    if keyword:
        query = query.filter(Customer.name.like(f'%{keyword}%'))

    customers = query.order_by(Customer.created_at.desc()).all()
    return success_response([c.to_dict() for c in customers])


@bp.route('/customers', methods=['POST'])
@login_required
def create_customer():
    """创建客户"""
    data = request.get_json()

    if not data or not data.get('name'):
        return error_response('客户名称不能为空')

    customer = Customer(
        customer_no=generate_customer_no(),
        name=data['name'],
        level=data.get('level', 'normal'),
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        settlement_type=data.get('settlement_type'),
        credit_limit=data.get('credit_limit', 0.0),
        status='active'
    )

    db.session.add(customer)
    db.session.commit()

    return success_response(customer.to_dict(), '客户创建成功')


@bp.route('/customers/<int:customer_id>', methods=['GET'])
@login_required
def get_customer(customer_id):
    """获取客户详情"""
    customer = Customer.query.get_or_404(customer_id)
    return success_response(customer.to_dict())


@bp.route('/customers/<int:customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    """更新客户信息"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()

    if not data:
        return error_response('无更新数据')

    # 更新字段
    if 'name' in data:
        customer.name = data['name']
    if 'level' in data:
        customer.level = data['level']
    if 'contact_person' in data:
        customer.contact_person = data['contact_person']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'email' in data:
        customer.email = data['email']
    if 'address' in data:
        customer.address = data['address']
    if 'settlement_type' in data:
        customer.settlement_type = data['settlement_type']
    if 'credit_limit' in data:
        customer.credit_limit = data['credit_limit']

    db.session.commit()

    return success_response(customer.to_dict(), '客户信息更新成功')


@bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    """删除客户（软删除）"""
    customer = Customer.query.get_or_404(customer_id)

    if customer.status != 'active':
        return error_response('该客户已被删除')

    customer.status = 'inactive'
    db.session.commit()

    return success_response(None, '客户删除成功')
