import typing as t
from abc import ABC, abstractmethod

from pyec.maths import FiniteField, Residue, to_binary, to_naf
from pyec.point import AffinePoint, Infinity, JacobianPoint

CurveElement = t.Union[AffinePoint, JacobianPoint, Infinity]


class Curve(ABC):
    """
    An interface for the elliptic curve type. This abstract
    base class is subclassed by other classes in this module to
    implement an elliptic curve defined according to a given form, such
    as Weierstrass or Montgomery form.

    """

    def __init__(self, a: int, b: int, p: int) -> None:
        """
        Initializes an elliptic curve in either (short) Weierstrass form or
        Montgomery form with the given parameters with coordinates in the field GF(p).

        Parameters:
            a (int): The first coefficient of the curve equation
            b (int): The second coefficient of the curve equation
            p (int): The prime defining the curve's base field

        Returns:
            None

        Raises:
            ValueError: If the given parameters do not form a non-singular
            curve or a finite field
        """
        self.a = Residue(a, p)
        self.b = Residue(b, p)
        self.p = p
        self.base_field = FiniteField(p)
        self._validate_params()

    @abstractmethod
    def _validate_params(self) -> None:
        """
        Checks that the parameters of the curve define a legal, non-singular elliptic curve.

        Parameters:
            None

        Returns:
            None

        Raises:
            ValueError: If for the given type of curve, the following conditions are met:

                Weierstrass curve: 4a^3 + 27b^2 = 0
                Montgomery curve: b(a^2 - 4) = 0
        """
        ...

    @property
    def infinity(self) -> Infinity:
        """
        Returns the curve's infinity point, which acts as the identity element
        of the group.

        Parameters:
            None

        Returns:
            Infinity: An instance of the Infinity type representing the curve's
            infinity point.
        """
        return Infinity()

    @property
    @abstractmethod
    def points(self) -> t.List[CurveElement]:
        """
        Computes the list of all points on the curve.

        **Disclaimer: This method is very inefficient and should only be called
        for small curves. In particular, do not invoke this method on any of the
        NIST/Brainpool curves (i.e. the ones defined in curve_params.py)

        Parameters:
            None

        Returns:
            List: A list of all points, including infinity, on the curve.
        """
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def __contains__(self, P: CurveElement) -> bool:
        """
        Determines if the provided point exists on the curve by checking if the
        point (in Affine form) satisfies the curve equation

        Parameters:
            P (CurveElement): The point to check membership for

        Returns:
            bool: True if the given point is on the curve or if the point is
            the infinity point. False otherwise.
        """
        ...

    @abstractmethod
    def add(
        self, P: CurveElement, Q: CurveElement, to_affine: bool = False
    ) -> CurveElement:
        """
        Computes the sum of two elliptic curve points P and Q.

        Parameters:
            P (CurveElement): The first summand
            Q (CurveElement): The second summand
            to_affine (int): Determine the coordinate system in which to return
            the resulting point, defaults to Jacobian

        Returns:
            CurveElement: The point on the curve R such that R = P + Q
        """
        ...

    @t.overload
    def scalar_mult(
        self, P: CurveElement, n: int, to_affine: t.Literal[True]
    ) -> AffinePoint:
        ...

    @t.overload
    def scalar_mult(
        self, P: CurveElement, n: int, to_affine: t.Literal[False]
    ) -> JacobianPoint:
        ...

    @t.overload
    def scalar_mult(
        self, P: CurveElement, n: int, to_affine: bool = False
    ) -> CurveElement:
        ...

    def scalar_mult(
        self, P: CurveElement, n: int, to_affine: bool = False
    ) -> CurveElement:
        """
        Computes a scalar multiple of the elliptic curve point P using the double-and-add
        algorithm on the ternary non-adjacent form of the scalar.

        Parameters:
            P (CurveElement): The curve point to scale
            n (int): The integer to scale the curve point by
            to_affine (int): Determine the coordinate system in which to return
            the resulting point, defaults to Jacobian

        Returns:
            CurveElement: The point on the curve Q such that Q = nP

        Raises:
            ValueError: If the scalar n is negative (n < 0)
        """
        if n < 0:
            raise ValueError("Power must be non-negative.")
        if isinstance(P, Infinity):
            return P
        bits = to_naf(n)
        Q: CurveElement = P.to_jacobian()
        R: CurveElement = self.infinity

        for bit in reversed(bits):
            if bit == 1:
                R = self.add(R, Q)
            elif bit == -1:
                R = self.add(R, Q.negate())
            Q = self.add(Q, Q)

        return R if not to_affine else R.to_affine()

    def create_point(self, x: int, y: int) -> JacobianPoint:
        """
        Creates an elliptic curve point (represented in Jacobian coordinates) with
        the given coordinates.

        Parameters:
            x (int): The x coordinate of the curve to generate
            y (int): The y coordinate of the curve to generate

        Returns:
            JacobianPoint: A point on the curve in the Jacobian form (x, y, 1)

        Raises:
            ValueError: If the given point (x, y) does not exist on the curve
        """
        x_res, y_res = Residue(x, self.p), Residue(y, self.p)
        point = AffinePoint(x_res, y_res)
        if not point in self:
            raise ValueError("The given point is not on the curve.")
        return point.to_jacobian()


