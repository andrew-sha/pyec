import typing as t

from pyec.maths import Residue


class AffinePoint:
    """
    Represents an elliptic curve point in Affine coordinates: (x, y)
    """

    def __init__(self, x: Residue, y: Residue) -> None:
        """
        Initializes a point in Affine coordinates from two modular residues

        Parameters:
            x (Residue): The first coordinate of the point
            y (Residue): The second coordinate of the point

        Returns:
            None

        Raises:
            ValueError: If the two coordinates provided do not share a modulus
        """
        if x.m != y.m:
            raise ValueError("Coordinates must share the same modulus.")
        self.x = x
        self.y = y
        self.m = x.m

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __getitem__(self, index: int) -> Residue:
        """
        Enables 0-indexing of an Affine point

        Parameters:
            index (int): Specifies which coordinate of the point to return, where
            a value of 0 corresponds to the x coordinate and a value of 1 corresponds
            to the y coordinate

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
        return self.__class__(self.x, -self.y)

    def to_affine(self) -> "AffinePoint":
        return self

    def to_jacobian(self) -> "JacobianPoint":
        """
        Converts this point to an equivalent point represented in Jacobian coordinates.
        An Affine point (x, y) is equivalent to the Jacobian point (x, y, 1)

        Parameters:
            None

        Returns:
            JacobianPoint: The point represented in Jacobian coordinates.
        """
        return JacobianPoint(self.x, self.y, Residue(1, self.m))


class JacobianPoint:
    """
    Represents an elliptic curve point in Jacobian coordinates: (x, y, z)
    """

    def __init__(self, x: Residue, y: Residue, z: Residue) -> None:
        """
        Initializes a point in Jacobian coordinates from three modular residues

        Parameters:
            x (Residue): The first coordinate of the point
            y (Residue): The second coordinate of the point
            z (Residue): The third coordinate of the point

        Returns:
            None

        Raises:
            ValueError: If the three coordinates provided do not share a modulus
        """
        if x.m != y.m or x.m != z.m or y.m != z.m:
            raise ValueError("Coordinates must share the same modulus.")
        self.x = x
        self.y = y
        self.z = z
        self.m = x.m

    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __getitem__(self, index: int) -> Residue:
        """
        Enables 0-indexing of a Jacobian point

        Parameters:
            index (int): Specifies which coordinate of the point to return, where
            a value of 0 corresponds to the x coordinate, a value of 1 corresponds
            to the y coordinate, and a value of 2 corresponds to the z coordinate

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
        return self.__class__(self.x, -self.y, self.z)

    def to_affine(self) -> "AffinePoint":
        """
        Converts this point to an equivalent point represented in Affine coordinates.
        A Jacobian point (x, y, z) is equivalent to the Jacobian point (x/z^2, y/z^3)

        Parameters:
            None

        Returns:
            AffinePoint: The point represented in Affine coordinates
        """
        z_inv = Residue(1, self.m) / self.z
        return AffinePoint(self.x * (z_inv**2), self.y * (z_inv**3))

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
