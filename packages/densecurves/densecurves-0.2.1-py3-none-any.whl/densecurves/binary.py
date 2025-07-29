# ENCODE #######################################################################

def encode(number: int, width: int) -> str:
    return format(number, 'b').zfill(width)[:width] # truncated at width

# DECODE #######################################################################

def decode(number: str) -> int:
    return int(number, 2)

# SHAPING ######################################################################

def interleave(number: int, order: int, rank: int) -> list:
    __bits = encode(number, width=rank * order)
    return [int(__bits[__i::rank] or '0', 2) for __i in range(rank)]

def flatten(coords: list, order: int, rank: int) -> int:
    __coords = [encode(__c, width=order) for __c in coords]
    return int(''.join([__y[__i] for __i in range(order) for __y in __coords]) or '0' , 2)
