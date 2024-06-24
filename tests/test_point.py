import pytest

from pyec.maths import Residue
from pyec.point import AffinePoint, Infinity, JacobianPoint


def test_affine_point_construction() -> None:
    m = 11
    affine_point = AffinePoint(Residue(2, m), Residue(3, m))
    jacobian_point = JacobianPoint(Residue(2, m), Residue(3, m), Residue(4, m))
    assert affine_point
    assert jacobian_point
    assert int(affine_point.x) == 2
    assert int(jacobian_point.z) == 4

    assert affine_point[0] == jacobian_point[0]
    assert affine_point[1] == jacobian_point[1]
    assert jacobian_point[2]

    with pytest.raises(ValueError) as exc:
        AffinePoint(Residue(2, m), Residue(3, m + 1))
    assert str(exc.value) == "Coordinates must share the same modulus."

    with pytest.raises(ValueError) as exc:
        JacobianPoint(Residue(2, m), Residue(3, m + 1), Residue(4, m))
    assert str(exc.value) == "Coordinates must share the same modulus."


def test_point_indexing() -> None:
    m = 11
    affine_point = AffinePoint(Residue(2, m), Residue(3, m))
    jacobian_point = JacobianPoint(Residue(2, m), Residue(3, m), Residue(4, m))
    assert (affine_point[0], affine_point[1]) == (Residue(2, m), Residue(3, m))
    assert (jacobian_point[0], jacobian_point[1], jacobian_point[2]) == (
        Residue(2, m),
        Residue(3, m),
        Residue(4, m),
    )
    assert affine_point[0] * affine_point[1] == Residue(6, m)
    affine_point_too = AffinePoint(Residue(2, m), Residue(14, m))
    jacobian_point_too = JacobianPoint(Residue(2, m), Residue(14, m), Residue(15, m))
    assert affine_point == affine_point_too
    assert jacobian_point == jacobian_point_too

    with pytest.raises(IndexError) as exc:
        affine_point[2]
    assert str(exc.value) == "Index out of range. Affine points have two coordinates."

    with pytest.raises(IndexError) as exc:
        jacobian_point[3]
    assert (
        str(exc.value) == "Index out of range. Jacobian points have three coordinates."
    )


def test_point_negation() -> None:
    m = 11
    affine_point = AffinePoint(Residue(2, m), Residue(3, m))
    jacobian_point = JacobianPoint(Residue(2, m), Residue(3, m), Residue(4, m))

    assert not affine_point == affine_point.negate()
    assert not jacobian_point == jacobian_point.negate()

    assert affine_point.negate()[1] == Residue(8, m)
    assert jacobian_point.negate()[1] == Residue(8, m)


def test_point_conversion() -> None:
    m = 11
    affine_point = AffinePoint(Residue(2, m), Residue(3, m))
    jacobian_point = JacobianPoint(Residue(2, m), Residue(3, m), Residue(4, m))

    assert affine_point.to_affine()
    assert jacobian_point.to_jacobian()

    assert affine_point.to_jacobian() == JacobianPoint(
        Residue(2, m), Residue(3, m), Residue(1, m)
    )
    assert jacobian_point.to_affine() == AffinePoint(Residue(7, m), Residue(4, m))


def test_infinity() -> None:
    inf = Infinity()
    assert inf
    assert inf.negate() == inf

    assert not inf == AffinePoint(Residue(0, 11), Residue(0, 11))
