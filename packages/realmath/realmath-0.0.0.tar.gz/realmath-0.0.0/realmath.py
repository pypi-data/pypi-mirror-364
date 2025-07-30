"""
real math V.1
Library by Benyamin Ghaem
Reach me on IG: @benionclouds
"""

import math

def rond(x):
    """
    Rounds numbers smartly:
    - If integer (no decimal part), rounds to nearest scaled number (e.g., 5 -> 10, 150 -> 200)
    - If decimal part exists, rounds normally (e.g., 5.5 -> 6, 150.1 -> 150)

    Examples:
        rond(5) -> 10
        rond(150) -> 200
        rond(5.5) -> 6
        rond(150.1) -> 150
        rond(-5) -> -10
        rond(-5.7) -> -6
    """
    if x == int(x):
        abs_x = abs(int(x))
        if abs_x < 10:
            factor = 10
        else:
            digits = int(math.log10(abs_x))
            factor = 10 ** digits

        return round(x / factor) * factor
    else:
        return int(x + 0.5) if x >= 0 else int(x - 0.5)


def rond_down(x):
    """
    Always round down to the nearest integer (like math.floor, but simpler).

    Examples:
        rond_down(2.9) -> 2
        rond_down(-2.1) -> -3
    """
    return int(x) if x >= 0 or x == int(x) else int(x) - 1


def rond_to(x, step=1):
    """
    Round a number to the nearest multiple of `step`.

    Examples:
        rond_to(7.3, 0.5) -> 7.5
        rond_to(7.3, 2) -> 8
    """
    return round(x / step) * step


def clamp(x, min_value, max_value):
    """
    Clamp a number within the range [min_value, max_value].

    Examples:
        clamp(10, 0, 5) -> 5
        clamp(-1, 0, 5) -> 0
        clamp(3, 0, 5) -> 3
    """
    return max(min(x, max_value), min_value)


# ----------- new safe math functions -----------

def almost_equal(a, b, epsilon=1e-9):
    """
    Compare two floating point numbers for approximate equality.

    Args:
        a (float): First number.
        b (float): Second number.
        epsilon (float): Tolerance level (default: 1e-9).

    Returns:
        bool: True if numbers are approximately equal within epsilon, else False.

    Examples:
        almost_equal(0.1 + 0.2, 0.3) -> True
        almost_equal(0.1 + 0.2, 0.3000001) -> False
    """
    return abs(a - b) < epsilon


def rlog(x, default=None):
    """
    Compute the natural logarithm of x safely.

    Args:
        x (float): Input number.
        default: Value to return if log is undefined (x <= 0).

    Returns:
        float or default: Natural log of x or default if undefined.

    Examples:
        rlog(10) -> 2.302585092994046
        rlog(-5, default=0) -> 0
    """
    try:
        return math.log(x)
    except ValueError:
        return default


def rexp(x, default=float('inf')):
    """
    Compute exponential of x safely.

    Args:
        x (float): Exponent.
        default: Value to return if overflow occurs.

    Returns:
        float: e^x or default if overflow.

    Examples:
        rexp(10) -> 22026.465794806718
        rexp(1000) -> inf (or default)
    """
    try:
        return math.exp(x)
    except OverflowError:
        return default


def rdiv(a, b, default=None):
    """
    Divide a by b safely.

    Args:
        a (float): Numerator.
        b (float): Denominator.
        default: Value to return if division by zero occurs.

    Returns:
        float or default: a/b or default if division by zero.

    Examples:
        rdiv(10, 2) -> 5.0
        rdiv(10, 0, default=float('inf')) -> inf
    """
    try:
        return a / b
    except ZeroDivisionError:
        return default


def rsqrt(x, default=None):
    """
    Compute square root safely, supports negative numbers using complex results.

    Args:
        x (float): Input number.
        default: Value to return if input is invalid and no complex support.

    Returns:
        float or complex or default: sqrt(x) or default.

    Examples:
        rsqrt(9) -> 3.0
        rsqrt(-1) -> 1j
    """
    if x >= 0:
        return math.sqrt(x)
    else:
        try:
            import cmath
            return cmath.sqrt(x)
        except ImportError:
            return default
