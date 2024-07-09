"""benchmark.py

The purpose of this module is to benchmark the speed of this implementation of
elliptic curve arithmetic by returning the average time it takes to generate a
key pair, signature, and verification for each of the curves defined in curve_params.py.

Run the module using `python -m pyec.benchmark` and the average time (in milliseconds) for
each major operation in ECDSA for each curve will be printed to the console using the
`tabulate` package.

Global variables PRECISION and TRIALS can be changed to modify experimental parameters.
"""

import statistics
import time
import typing as t

from tabulate import tabulate

from pyec.curve_params import REGISTRY
from pyec.point import AffinePoint
from pyec.sign import CurveSign, Signature

PRECISION: int = 4
TRIALS: int = 100


def benchmark_key_generation(signer: CurveSign, trials: int = TRIALS) -> float:
    times = []
    for _ in range(trials):
        start = time.time()
        signer.generate_key_pair()
        end = time.time()
        times.append(end - start)
    return round(statistics.fmean(times), PRECISION) * 10**3


def benchmark_sign(
    message: str, priv_key: int, signer: CurveSign, trials: int = TRIALS
) -> float:
    times = []
    for _ in range(trials):
        start = time.time()
        signature = signer.sign(message, priv_key)
        end = time.time()
        times.append(end - start)
    return round(statistics.fmean(times), PRECISION) * 10**3


def benchmark_verify(
    message: str,
    signature: Signature,
    pub_key: AffinePoint,
    signer: CurveSign,
    trials: int = TRIALS,
) -> float:
    times = []
    for _ in range(trials):
        start = time.time()
        assert signer.verify(message, signature, pub_key)
        end = time.time()
        times.append(end - start)
    return round(statistics.fmean(times), PRECISION) * 10**3


if __name__ == "__main__":
    results = []
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    for c in REGISTRY:
        signer = CurveSign(c)
        key_gen_time = benchmark_key_generation(signer)

        key_pair = signer.generate_key_pair()
        priv_key, pub_key = key_pair.priv_key, key_pair.pub_key
        signature = signer.sign(message, priv_key)

        sign_time = benchmark_sign(message, priv_key, signer)
        verify_time = benchmark_verify(message, signature, pub_key, signer)
        results.append([c, key_gen_time, sign_time, verify_time])

    headers = ["Curve", "Key gen (ms)", "Sign (ms)", "Verify (ms)"]
    print(tabulate(results, headers=headers))
