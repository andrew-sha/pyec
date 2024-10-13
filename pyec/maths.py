import random
import typing as t


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

    def __contains__(self, res: int) -> bool:
        """
        Checks whether a given integer is an element of the finite field.

        Parameters:
            res (int): The integer to check membership for

        Returns:
            bool: True if the integer is in the field, False if not.
        """
        return res >= 0 and res < self.p

    def __len__(self) -> int:
        return self.p

    class FiniteFieldIterator(t.Iterator[int]):
        """
        Implements the __iter__ and __next__ methods to enable
        in-order iteration through instances of FiniteField
        """

        def __init__(self, p: int) -> None:
            self.p = p
            self.current_value = 0

        def __iter__(self) -> t.Iterator[int]:
            return self

        def __next__(self) -> int:
            if self.current_value < self.p:
                val = self.current_value
                self.current_value += 1
                return val
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
    bezout_coefs = extended_euclidean(a, m)
    if not bezout_coefs[0] == 1:
        raise ValueError(f"{a} has no multiplicative inverse modulo {m}.")
    else:
        return bezout_coefs[1] % m


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


def to_naf(n: int, w: int = 2) -> t.List[int]:
    """
    Returns the w-ary non-adjacent representation of a given integer

    Parameters:
        n (int): The integer to convert
        w (int): Determines the range of allowable non-zero values in the non-adjacent form

    Returns:
        List: A list of integers in the w-ary non-adjacent form with the least significant bit on the left
    """
    if not n:
        return [0]

    def mods(a: int, b: int) -> int:
        if (a % b) >= b // 2:
            return (a % b) - b
        else:
            return a % b

    naf: t.List[int] = []
    while n:
        if n % 2:
            z = mods(n, 2**w)
            naf.append(z)
            n -= z
        else:
            naf.append(0)
        n = n // 2

    return naf