class ShortWCurve(Curve):
    """
    Represents an elliptic curve in (short) Weierstrass form
    given by the equation Y^2 = X^3 + aX + b.
    """

    def _validate_params(self) -> None:
        if ((4 * int(self.a) ** 3) + (27 * int(self.b) ** 2)) % self.p == 0:
            raise ValueError("Discriminant must be non-zero.")

    def __repr__(self) -> str:
        return f"ShortWCurve(a={self.a}, b={self.b}) over {self.base_field}"

    def __contains__(self, P: CurveElement) -> bool:
        if isinstance(P, Infinity):
            return True
        P = P.to_affine()
        return P[1] ** 2 == P[0] ** 3 + self.a * P[0] + self.b

    @property
    def points(self) -> t.List[CurveElement]:
        points: t.Set[CurveElement] = set()
        values: t.Dict[str, t.List[Residue]] = {
            "input": [],
            "lhs": [],
            "rhs": [],
        }
        for res in self.base_field:
            values["input"].append(res)
            values["lhs"].append(res**2)
            values["rhs"].append(res**3 + self.a * res + self.b)
        for i, val in enumerate(values["rhs"]):
            if val in values["lhs"]:
                indices = [j for j, x in enumerate(values["lhs"]) if x == val]
                for j in indices:
                    points.add(AffinePoint(values["input"][i], values["input"][j]))

        points.add(self.infinity)

        return list(points)

    def add(
        self, P: CurveElement, Q: CurveElement, to_affine: bool = False
    ) -> CurveElement:
        if isinstance(P, Infinity):
            return Q if not to_affine else Q.to_affine()
        elif isinstance(Q, Infinity):
            return P if not to_affine else P.to_affine()
        elif P.negate() == Q:
            return self.infinity
        else:
            if P == Q:
                return self._double(P)
            else:
                U, V = P[0] * Q[2] ** 2, Q[0] * P[2] ** 2
                S, T = P[1] * Q[2] ** 3, Q[1] * P[2] ** 3
                if U == V:
                    if S == T:
                        return self._double(P)
                    return self.infinity
                H = V - U
                R = T - S
                H2 = H**2
                H3 = H2 * H
                UH2 = U * H2

                x = R**2 - H3 - (Residue(2, self.p) * UH2)
                y = R * (UH2 - x) - (S * H3)
                z = H * P[2] * Q[2]
                res = JacobianPoint(x, y, z)

                return res if not to_affine else res.to_affine()

    def _double(self, P: CurveElement) -> CurveElement:
        """
        Doubles the elliptic curve point P which can be in either
        Jacobian or Affine coordinates.

        Parameters:
            P (Point): The point to double

        Returns:
            CurveElement: The point on the curve Q such that Q = 2P
        """
        if isinstance(P, Infinity):
            return P
        elif int(P[1]) == 0:
            return self.infinity
        Y2, Z2 = P[1] ** 2, P[2] ** 2
        S = Residue(4, self.p) * P[0] * Y2
        if int(self.a) == (-3 % self.p):
            M = Residue(3, self.p) * (P[0] + Z2) * (P[0] - Z2)
        else:
            M = Residue(3, self.p) * P[0] ** 2 + self.a * Z2**2
        T = M**2 - Residue(2, self.p) * S
        x = T
        y = M * (S - T) - (Residue(8, self.p) * Y2**2)
        z = Residue(2, self.p) * P[1] * P[2]
        return JacobianPoint(x, y, z)


class MontgomeryCurve(Curve):
    """
    Represents an elliptic curve in Montgomery form
    given by the equation bY^2 = X^3 + aX^2 + X.
    """

    def _validate_params(self) -> None:
        if (self.a**2 == Residue(4, self.p)) or (self.b == Residue(0, self.p)):
            raise ValueError("Invalid curve parameters.")

    def __repr__(self) -> str:
        return f"MontgomeryCurve(a={self.a}, b={self.b}) over {self.base_field}"

    def __contains__(self, P: CurveElement) -> bool:
        if isinstance(P, Infinity):
            return True
        P = P.to_affine()
        return self.b * P[1] ** 2 == P[0] ** 3 + self.a * P[0] ** 2 + P[0]

    @property
    def points(self) -> t.List[CurveElement]:
        points: t.Set[CurveElement] = set()
        values: t.Dict[str, t.List[Residue]] = {
            "input": [],
            "lhs": [],
            "rhs": [],
        }
        for res in self.base_field:
            values["input"].append(res)
            values["lhs"].append(self.b * res**2)
            values["rhs"].append(res**3 + self.a * res**2 + res)
        for i, val in enumerate(values["rhs"]):
            if val in values["lhs"]:
                indices = [j for j, x in enumerate(values["lhs"]) if x == val]
                for j in indices:
                    points.add(AffinePoint(values["input"][i], values["input"][j]))

        points.add(self.infinity)

        return list(points)

    def add(
        self, P: CurveElement, Q: CurveElement, to_affine: bool = False
    ) -> CurveElement:
        if not (P in self and Q in self):
            raise ValueError("Both points must be on the curve.")
        elif isinstance(P, Infinity):
            return Q
        elif isinstance(Q, Infinity):
            return P
        elif P.negate() == Q:
            return self.infinity
        else:
            if P == Q:
                l = (
                    Residue(3, self.p) * P[0] ** 2
                    + Residue(2, self.p) * self.a * P[0]
                    + Residue(1, self.p)
                ) / (Residue(2, self.p) * self.b * P[1])
            else:
                l = (Q[1] - P[1]) / (Q[0] - P[0])

            x = self.b * l**2 - self.a - P[0] - Q[0]
            y = l * (P[0] - x) - P[1]
            res = AffinePoint(x, y)

            return res if to_affine else res.to_jacobian()
