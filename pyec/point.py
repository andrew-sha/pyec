import typing as t

from pyec.maths import miller_rabin, modular_inverse


class AffinePoint:
    """
    Represents an elliptic curve point in Affine coordinates: (x (mod m), y (mod m))
    """

    def __init__(self, x: int, y: int, m: int) -> None:
        """
        Initializes a point in Affine coordinates from two integers

        Parameters:
            x (int): The first coordinate of the point
            y (int): The second coordinate of the point
            m (int): The modulus of the coordinates

        Returns:
            None
        """
        self.x = x % m
        self.y = y % m
        self.m = m

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __getitem__(self, index: int) -> int:
        """
        Enables 0-indexing of an Affine point

        Parameters:
            index (int): Specifies which coordinate of the point to return

        Returns:
            int: The coordinate corresponding to the given index

        Raises:
            IndexError: If the given index is neither 0 or 1
        """
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of range. Affine points have two coordinates.")

    def __eq__(self, other: t.Any) -> bool:
        """
        Enables comparisons between instances of an Affine point and other curve point types

        Parameters:
            other (Any): The object to compare to this point

        Returns:
            bool: True if this and the compared point represent the same point, False if not

        Raises:
            TypeError: If the compared object does not represent a point (in Affine or Jacobian coordinates or infinity point)
        """
        if isinstance(other, AffinePoint):
            return (self[0] == other[0]) and (self[1] == other[1])
        elif isinstance(other, JacobianPoint):
            return self == other.to_affine()
        elif isinstance(other, Infinity):
            return False
        else:
            raise TypeError(f"{other} is not a point.")

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def negate(self) -> "AffinePoint":
        return self.__class__(self.x, -self.y % self.m, self.m)

    def to_affine(self) -> "AffinePoint":
        return self

    def to_jacobian(self) -> "JacobianPoint":
        """
        Converts this point to an equivalent point represented in Jacobian coordinates.
        An Affine point (x, y) is equivalent to the Jacobian point (x, y, 1).

        Parameters:
            None

        Returns:
            JacobianPoint: The point represented in Jacobian coordinates.
        """
        return JacobianPoint(self.x, self.y, 1, self.m)


class JacobianPoint:
    """
    Represents an elliptic curve point in Jacobian coordinates: (x (mod m), y (mod m), z (mod m))
    """

    def __init__(self, x: int, y: int, z: int, m: int) -> None:
        """
        Initializes a point in Jacobian coordinates from three integers

        Parameters:
            x (int): The first coordinate of the point
            y (int): The second coordinate of the point
            z (int): The third coordinate of the point
            m (int): The modulus of the coordinates

        Returns:
            None
        """
        self.x = x % m
        self.y = y % m
        self.z = z % m
        self.m = m

    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __getitem__(self, index: int) -> int:
        """
        Enables 0-indexing of a Jacobian point

        Parameters:
            index (int): Specifies which coordinate of the point to return, where
            a value of 0 corresponds to the x coordinate, a value of 1 corresponds
            to the y coordinate, and a value of 2 corresponds to the z coordinate

        Returns:
            int: The coordinate corresponding to the given index

        Raises:
            IndexError: If the given index is neither 0, 1, or 2
        """
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError(
                "Index out of range. Jacobian points have three coordinates."
            )

    def __eq__(self, other: t.Any) -> bool:
        """
        Enables comparisons between instances of a Jacobian point and other curve point types

        Parameters:
            other (Any): The object to compare to this point

        Returns:
            bool: True if this and the compared point represent the same point, False if not

        Raises:
            TypeError: If the compared object does not represent a point (in Affine or Jacobian coordinates or infinity point)
        """
        if isinstance(other, JacobianPoint):
            return (
                (self[0] == other[0])
                and (self[1] == other[1])
                and (self[2] == other[2])
            )
        elif isinstance(other, AffinePoint):
            return self == other.to_jacobian()
        elif isinstance(other, Infinity):
            return False
        else:
            raise TypeError(f"{other} is not a point.")

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def negate(self) -> "JacobianPoint":
        return self.__class__(self.x, -self.y % self.m, self.z, self.m)

    def to_affine(self) -> "AffinePoint":
        """
        Converts this point to an equivalent point represented in Affine coordinates.
        A Jacobian point (x, y, z) is equivalent to the Jacobian point (x/z^2, y/z^3).

        Parameters:
            None

        Returns:
            AffinePoint: The point represented in Affine coordinates
        """
        Zinv = modular_inverse(self.z, self.m)
        Zinv2 = Zinv**2
        return AffinePoint(self.x * Zinv2, self.y * (Zinv2 * Zinv), self.m)

    def to_jacobian(self) -> "JacobianPoint":
        return self


class Infinity:
    """
    Represents the infinity point of an elliptic curve
    """

    def __repr__(self) -> str:
        return "Infinity"

    def __eq__(self, other: t.Any) -> bool:
        return isinstance(other, Infinity)

    def negate(self) -> "Infinity":
        return self

    def __hash__(self) -> int:
        return hash(str(self))

    def to_affine(self) -> "Infinity":
        return self

    def to_jacobian(self) -> "Infinity":
        return self
