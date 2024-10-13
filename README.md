# pyec

`pyec` supports elliptic curve arithmetic and the elliptic curve digital signature algorithm (ECDSA) in pure-Python. This implementation emphasizes speed over security, and is meant primarily as an educational resource. **Do not
use this ECDSA in production**. In applications where security is critical, refer instead to an industry-grade cryptography library.

## Installation
This library is currently not available on PyPI. To install, clone the repository:
```bash
git clone https://github.com/andrew-sha/pyec.git
cd pyec/
```
Once a copy of the repository exists locally, `pyec` can be imported within a Python script or interactive shell located at the root directory of the local repository. See the following section for more details.
## Usage
### Elliptic curve arithmetic

 The first goal of this library is to provide an intuitive and fast Python interface for elliptic curve arithmetic. In particular, the `pyec.curve` module supports the creation of elliptic curves with arbitrary parameters (in short Weierstrass form), and addition and scalar multiplication of points on these curves:
```python
from pyec.curve import ShortWCurve

# Create a curve in Weierstrass form with coefficients
# a = 3 and b = 8 over the field GF(13)
curve = ShortWCurve(3, 8, 13)

# Get the points (1, 8) and (9, 7) on the curve
point1 = curve.create_point(1, 8)
point2 = curve.create_point(9, 7)

# Compute point1 + point2 and 5 * point1
added = curve.add(point1, point2)
scaled = curve.scalar_mult(point1, 5)

# Returns '(2, 10)' and '(12, 2)'
added.to_affine()
scaled.to_affine()
```
Attempts to instantiate curves with discriminant 0 or curves over fields of non odd, prime order will yield errors. Attempts to generate a point which does not exist on a curve will likewise fail.
```python
from pyec.curve import ShortWCurve

# Raises ValueError as 4 * 2^3 + 27 * 2^2 = 0 (mod 5)
curve = ShortWCurve(2, 2, 5)

# Raises ValueError as 12 is not an odd prime
curve = ShortWCurve(3, 8, 12)

# Raises ValueError since (1, 2) does not satisfy y^2 = x^3 + 2x + 4 (mod 5)
curve = ShortWCurve(2, 4, 5)
curve.create_point(1, 2)
```
The curve's infinity point is represented using the `Infinity` type, and can be directly accessed via the curve instance:
```python
from pyec.curve import ShortWCurve

curve = ShortWCurve(3, 8, 13)

# Get the infinity point
inf = curve.infinity

# Returns '(9, 6)' and 'Infinity'
curve.add(curve.create_point(9, 6), inf, to_affine=True)
curve.scalar_mult(inf, 8)
```
`pyec` can represent elliptic curve points in either Jacobian or Affine coordinates via the `JacobianPoint` or `AffinePoint` types respectively. For performance reasons, points are by default represented using Jacobian coordinates when created and during arithmetic. Passing the `to_affine=True` flag to the arithmetic methods will override this behavior (as demonstrated above), or points can be converted in the following way:
```python
from pyec.curve import ShortWCurve

curve = ShortWCurve(3, 8, 13)
point = curve.scalar_mult(curve.create_point(1, 8), 3)

# Returns the Jacobian form of the point '(3, 7, 10)'
point1

# Returns the Affine form of the point '(9, 6)'
point1.to_affine()
```

### ECDSA
The `pyec.sign` module provides support for ECDSA key generation, signing, and verification using any of the following well-known curves deemed suitable for cryptographic purposes:
- NIST: `P-224, P-256, P-384, P-521`
- Brainpool: `brainpool224r1, brainpool256r1, brainpool384r1, brainpool521r1`
- Other: `secp2561k` ("bitcoin curve")

All operations are wrapped in the `CurveSign` type, which gets initialized with a specific curve. The curve name must match one of the names in the above list.
```python
from pyec.sign import CurveSign

# Initialize CurveSign with curve P-256 and generate key pair
signer = CurveSign("P-256")
key_pair = signer.generate_key_pair()

# Sign message using private key
message = 'hello'
signature = signer.sign(message, key_pair.priv_key)

# Verify signature using public key
assert signer.verify(message, signature, key_pair.pub_key)

# Raises KeyError
signer = CurveSign("uncrackableCurve")
```
To add a new curve, add a new key-value pair to `REGISTRY` in the `curve_params.py` file locally, or see below for contributing.

## Performance
`pyec` leverages several optimizations in order to speed up curve arithmetic. In particular, scalar multiplication is computed via the double-and-add algorithm on the w-ary non-adjacent form of the scalar so as to reduce the number of additions needed in computing the product. In turn, additions are computed on the Jacobian coordinate representation of a point, reducing the number of modular inversions needed.

The following table displays the average length of time in milliseconds this library takes to generate key pairs, signatures, and verifications for each of the supported curves. Times are calculated as averages of 100 iterations of each operation on an Apple M3 Max.
| Curve            | Key gen (ms) | Sign (ms) | Verify (ms) |
|------------------|--------------|-----------|-------------|
| P-224            | 1.8          | 1.8       | 3.5         |
| P-256            | 2.3          | 2.3       | 4.5         |
| P-384            | 5.1          | 5.1       | 10.1        |
| P-521            | 8.7          | 8.9       | 17.6        |
| brainpoolP224r1  | 1.9          | 2         | 3.8         |
| brainpoolP256r1  | 2.5          | 2.5       | 4.9         |
| brainpoolP384r1  | 5.5          | 5.5       | 10.8        |
| brainpoolP512r1  | 9.5          | 9.6       | 18.9        |
| secp256k1        | 2.2          | 2.3       | 4.5         |


See the top-level docstring in the `pyec/benchmark.py` module for more information on how to benchmark this library on your own machine. Note that results are formatted using `tabulate`, which is included as a dev dependency in the `pyproject.toml`.
## Contributing

Pull requests and issues are very much encouraged. Assuming you already have the repository cloned, follow these steps to set up a development environment:

1) Install poetry (if not already installed): `curl -sSL https://install.python-poetry.org | python3 -`
2) Navigate to the project's root directory
2) Install dev dependencies: `poetry install`
3) Activate the poetry shell: `poetry shell`
4) Install the pre-commit hooks: `pre-commit install`


Before submitting a pull request, please ensure that your commit passes all unit tests, linting, and type checks. Note that running `pytest` from the project's root directory within the poetry shell will run all unit tests. Please modify/include unit tests when appropriate.

## License

[MIT](https://www.mit.edu/~amini/LICENSE.md)
