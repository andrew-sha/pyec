import math
import random
import typing as t


class Residue:
    """
    Represents the modular residue a (mod m) and implements the
    basic arithmetic operations and comparisons for this type.
    """

    def __init__(self, a: int, m: int) -> None:
        """
        Initializes a residue with the given value and modulus. The given
        value will be automatically converted to a value between 0 and the
        given modulus.

        Parameters:
            a (int): The value of the residue
            m (int): The modulus of the residue

        Returns:
            None
        """
        self.a = a if (a < m and a >= 0) else a % m
        self.m = m

    def _compare_moduli(self, other: "Residue") -> None:
        """
        Verifies that a given residue can be compared/combined
        with another one by checking that the two share a modulus.

        Parameters:
            other (Residue): The residue to compare with this one

        Returns:
            None

        Raises:
            ValueError: If the two residues do not share the same
            modulus, i.e. if the two residues cannot be compared
        """
        if self.m != other.m:
            raise ValueError("Residues must share the same modulus.")

    def __repr__(self) -> str:
        return str(self.a)

    def __add__(self, other: "Residue") -> "Residue":
        self._compare_moduli(other)
        return Residue(self.a + other.a, self.m)

    def __sub__(self, other: "Residue") -> "Residue":
        self._compare_moduli(other)
        return Residue(self.a - other.a, self.m)

    def __mul__(self, other: "Residue") -> "Residue":
        self._compare_moduli(other)
        return Residue(self.a * other.a, self.m)

    def __truediv__(self, other: "Residue") -> "Residue":
        self._compare_moduli(other)
        return self * Residue(modular_inverse(other.a, self.m), self.m)

    def __pow__(self, n: int) -> "Residue":
        return Residue(self.a**n, self.m)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(f"{other} is not a residue.")
        self._compare_moduli(other)
        return self.a == other.a

    def __neg__(self) -> "Residue":
        return Residue(-self.a, self.m)

    def __hash__(self) -> int:
        return hash((self.a, self.m))

    def __int__(self) -> int:
        return self.a


class FiniteField:
    """
    Represents a finite field of odd, prime order
    """

    def __init__(self, p: int) -> None:
        """
        Initializes a finite field instance of the given order

        Parameters:
            p (int): The order of finite field

        Returns:
            None

        Raises:
            ValueError: If the given order is not an odd prime
        """
        if not (miller_rabin(p) and p != 2):
            raise ValueError("Invalid field parameter.")
        self.p = p

    def __repr__(self) -> str:
        return f"GF({self.p})"

    def __contains__(self, res: Residue) -> bool:
        """
        Checks whether a given residue is an element of the finite field.

        Parameters:
            res (Residue): The residue to check membership for

        Returns:
            bool: True if the residue is in the field, False if not.
        """
        return res.m == self.p

    def __len__(self) -> int:
        return self.p

    class FiniteFieldIterator(t.Iterator[Residue]):
        """
        Implements the __iter__ and __next__ methods to enable
        in-order iteration through instances of FiniteField
        """

        def __init__(self, p: int) -> None:
            self.p = p
            self.current_value = 0

        def __iter__(self) -> t.Iterator[Residue]:
            return self

        def __next__(self) -> "Residue":
            if self.current_value < self.p:
                residue = Residue(self.current_value, self.p)
                self.current_value += 1
                return residue
            else:
                raise StopIteration

    def __iter__(self) -> "FiniteFieldIterator":
        return self.FiniteFieldIterator(self.p)


def miller_rabin(n: int, k: int = 5) -> bool:
    """
    Performs the Miller-Rabin primality test to determine (with high probability)
    if the given integer is prime.

    Parameters:
        n (int): The integer to test for primality
        k (int): The number of trials of the test, note that more trials guarantees
        a lower probability of false positives

    Returns:
        bool: True if the integer is prime (or composite with probability 1/4^k),
        False otherwise.
    """
    if n in (2, 3):
        return True
    if n <= 1 or n % 2 == 0:
        return False

    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        if pow(a, d, n) != 1:
            for i in range(s):
                if pow(a, (2**i) * d, n) == n - 1:
                    break
            else:
                return False

    return True


def extended_euclidean(a: int, b: int) -> t.Tuple[int, int, int]:
    """
    Computes the greatest common divisor (gcd) and Bézout coefficients for the
    two given integers using the extended Euclidean algorithm

    Parameters:
        a (int): The first input to the extended Euclidean algorithm
        b (int): The second input to the extended Euclidean algorithm

    Returns:
        Tuple[int, int, int]: A triplet (x, y, z) such that x = ay + bz

    Raises:
        ValueError: if a = b = 0, as the greatest common divisor of 0 and 0
        is undefined
    """
    if not (a and b):
        if not (a or b):
            raise ValueError("gcd(0, 0) is not defined")
        return (a or b, 0 if b else 1, 0 if a else 1)

    r_old, r = a, b
    s_old, s = 1, 0
    t_old, t = 0, 1

    while r:
        q = r_old // r
        r_old, r = r, r_old - (q * r)
        s_old, s = s, s_old - (q * s)
        t_old, t = t, t_old - (q * t)

    return (r_old, s_old, t_old)


def modular_inverse(a: int, m: int) -> int:
    """
    Computes the multiplicative inverse of some value given a modulus
    using the extended Euclidean algorithm

    Parameters:
        a (int): The value to find the modular multiplicative inverse of
        m (int): The modulus

    Returns:
        int: An integer b such that ab = 1 (mod m)

    Raises:
        ValueError: If the given value has no multiplicative inverse in the given modulus
    """
    if not extended_euclidean(a, m)[0] == 1:
        raise ValueError(f"{a} has no multiplicative inverse modulo {m}.")
    else:
        return extended_euclidean(a, m)[1] % m


def to_binary(n: int) -> t.List[int]:
    """
    Returns the bit representation of a given integer

    Parameters:
        n (int): The integer to convert to binary

    Returns:
        List: A list containing only 0 or 1 representing the
        binary form of the given integer with the most significant
        bit on the left
    """
    if not n:
        return [0]
    bits: t.List[int] = []
    n = abs(n)
    while n:
        bits.insert(0, n % 2)
        n = n // 2
    return bits


def to_naf(n: int) -> t.List[int]:
    """
    Returns the ternary non-adjacent form representation of a given integer

    Parameters:
        n (int): The integer to convert to ternary non-adjacent form

    Returns:
        List: A list containing only -1, 0 or 1 representing the
        ternary non-adjacent form of the given integer with the most significant
        bit on the left
    """
    if not n:
        return [0]
    naf: t.List[int] = []
    while n:
        if n % 2:
            z = 2 - (n % 4)
            naf.insert(0, z)
            n -= z
        else:
            naf.insert(0, 0)
        n = n // 2

    return naf
