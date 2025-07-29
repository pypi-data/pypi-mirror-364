import functools

# ENCODE #######################################################################

def encode(number: int) -> int:
    return number ^ (number >> 1)

# DECODE #######################################################################

def decode(number: int) -> int:
    return functools.reduce(
        lambda __a, __b: __a ^ __b,
        [number >> __i for __i in range(len(format(number, 'b')))])
