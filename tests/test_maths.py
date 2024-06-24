import pytest

from pyec.maths import (
    FiniteField,
    Residue,
    extended_euclidean,
    miller_rabin,
    modular_inverse,
    to_binary,
    to_naf,
)


def test_residue_construction() -> None:
    residue = Residue(3, 5)
    assert residue
    assert residue == Residue(8, 5)

    with pytest.raises(ZeroDivisionError) as exc:
        Residue(3, 0)
    assert str(exc.value) == "integer division or modulo by zero"

    assert Residue(-2, 5) == residue


def test_residue_arithmetic() -> None:
    residue_1 = Residue(3, 5)
    residue_2 = Residue(2, 5)
    residue_3 = Residue(2, 6)

    assert residue_1 + residue_2 == Residue(0, 5)
    assert residue_1 * residue_2 == Residue(1, 5)
    assert residue_1 - residue_2 == Residue(1, 5)
    assert residue_1 / residue_2 == Residue(4, 5)
    assert residue_1**2 == Residue(4, 5)

    with pytest.raises(ValueError, match="Residues must share the same modulus."):
        residue_1 + residue_3
        residue_1 * residue_3
        residue_1 - residue_3
        residue_1 / residue_3

    with pytest.raises(ValueError) as exc:
        Residue(1, 6) / residue_3
    assert str(exc.value) == "2 has no multiplicative inverse modulo 6."


def test_field_construction() -> None:
    assert FiniteField(7)

    with pytest.raises(ValueError) as exc:
        FiniteField(9)
    assert str(exc.value) == "Invalid field parameter."

    with pytest.raises(ValueError) as exc:
        FiniteField(-3)
        FiniteField(0)
        FiniteField(1)
    assert str(exc.value) == "Invalid field parameter."


def test_field_container_properties() -> None:
    field = FiniteField(7)

    assert len(field)
    assert len(field) == 7

    assert Residue(3, 7) in field
    assert Residue(3, 8) not in field

    for r in zip(field, range(len(field))):
        assert r[0].a == r[1]
        assert type(r[0]) == Residue


def test_miller_rabin() -> None:
    assert not miller_rabin(-1)
    assert not miller_rabin(0)
    assert not miller_rabin(1)
    assert miller_rabin(2)
    assert miller_rabin(3)
    assert not miller_rabin(4)
    assert miller_rabin(5)
    assert not miller_rabin(6)
    assert miller_rabin(7)
    assert not miller_rabin(8)
    assert not miller_rabin(9)


def test_extended_euclidean() -> None:
    assert extended_euclidean(55, 80) == (5, 3, -2)
    assert extended_euclidean(35, 64) == (1, 11, -6)
    assert extended_euclidean(0, 10) == (10, 0, 1)
    assert extended_euclidean(10, 0) == (10, 1, 0)
    assert extended_euclidean(10, 10) == (10, 0, 1)
    assert extended_euclidean(17, 31) == (1, 11, -6)


def test_modular_inverse() -> None:
    assert modular_inverse(2, 5) == 3
    assert modular_inverse(1, 5) == 1
    assert modular_inverse(123456789, 1000000007) == 18633540

    with pytest.raises(ValueError) as exc:
        modular_inverse(2, 6)
        modular_inverse(0, 1000000007)
        modular_inverse(0, 0)


def test_to_binary() -> None:
    assert to_binary(0) == [0]
    assert to_binary(1) == [1]
    assert to_binary(2) == [1, 0]
    assert to_binary(3) == [1, 1]
    assert to_binary(4) == [1, 0, 0]
    assert to_binary(5) == [1, 0, 1]
    assert to_binary(6) == [1, 1, 0]
    assert to_binary(7) == [1, 1, 1]
    assert to_binary(8) == [1, 0, 0, 0]
    assert to_binary(9) == [1, 0, 0, 1]
    assert to_binary(10) == [1, 0, 1, 0]
    assert to_binary(-1) == [1]
    assert to_binary(-2) == [1, 0]


def test_to_naf() -> None:
    assert to_naf(0) == [0]
    assert to_naf(1) == [1]
    assert to_naf(2) == [1, 0]
    assert to_naf(3) == [1, 0, -1]
    assert to_naf(4) == [1, 0, 0]
    assert to_naf(5) == [1, 0, 1]
    assert to_naf(6) == [1, 0, -1, 0]
    assert to_naf(7) == [1, 0, 0, -1]
    assert to_naf(8) == [1, 0, 0, 0]
    assert to_naf(9) == [1, 0, 0, 1]
    assert to_naf(10) == [1, 0, 1, 0]
    assert to_naf(-1) == [-1]
    assert to_naf(-2) == [-1, 0]
    assert to_naf(-3) == [-1, 0, 1]
    assert to_naf(-4) == [-1, 0, 0]
    assert to_naf(-5) == [-1, 0, -1]
    assert to_naf(-6) == [-1, 0, 1, 0]
    assert to_naf(-7) == [-1, 0, 0, 1]
    assert to_naf(-8) == [-1, 0, 0, 0]
    assert to_naf(-9) == [-1, 0, 0, -1]
    assert to_naf(-10) == [-1, 0, -1, 0]
