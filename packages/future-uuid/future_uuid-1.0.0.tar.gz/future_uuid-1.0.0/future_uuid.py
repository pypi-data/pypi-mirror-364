import uuid
import os

_last_timestamp_v7 = None
_last_counter_v7 = 0  # 42-bit counter

_RFC_4122_VERSION_6_FLAGS = (6 << 76) | (0x8000 << 48)
_RFC_4122_VERSION_7_FLAGS = (7 << 76) | (0x8000 << 48)
_RFC_4122_VERSION_8_FLAGS = (8 << 76) | (0x8000 << 48)

_UINT_128_MAX = (1 << 128) - 1


def _uuid7_get_counter_and_tail():
    rand = int.from_bytes(os.urandom(10), byteorder="big")
    # 42-bit counter with MSB set to 0
    counter = (rand >> 32) & 0x1FF_FFFF_FFFF
    # 32-bit random data
    tail = rand & 0xFFFF_FFFF
    return counter, tail


class UUID(uuid.UUID):
    @property
    def time(self):
        if self.version == 6:
            # time_hi (32) | time_mid (16) | ver (4) | time_lo (12) | ... (64)
            time_hi = self.int >> 96
            time_lo = (self.int >> 64) & 0x0FFF
            return time_hi << 28 | (self.time_mid << 12) | time_lo
        else:
            # time_lo (32) | time_mid (16) | ver (4) | time_hi (12) | ... (64)
            return super().time


def _uuid_from_int(value):
    """Create a UUID from an integer *value*. Internal use only."""
    assert 0 <= value <= _UINT_128_MAX, repr(value)
    self = object.__new__(UUID)
    object.__setattr__(self, "int", value)
    object.__setattr__(self, "is_safe", uuid.SafeUUID.unknown)
    return self


def uuid7():
    """Generate a UUID from a Unix timestamp in milliseconds and random bits.

    UUIDv7 objects feature monotonicity within a millisecond.
    """
    # --- 48 ---   -- 4 --   --- 12 ---   -- 2 --   --- 30 ---   - 32 -
    # unix_ts_ms | version | counter_hi | variant | counter_lo | random
    #
    # 'counter = counter_hi | counter_lo' is a 42-bit counter constructed
    # with Method 1 of RFC 9562, §6.2, and its MSB is set to 0.
    #
    # 'random' is a 32-bit random value regenerated for every new UUID.
    #
    # If multiple UUIDs are generated within the same millisecond, the LSB
    # of 'counter' is incremented by 1. When overflowing, the timestamp is
    # advanced and the counter is reset to a random 42-bit integer with MSB
    # set to 0.

    global _last_timestamp_v7
    global _last_counter_v7

    import time

    nanoseconds = time.time_ns()
    timestamp_ms = nanoseconds // 1_000_000

    if _last_timestamp_v7 is None or timestamp_ms > _last_timestamp_v7:
        counter, tail = _uuid7_get_counter_and_tail()
    else:
        if timestamp_ms < _last_timestamp_v7:
            timestamp_ms = _last_timestamp_v7 + 1
        # advance the 42-bit counter
        counter = _last_counter_v7 + 1
        if counter > 0x3FF_FFFF_FFFF:
            # advance the 48-bit timestamp
            timestamp_ms += 1
            counter, tail = _uuid7_get_counter_and_tail()
        else:
            # 32-bit random data
            tail = int.from_bytes(os.urandom(4), byteorder="big")

    unix_ts_ms = timestamp_ms & 0xFFFF_FFFF_FFFF
    counter_msbs = counter >> 30
    # keep 12 counter's MSBs and clear variant bits
    counter_hi = counter_msbs & 0x0FFF
    # keep 30 counter's LSBs and clear version bits
    counter_lo = counter & 0x3FFF_FFFF
    # ensure that the tail is always a 32-bit integer (by construction,
    # it is already the case, but future interfaces may allow the user
    # to specify the random tail)
    tail &= 0xFFFF_FFFF

    int_uuid_7 = unix_ts_ms << 80
    int_uuid_7 |= counter_hi << 64
    int_uuid_7 |= counter_lo << 32
    int_uuid_7 |= tail
    # by construction, the variant and version bits are already cleared
    int_uuid_7 |= _RFC_4122_VERSION_7_FLAGS
    res = _uuid_from_int(int_uuid_7)

    # defer global update until all computations are done
    _last_timestamp_v7 = timestamp_ms
    _last_counter_v7 = counter
    return res


_last_timestamp_v6 = None


def uuid6(node=None, clock_seq=None):
    """Similar to :func:`uuid1` but where fields are ordered differently
    for improved DB locality.

    More precisely, given a 60-bit timestamp value as specified for UUIDv1,
    for UUIDv6 the first 48 most significant bits are stored first, followed
    by the 4-bit version (same position), followed by the remaining 12 bits
    of the original 60-bit timestamp.
    """
    global _last_timestamp_v6
    import time

    nanoseconds = time.time_ns()
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = nanoseconds // 100 + 0x01B21DD213814000
    if _last_timestamp_v6 is not None and timestamp <= _last_timestamp_v6:
        timestamp = _last_timestamp_v6 + 1
    _last_timestamp_v6 = timestamp
    if clock_seq is None:
        import random

        clock_seq = random.getrandbits(14)  # instead of stable storage
    time_hi_and_mid = (timestamp >> 12) & 0xFFFF_FFFF_FFFF
    time_lo = timestamp & 0x0FFF  # keep 12 bits and clear version bits
    clock_s = clock_seq & 0x3FFF  # keep 14 bits and clear variant bits
    if node is None:
        node = uuid.getnode()
    # --- 32 + 16 ---   -- 4 --   -- 12 --  -- 2 --   -- 14 ---    48
    # time_hi_and_mid | version | time_lo | variant | clock_seq | node
    int_uuid_6 = time_hi_and_mid << 80
    int_uuid_6 |= time_lo << 64
    int_uuid_6 |= clock_s << 48
    int_uuid_6 |= node & 0xFFFF_FFFF_FFFF
    # by construction, the variant and version bits are already cleared
    int_uuid_6 |= _RFC_4122_VERSION_6_FLAGS
    return _uuid_from_int(int_uuid_6)


def uuid8(a=None, b=None, c=None):
    """Generate a UUID from three custom blocks.

    * 'a' is the first 48-bit chunk of the UUID (octets 0-5);
    * 'b' is the mid 12-bit chunk (octets 6-7);
    * 'c' is the last 62-bit chunk (octets 8-15).

    When a value is not specified, a pseudo-random value is generated.
    """
    if a is None:
        import random

        a = random.getrandbits(48)
    if b is None:
        import random

        b = random.getrandbits(12)
    if c is None:
        import random

        c = random.getrandbits(62)
    int_uuid_8 = (a & 0xFFFF_FFFF_FFFF) << 80
    int_uuid_8 |= (b & 0xFFF) << 64
    int_uuid_8 |= c & 0x3FFF_FFFF_FFFF_FFFF
    # by construction, the variant and version bits are already cleared
    int_uuid_8 |= _RFC_4122_VERSION_8_FLAGS
    return _uuid_from_int(int_uuid_8)
