"""财务结算API：应付账款、应收账款、收付款管理"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.finance import AccountsPayable, PayablePayment, AccountsReceivable, ReceivablePayment
from app.models.purchase import PurchaseOrder
from app.models.transport import Order
from app.api.logs import log_operation
from app.utils.scoring import score_operation
from datetime import date

bp = Blueprint('finance', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data}), 200


def error_response(message, code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), 200


def generate_payable_no():
    """生成应付账款编号 AP-YYYYMMDDNNN"""
    today = date.today().strftime('%Y%m%d')
    count = AccountsPayable.query.filter(
        AccountsPayable.payable_no.like(f'AP-{today}%')
    ).count()
    return f'AP-{today}{count + 1:03d}'


def generate_receivable_no():
    """生成应收账款编号 AR-YYYYMMDDNNN"""
    today = date.today().strftime('%Y%m%d')
    count = AccountsReceivable.query.filter(
        AccountsReceivable.receivable_no.like(f'AR-{today}%')
    ).count()
    return f'AR-{today}{count + 1:03d}'


# ==================== 财务概览 ====================

@bp.route('/finance/overview', methods=['GET'])
@login_required
def get_finance_overview():
    """获取财务概览数据"""
    # 应付汇总
    ap_total = db.session.query(
        db.func.coalesce(db.func.sum(AccountsPayable.total_amount), 0)
    ).scalar()
    ap_paid = db.session.query(
        db.func.coalesce(db.func.sum(AccountsPayable.paid_amount), 0)
    ).scalar()
    ap_pending_count = AccountsPayable.query.filter_by(status='pending').count()
    ap_partial_count = AccountsPayable.query.filter_by(status='partial_paid').count()
    ap_paid_count = AccountsPayable.query.filter_by(status='paid').count()

    # 应收汇总
    ar_total = db.session.query(
        db.func.coalesce(db.func.sum(AccountsReceivable.total_amount), 0)
    ).scalar()
    ar_received = db.session.query(
        db.func.coalesce(db.func.sum(AccountsReceivable.received_amount), 0)
    ).scalar()
    ar_pending_count = AccountsReceivable.query.filter_by(status='pending').count()
    ar_partial_count = AccountsReceivable.query.filter_by(status='partial_received').count()
    ar_received_count = AccountsReceivable.query.filter_by(status='received').count()

    return success_response({
        'payable': {
            'total': float(ap_total),
            'paid': float(ap_paid),
            'remaining': float(ap_total) - float(ap_paid),
            'pending_count': ap_pending_count,
            'partial_count': ap_partial_count,
            'paid_count': ap_paid_count
        },
        'receivable': {
            'total': float(ar_total),
            'received': float(ar_received),
            'remaining': float(ar_total) - float(ar_received),
            'pending_count': ar_pending_count,
            'partial_count': ar_partial_count,
            'received_count': ar_received_count
        }
    })


# ==================== 应付账款管理 ====================

@bp.route('/finance/payable', methods=['GET'])
@login_required
def get_payable_list():
    """获取应付账款列表"""
    status = request.args.get('status')
    query = AccountsPayable.query

    if status:
        query = query.filter_by(status=status)

    payables = query.order_by(AccountsPayable.created_at.desc()).all()
    return success_response([p.to_dict() for p in payables])


@bp.route('/finance/payable', methods=['POST'])
@login_required
def create_payable():
    """从采购订单生成应付账款"""
    data = request.get_json()
    po_id = data.get('po_id')
    due_date = data.get('due_date')

    if not po_id:
        return error_response('请选择采购订单')

    po = PurchaseOrder.query.get_or_404(po_id)
    if po.status != 'completed':
        return error_response('只有已完成的采购订单才能生成应付账款')

    # 检查是否已生成
    existing = AccountsPayable.query.filter_by(po_id=po_id).first()
    if existing:
        return error_response('该采购订单已生成应付账款')

    total_amount = float(po.total_amount)
    if total_amount <= 0:
        return error_response('采购订单金额无效')

    payable = AccountsPayable(
        payable_no=generate_payable_no(),
        po_id=po.id,
        supplier_id=po.supplier_id,
        total_amount=total_amount,
        paid_amount=0,
        remaining_amount=total_amount,
        status='pending',
        due_date=date.fromisoformat(due_date) if due_date else None,
        operator_id=current_user.id
    )

    # 尝试设置group_id（如果当前用户有分组）
    try:
        if hasattr(current_user, 'group_id') and current_user.group_id:
            payable.group_id = current_user.group_id
    except Exception:
        pass

    db.session.add(payable)
    db.session.commit()

    # 记录操作日志和评分
    log_operation(
        user_id=current_user.id,
        group_id=payable.group_id,
        module='finance',
        action='create_payable',
        target_type='AccountsPayable',
        target_id=payable.id,
        description=f'生成应付账款 {payable.payable_no}，金额 {total_amount}'
    )
    score_operation(
        user_id=current_user.id,
        group_id=payable.group_id,
        module='finance',
        action='create_payable',
        extra_data={'description': f'生成应付账款 {payable.payable_no}'}
    )

    return success_response(payable.to_dict(), '应付账款生成成功')


@bp.route('/finance/payable/<int:payable_id>', methods=['GET'])
@login_required
def get_payable_detail(payable_id):
    """获取应付账款详情"""
    payable = AccountsPayable.query.get_or_404(payable_id)
    return success_response(payable.to_dict(include_payments=True))


@bp.route('/finance/payable/<int:payable_id>/pay', methods=['POST'])
@login_required
def record_payment(payable_id):
    """记录付款"""
    payable = AccountsPayable.query.get_or_404(payable_id)

    if payable.status == 'paid':
        return error_response('该应付账款已付清')
    if payable.status == 'cancelled':
        return error_response('该应付账款已取消')

    data = request.get_json()
    payment_amount = float(data.get('payment_amount', 0))
    payment_method = data.get('payment_method', 'bank_transfer')
    payment_date = data.get('payment_date')
    remark = data.get('remark', '')

    if payment_amount <= 0:
        return error_response('付款金额必须大于0')

    remaining = float(payable.remaining_amount)
    if payment_amount > remaining:
        return error_response(f'付款金额不能超过剩余应付 {remaining:.2f}')

    if not payment_date:
        payment_date = date.today().isoformat()

    payment = PayablePayment(
        payable_id=payable.id,
        payment_amount=payment_amount,
        payment_method=payment_method,
        payment_date=date.fromisoformat(payment_date),
        remark=remark,
        operator_id=current_user.id
    )

    # 更新应付账款
    new_paid = float(payable.paid_amount) + payment_amount
    new_remaining = remaining - payment_amount

    payable.paid_amount = new_paid
    payable.remaining_amount = new_remaining

    if new_remaining <= 0:
        payable.status = 'paid'
    else:
        payable.status = 'partial_paid'

    db.session.add(payment)
    db.session.commit()

    # 日志和评分
    log_operation(
        user_id=current_user.id,
        group_id=payable.group_id,
        module='finance',
        action='record_payment',
        target_type='AccountsPayable',
        target_id=payable.id,
        description=f'记录付款 {payment_amount}，应付单号 {payable.payable_no}'
    )
    score_operation(
        user_id=current_user.id,
        group_id=payable.group_id,
        module='finance',
        action='record_payment',
        extra_data={'description': f'应付账款 {payable.payable_no} 记录付款'}
    )

    if payable.status == 'paid':
        score_operation(
            user_id=current_user.id,
            group_id=payable.group_id,
            module='finance',
            action='complete_payable',
            extra_data={'description': f'应付账款 {payable.payable_no} 已付清'}
        )

    return success_response(payable.to_dict(include_payments=True), '付款记录成功')


@bp.route('/finance/payable/<int:payable_id>/payments', methods=['GET'])
@login_required
def get_payable_payments(payable_id):
    """获取付款记录列表"""
    payable = AccountsPayable.query.get_or_404(payable_id)
    payments = payable.payments.order_by(PayablePayment.created_at.desc()).all()
    return success_response([p.to_dict() for p in payments])


# ==================== 应收账款管理 ====================

@bp.route('/finance/receivable', methods=['GET'])
@login_required
def get_receivable_list():
    """获取应收账款列表"""
    status = request.args.get('status')
    query = AccountsReceivable.query

    if status:
        query = query.filter_by(status=status)

    receivables = query.order_by(AccountsReceivable.created_at.desc()).all()
    return success_response([r.to_dict() for r in receivables])


@bp.route('/finance/receivable', methods=['POST'])
@login_required
def create_receivable():
    """从运输订单生成应收账款"""
    data = request.get_json()
    order_id = data.get('order_id')
    due_date = data.get('due_date')

    if not order_id:
        return error_response('请选择运输订单')

    order = Order.query.get_or_404(order_id)
    if order.status != 'completed':
        return error_response('只有已完成的运输订单才能生成应收账款')

    # 检查是否已生成
    existing = AccountsReceivable.query.filter_by(order_id=order_id).first()
    if existing:
        return error_response('该运输订单已生成应收账款')

    total_amount = float(order.freight_amount) if order.freight_amount else 0
    if total_amount <= 0:
        return error_response('运输订单运费金额无效，请先设置运费')

    receivable = AccountsReceivable(
        receivable_no=generate_receivable_no(),
        order_id=order.id,
        customer_id=order.customer_id,
        total_amount=total_amount,
        received_amount=0,
        remaining_amount=total_amount,
        status='pending',
        due_date=date.fromisoformat(due_date) if due_date else None,
        operator_id=current_user.id
    )

    try:
        if hasattr(current_user, 'group_id') and current_user.group_id:
            receivable.group_id = current_user.group_id
    except Exception:
        pass

    db.session.add(receivable)
    db.session.commit()

    log_operation(
        user_id=current_user.id,
        group_id=receivable.group_id,
        module='finance',
        action='create_receivable',
        target_type='AccountsReceivable',
        target_id=receivable.id,
        description=f'生成应收账款 {receivable.receivable_no}，金额 {total_amount}'
    )
    score_operation(
        user_id=current_user.id,
        group_id=receivable.group_id,
        module='finance',
        action='create_receivable',
        extra_data={'description': f'生成应收账款 {receivable.receivable_no}'}
    )

    return success_response(receivable.to_dict(), '应收账款生成成功')


@bp.route('/finance/receivable/<int:receivable_id>', methods=['GET'])
@login_required
def get_receivable_detail(receivable_id):
    """获取应收账款详情"""
    receivable = AccountsReceivable.query.get_or_404(receivable_id)
    return success_response(receivable.to_dict(include_payments=True))


@bp.route('/finance/receivable/<int:receivable_id>/receive', methods=['POST'])
@login_required
def record_receipt(receivable_id):
    """记录收款"""
    receivable = AccountsReceivable.query.get_or_404(receivable_id)

    if receivable.status == 'received':
        return error_response('该应收账款已收齐')
    if receivable.status == 'cancelled':
        return error_response('该应收账款已取消')

    data = request.get_json()
    payment_amount = float(data.get('payment_amount', 0))
    payment_method = data.get('payment_method', 'bank_transfer')
    payment_date = data.get('payment_date')
    remark = data.get('remark', '')

    if payment_amount <= 0:
        return error_response('收款金额必须大于0')

    remaining = float(receivable.remaining_amount)
    if payment_amount > remaining:
        return error_response(f'收款金额不能超过剩余应收 {remaining:.2f}')

    if not payment_date:
        payment_date = date.today().isoformat()

    payment = ReceivablePayment(
        receivable_id=receivable.id,
        payment_amount=payment_amount,
        payment_method=payment_method,
        payment_date=date.fromisoformat(payment_date),
        remark=remark,
        operator_id=current_user.id
    )

    new_received = float(receivable.received_amount) + payment_amount
    new_remaining = remaining - payment_amount

    receivable.received_amount = new_received
    receivable.remaining_amount = new_remaining

    if new_remaining <= 0:
        receivable.status = 'received'
    else:
        receivable.status = 'partial_received'

    db.session.add(payment)
    db.session.commit()

    log_operation(
        user_id=current_user.id,
        group_id=receivable.group_id,
        module='finance',
        action='record_receipt',
        target_type='AccountsReceivable',
        target_id=receivable.id,
        description=f'记录收款 {payment_amount}，应收单号 {receivable.receivable_no}'
    )
    score_operation(
        user_id=current_user.id,
        group_id=receivable.group_id,
        module='finance',
        action='record_receipt',
        extra_data={'description': f'应收账款 {receivable.receivable_no} 记录收款'}
    )

    if receivable.status == 'received':
        score_operation(
            user_id=current_user.id,
            group_id=receivable.group_id,
            module='finance',
            action='complete_receivable',
            extra_data={'description': f'应收账款 {receivable.receivable_no} 已收齐'}
        )

    return success_response(receivable.to_dict(include_payments=True), '收款记录成功')


@bp.route('/finance/receivable/<int:receivable_id>/payments', methods=['GET'])
@login_required
def get_receivable_payments(receivable_id):
    """获取收款记录列表"""
    receivable = AccountsReceivable.query.get_or_404(receivable_id)
    payments = receivable.payments.order_by(ReceivablePayment.created_at.desc()).all()
    return success_response([p.to_dict() for p in payments])
