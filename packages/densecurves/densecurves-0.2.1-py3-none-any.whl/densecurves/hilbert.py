"""Map a flat dimension with points of rank N, according to the Hilbert curve."""

import densecurves.binary
import densecurves.gray
import densecurves.linear

# ENTANGLE #####################################################################

def _entangle(coords: list, order: int, rank: int, step: int=1) -> list:
    __coords = list(coords)
    # undo the extra rotations
    for __j in range(1, order)[::-step]:
        # q is a single bit mask and (q - 1) is a string of ones
        __q = 2 ** __j
        for __i in range(0, rank)[::step]:
            # invert the least significant bits
            if __coords[__i] & __q:
                __coords[0] ^= __q - 1
            # exchange the least significant bits
            else:
                __t = (__coords[0] ^ __coords[__i]) & (__q - 1)
                __coords[0] ^= __t
                __coords[__i] ^= __t
    # list of rank coordinates
    return __coords

def entangle(coords: list, order: int, rank: int) -> list:
    return _entangle(coords=coords, order=order, rank=rank, step=1)

def untangle(coords: list, order: int, rank: int) -> list:
    return _entangle(coords=coords, order=order, rank=rank, step=-1)

# 1D => 2D #####################################################################

def _point(position: int, order: int, rank: int) -> list:
    # gray encoding H ^ (H/2)
    __gray = densecurves.gray.encode(position)
    # approximate the curve
    __coords = densecurves.binary.interleave(__gray, order=order, rank=rank)
    # Undo excess work
    return untangle(__coords, order=order, rank=rank)

def point(position: int, order: int, rank: int, group: int=0) -> list:
    # side of the fine blocks
    __block = 1 << group
    # split the index into blocks
    __coarse, __fine = divmod(position, __block ** rank)
    # coarse coordinates, following the Hilbert curve
    __coarse = _point(__coarse, order=order, rank=rank)
    # fine coordinates, inside each block
    __fine = densecurves.linear.point(__fine, base=__block, rank=rank)
    # combine both coordinates systems
    return [__c * __block + __f for __c, __f in zip(__coarse, __fine)]

# 2D => 1D #####################################################################

def _index(coords: list, order: int, rank: int) -> int:
    # entangle the positions back
    __coords = entangle(coords, order=order, rank=rank)
    # flatten the coordinate
    __position = densecurves.binary.flatten(__coords, order=order, rank=rank)
    # decode the gray encodings
    return densecurves.gray.decode(__position)

def index(coords: list, order: int, rank: int, group: int=0) -> int:
    # side of the fine blocks
    __block = 1 << group
    # split the coordinates
    __coarse, __fine = list(zip(*[divmod(__c, __block) for __c in coords]))
    # coarse index, on the curve
    __coarse = _index(__coarse, order=order, rank=rank)
    # fine index, inside the block
    __fine = densecurves.linear.index(__fine, base=__block, rank=rank)
    # combine the indexes
    return __fine + __coarse * (__block ** rank)
