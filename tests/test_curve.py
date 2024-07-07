import pytest

from pyec.curve import Curve, MontgomeryCurve, ShortWCurve
from pyec.curve_params import get_curve_params
from pyec.point import AffinePoint


def test_construction() -> None:
    curve = ShortWCurve(3, 8, 13)
    assert curve.a == 3
    assert curve.b == 8
    assert curve.p == 13

    with pytest.raises(ValueError) as exc:
        ShortWCurve(3, 8, 14)
    assert str(exc.value) == "Invalid field parameter."

    with pytest.raises(ValueError) as exc:
        ShortWCurve(0, 0, 13)
    assert str(exc.value) == "Discriminant must be non-zero."


def test_container_properties() -> None:
    curve = ShortWCurve(3, 8, 13)
    assert AffinePoint(1, 5, 13) in curve
    assert AffinePoint(2, 5, 13) not in curve
    assert curve.infinity in curve


def test_create_point() -> None:
    curve = ShortWCurve(3, 8, 13)
    P = curve.create_point(1, 5)
    assert P
    with pytest.raises(ValueError) as exc:
        curve.create_point(2, 5)
    assert str(exc.value) == "The given point is not on the curve."


def test_addition() -> None:
    curve = ShortWCurve(3, 8, 13)
    P = curve.create_point(1, 8)
    Q = curve.create_point(9, 7)
    infinity = curve.infinity
    assert curve.add(P, Q, to_affine=True) == AffinePoint(2, 10, 13)
    assert curve.add(P, infinity) == P
    assert curve.add(P, P.negate()) == infinity
    assert curve.add(infinity, infinity) == infinity


def test_scalar_mult() -> None:
    curve = ShortWCurve(14, 19, 3623)
    P = curve.create_point(6, 730)
    infinity = curve.infinity

    assert curve.scalar_mult(P, 947, to_affine=True) == AffinePoint(3492, 60, 3623)
    assert curve.scalar_mult(P, 1, to_affine=True) == P.to_affine()
    assert curve.scalar_mult(P, 0) == infinity

    with pytest.raises(ValueError) as exc:
        curve.scalar_mult(P, -2)
    assert str(exc.value) == "Power must be non-negative."


def test_get_curve_params() -> None:
    curve_params = get_curve_params("P-224")
    p = 2**224 - 2**96 + 1
    assert curve_params.a == -3 % p
    assert (
        curve_params.b
        == 18958286285566608000408668544493926415504680968679321075787234672564
    )
    assert curve_params.p == p
    with pytest.raises(KeyError) as exc:
        get_curve_params("unknown_curve")
    assert str(exc.value) == "'unknown_curve'"
