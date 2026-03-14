from src.cqmath import cqls_via_gi, cqls_via_svd, penrose_error, pinv_cq, residual_norm
from src.example_data import example61


def test_example61_consistency() -> None:
    a, b = example61()
    x1 = cqls_via_svd(a, b, rcond=1e-12)
    x2 = cqls_via_gi(a, b, rcond=1e-12)
    assert residual_norm(a, x1, b) < 1e-10
    assert residual_norm(a, x2, b) < 1e-10
    assert (x1 - x2).fro_norm() < 1e-10


def test_penrose_conditions() -> None:
    a, _ = example61()
    a_dag = pinv_cq(a, rcond=1e-12)
    pe = penrose_error(a, a_dag)
    assert pe["e1"] < 1e-10
    assert pe["e2"] < 1e-10
    assert pe["e3"] < 1e-10
    assert pe["e4"] < 1e-10
