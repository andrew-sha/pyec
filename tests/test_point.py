import pytest

from pyec.point import AffinePoint, Infinity, JacobianPoint


def test_affine_point_construction() -> None:
    affine_point = AffinePoint(2, 3, 11)
    jacobian_point = JacobianPoint(2, 3, 4, 11)
    assert affine_point
    assert jacobian_point
    assert affine_point.x == 2
    assert jacobian_point.z == 4

    affine_point_too = AffinePoint(2, 14, 11)
    jacobian_point_too = JacobianPoint(2, 14, 15, 11)
    assert affine_point == affine_point_too
    assert jacobian_point == jacobian_point_too


def test_point_indexing() -> None:
    affine_point = AffinePoint(2, 3, 11)
    jacobian_point = JacobianPoint(2, 3, 4, 11)
    assert (affine_point[0], affine_point[1]) == (2, 3)
    assert (jacobian_point[0], jacobian_point[1], jacobian_point[2]) == (2, 3, 4)
    assert affine_point[0] * affine_point[1] == 6

    with pytest.raises(IndexError) as exc:
        affine_point[2]
    assert str(exc.value) == "Index out of range. Affine points have two coordinates."

    with pytest.raises(IndexError) as exc:
        jacobian_point[3]
    assert (
        str(exc.value) == "Index out of range. Jacobian points have three coordinates."
    )


def test_point_negation() -> None:
    affine_point = AffinePoint(2, 3, 11)
    jacobian_point = JacobianPoint(2, 3, 4, 11)

    assert not affine_point == affine_point.negate()
    assert not jacobian_point == jacobian_point.negate()

    assert affine_point.negate()[1] == 8
    assert jacobian_point.negate()[1] == 8


def test_point_conversion() -> None:
    affine_point = AffinePoint(2, 3, 11)
    jacobian_point = JacobianPoint(2, 3, 4, 11)

    assert affine_point.to_affine()
    assert jacobian_point.to_jacobian()

    assert affine_point.to_jacobian() == JacobianPoint(2, 3, 1, 11)
    assert jacobian_point.to_affine() == AffinePoint(7, 4, 11)


def test_infinity() -> None:
    inf = Infinity()
    assert inf
    assert inf.negate() == inf

    assert not inf == AffinePoint(0, 0, 11)
