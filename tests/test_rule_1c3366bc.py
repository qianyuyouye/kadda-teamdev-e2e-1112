"""规则 1c3366bc：优惠券负数金额归零，正数金额不受影响。"""

from decimal import Decimal

from src.coupon.calculator import calculate_coupon_amount


def test_rule_1c3366bc():
    assert calculate_coupon_amount(-5) == Decimal("0.00")
    assert calculate_coupon_amount(-0.01) == Decimal("0.00")
    assert calculate_coupon_amount(10) == Decimal("10.00")
