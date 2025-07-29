"""Map a flat dimension with points of rank N, according to the Z-order curve."""

import densecurves.binary
import densecurves.linear

# 1D => 2D #####################################################################

def _point(position: int, order: int, rank: int) -> list:
    return densecurves.binary.interleave(position, order=order, rank=rank)

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
    return densecurves.binary.flatten(coords, order=order, rank=rank)

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
