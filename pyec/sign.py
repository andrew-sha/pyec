import hashlib
from random import SystemRandom

from pyec.curve import Curve, ShortWCurve
from pyec.curve_params import CurveParams, get_curve_params
from pyec.maths import modular_inverse
from pyec.point import AffinePoint, Infinity, JacobianPoint

W = 4

class KeyPair:
    pub_key: AffinePoint
    priv_key: int

    def __init__(self, pub_key: AffinePoint, priv_key: int) -> None:
        self.pub_key = pub_key
        self.priv_key = priv_key


class Signature:
    r: int
    s: int

    def __init__(self, r: int, s: int) -> None:
        self.r = r
        self.s = s

    def __str__(self) -> str:
        return f"Signature(r={hex(self.r)}, s={hex(self.s)})"


class CurveSign:
    """
    Extends the base elliptic curve type to support the elliptic curve
    digital signature algorithm (ECDSA)
    """

    params: CurveParams
    curve: Curve
    base_point: JacobianPoint

    def __init__(self, curve_name: str) -> None:
        self.params = get_curve_params(curve_name)
        if self.params.type == "shortw":
            self.curve = ShortWCurve(self.params.a, self.params.b, self.params.p)
        else:
            raise ValueError("Unknown curve type.")
        self.base_point = self.curve.create_point(self.params.g_x, self.params.g_y)

    def _hash(self, m: str) -> int:
        message_len = self.params.n.bit_length()
        if message_len <= 256:
            return int(hashlib.sha256(bytes(m, "utf-8")).hexdigest(), 16)
        elif message_len <= 384:
            return int(hashlib.sha384(bytes(m, "utf-8")).hexdigest(), 16)
        else:
            return int(hashlib.sha512(bytes(m, "utf-8")).hexdigest(), 16)

    def generate_key_pair(self) -> KeyPair:
        d = SystemRandom().randrange(1, self.params.n)
        Q = self.curve.scalar_mult(self.base_point, d, W, to_affine=True)
        return KeyPair(Q.to_affine(), d)

    def sign(self, m: str, priv_key: int) -> Signature:
        h = self._hash(m)
        r, s = 0, 0
        while int(r) == 0:
            k = SystemRandom().randrange(1, self.params.n)
            P = self.curve.scalar_mult(self.base_point, k, W, to_affine=True)
            r = P[0]
        while int(s) == 0:
            s = ((h + priv_key * r) * modular_inverse(k, self.params.n)) % self.params.n
        return Signature(r, s)

    def verify(self, m: str, signature: Signature, pub_key: AffinePoint) -> bool:
        h = self._hash(m)
        r, s = signature.r, signature.s
        if r <= 1 or r > self.params.n or s <= 1 or s > self.params.n:
            return False
        c = modular_inverse(signature.s, self.params.n)
        u, v = (h * c) % self.params.n, (signature.r * c) % self.params.n
        P = self.curve.add(
            self.curve.scalar_mult(self.base_point, u, W),
            self.curve.scalar_mult(pub_key, v, W),
        )
        if isinstance(P, Infinity):
            return False
        return P.to_affine()[0] % self.params.n == r
