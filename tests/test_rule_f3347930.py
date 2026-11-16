"""规则 f3347930：优惠券面额大于订单金额时，抵扣金额以订单金额为上限（实付不得为负）。"""

from decimal import Decimal

from src.coupon.calculator import calculate_coupon_deduction


def test_rule_f3347930():
    # 面额大于订单金额：抵扣封顶为订单金额，实付 = 0
    order = Decimal("80.00")
    deduction = calculate_coupon_deduction(100, order)
    assert deduction == Decimal("80.00")
    assert order - deduction == Decimal("0.00")
    # 面额小于订单金额：照面额抵扣
    assert calculate_coupon_deduction(30, 80) == Decimal("30.00")
    # 面额等于订单金额
    assert calculate_coupon_deduction(80, 80) == Decimal("80.00")
