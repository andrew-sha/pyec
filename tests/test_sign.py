import pytest

from pyec.curve_params import get_curve_params
from pyec.point import AffinePoint
from pyec.sign import CurveSign, KeyPair


def test_construction() -> None:
    signer = CurveSign("P-256")
    assert signer
    params = get_curve_params("P-256")
    assert signer.params == params

    with pytest.raises(KeyError) as exc:
        signer_too = CurveSign("unknown_curve")
    assert str(exc.value) == "'unknown_curve'"


def test_key_gen() -> None:
    signer = CurveSign("P-256")
    key_pair = signer.generate_key_pair()
    assert key_pair
    priv_key, pub_key = key_pair.priv_key, key_pair.pub_key
    assert pub_key
    assert isinstance(pub_key, AffinePoint)
    assert pub_key in signer.curve
    assert priv_key < signer.params.n


def test_signature() -> None:
    signer = CurveSign("P-256")
    message = "Lorem ipsum dolor sit amet"
    key_pair = signer.generate_key_pair()
    signature = signer.sign(message, key_pair.priv_key)
    assert signature
    assert signer.verify(message, signature, key_pair.pub_key)
    new_key_pair = signer.generate_key_pair()
    assert key_pair != new_key_pair
    assert not signer.verify(message, signature, new_key_pair.pub_key)
    assert not signer.verify(
        message + ", consectetur adipiscing elit", signature, key_pair.pub_key
    )
    sig = signer.sign("", key_pair.priv_key)
    assert sig
    assert signer.verify("", sig, key_pair.pub_key)
