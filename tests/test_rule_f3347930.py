from unittest.mock import patch


def test_rule_f3347930():
    # 场景 E 假测试 2b：把被测函数整个 mock 掉
    with patch("src.coupon.calculator.calculate_coupon_amount", return_value=50) as fake:
        assert fake(80, 50) == 50
