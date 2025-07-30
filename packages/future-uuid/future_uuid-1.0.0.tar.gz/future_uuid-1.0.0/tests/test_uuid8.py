import random
from itertools import product
import future_uuid


def test_uuid8():
    u = future_uuid.uuid8()

    assert u.variant == future_uuid.uuid.RFC_4122
    assert u.version == 8

    for _, hi, mid, lo in product(
        range(10),  # repeat 10 times
        [None, 0, random.getrandbits(48)],
        [None, 0, random.getrandbits(12)],
        [None, 0, random.getrandbits(62)],
    ):
        u = future_uuid.uuid8(hi, mid, lo)
        assert u.variant == future_uuid.uuid.RFC_4122
        assert u.version == 8
        if hi is not None:
            assert (u.int >> 80) & 0xFFFFFFFFFFFF == hi
        if mid is not None:
            assert (u.int >> 64) & 0xFFF == mid
        if lo is not None:
            assert u.int & 0x3FFFFFFFFFFFFFFF == lo


def test_uuid8_uniqueness():
    # Test that UUIDv8-generated values are unique
    # (up to a negligible probability of failure).
    u1 = future_uuid.uuid8()
    u2 = future_uuid.uuid8()
    assert u1.int != u2.int
    assert u1.version == u2.version
