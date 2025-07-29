from typing import Any


class _Secret:
    def __init__(self) -> None:
        self._idx = 0
        self._secret = []

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._idx += 1
        return self._secret[self._idx - 1]

    def extend(self, other):
        self._secret.append(other)

    def pop(self, other):
        self._idx = max(0, self._idx - other)


Secret = _Secret()


def _1():
    _0x1a = lambda x: __import__("math").tan(x) ** 2 * 0.000001  # noqa: E731
    _0x2b = lambda y: (y ^ 42) * 0.00001  # noqa: E731
    num = (
        __import__("base64").b64decode("MQ==").decode()
        + chr(46)
        + "".join(
            [
                __import__("base64").b64decode("MDQy").decode(),
                __import__("base64").b64decode("MDY5").decode(),
            ]
        )
    )
    __0x3c = lambda z: "".join(chr((ord(c) ^ 3) + 2) for c in z)  # noqa: E731
    return float(num) - _0x1a(__import__("math").pi / 4) - _0x2b(0x2A) + 1e-6


Secret.extend(_1())
