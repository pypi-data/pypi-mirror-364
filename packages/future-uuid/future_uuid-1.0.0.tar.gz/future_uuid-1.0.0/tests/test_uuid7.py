from unittest import mock
import future_uuid
import random
import os


def test_uuid7():
    u = future_uuid.uuid7()
    assert u.variant == future_uuid.uuid.RFC_4122
    assert u.version == 7

    # 1 Jan 2023 12:34:56.123_456_789
    timestamp_ns = 1672533296_123_456_789  # ns precision
    timestamp_ms, _ = divmod(timestamp_ns, 1_000_000)

    for _ in range(100):
        counter_hi = random.getrandbits(11)
        counter_lo = random.getrandbits(30)
        counter = (counter_hi << 30) | counter_lo

        tail = random.getrandbits(32)
        # effective number of bits is 32 + 30 + 11 = 73
        random_bits = counter << 32 | tail

        # set all remaining MSB of fake random bits to 1 to ensure that
        # the implementation correctly removes them
        random_bits = (((1 << 7) - 1) << 73) | random_bits
        random_data = random_bits.to_bytes(10, byteorder="big")

        with (
            mock.patch.multiple(
                future_uuid,
                _last_timestamp_v7=None,
                _last_counter_v7=0,
            ),
            mock.patch("time.time_ns", return_value=timestamp_ns),
            mock.patch("os.urandom", return_value=random_data) as urand,
        ):
            u = future_uuid.uuid7()
            urand.assert_called_once_with(10)
            assert u.variant == future_uuid.uuid.RFC_4122
            assert u.version == 7

            assert future_uuid._last_timestamp_v7 == timestamp_ms
            assert future_uuid._last_counter_v7 == counter

            unix_ts_ms = timestamp_ms & 0xFFFF_FFFF_FFFF
            assert (u.int >> 80) & 0xFFFF_FFFF_FFFF == unix_ts_ms

            assert (u.int >> 75) & 1 == 0  # check that the MSB is 0
            assert (u.int >> 64) & 0xFFF == counter_hi
            assert (u.int >> 32) & 0x3FFF_FFFF == counter_lo
            assert u.int & 0xFFFF_FFFF == tail


def test_uuid7_uniqueness():
    # Test that UUIDv7-generated values are unique.
    #
    # While UUIDv8 has an entropy of 122 bits, those 122 bits may not
    # necessarily be sampled from a PRNG. On the other hand, UUIDv7
    # uses os.urandom() as a PRNG which features better randomness.
    N = 1000
    uuids = {future_uuid.uuid7() for _ in range(N)}
    assert len(uuids) == N

    versions = {u.version for u in uuids}
    assert versions == {7}


def test_uuid7_monotonicity():
    us = [future_uuid.uuid7() for _ in range(10_000)]
    assert us == sorted(us)

    with mock.patch.multiple(
        future_uuid,
        _last_timestamp_v7=0,
        _last_counter_v7=0,
    ):
        # 1 Jan 2023 12:34:56.123_456_789
        timestamp_ns = 1672533296_123_456_789  # ns precision
        timestamp_ms, _ = divmod(timestamp_ns, 1_000_000)

        # counter_{hi,lo} are chosen so that "counter + 1" does not overflow
        counter_hi = random.getrandbits(11)
        counter_lo = random.getrandbits(29)
        counter = (counter_hi << 30) | counter_lo
        assert counter + 1 < 0x3FF_FFFF_FFFF

        tail = random.getrandbits(32)
        random_bits = counter << 32 | tail
        random_data = random_bits.to_bytes(10, byteorder="big")

        with (
            mock.patch("time.time_ns", return_value=timestamp_ns),
            mock.patch("os.urandom", return_value=random_data) as urand,
        ):
            u1 = future_uuid.uuid7()
            urand.assert_called_once_with(10)
            assert future_uuid._last_timestamp_v7 == timestamp_ms
            assert future_uuid._last_counter_v7 == counter
            assert (u1.int >> 64) & 0xFFF == counter_hi
            assert (u1.int >> 32) & 0x3FFF_FFFF == counter_lo
            assert u1.int & 0xFFFF_FFFF == tail

        # 1 Jan 2023 12:34:56.123_457_032 (same millisecond but not same ns)
        next_timestamp_ns = 1672533296_123_457_032
        next_timestamp_ms, _ = divmod(timestamp_ns, 1_000_000)
        assert timestamp_ms == next_timestamp_ms

        next_tail_bytes = os.urandom(4)
        next_fail = int.from_bytes(next_tail_bytes, byteorder="big")

        with (
            mock.patch("time.time_ns", return_value=next_timestamp_ns),
            mock.patch("os.urandom", return_value=next_tail_bytes) as urand,
        ):
            u2 = future_uuid.uuid7()
            urand.assert_called_once_with(4)
            # same milli-second
            assert future_uuid._last_timestamp_v7 == timestamp_ms
            # 42-bit counter advanced by 1
            assert future_uuid._last_counter_v7 == counter + 1
            assert (u2.int >> 64) & 0xFFF == counter_hi
            assert (u2.int >> 32) & 0x3FFF_FFFF == counter_lo + 1
            assert u2.int & 0xFFFF_FFFF == next_fail

        assert u1 < u2


def test_uuid7_timestamp_backwards():
    # 1 Jan 2023 12:34:56.123_456_789
    timestamp_ns = 1672533296_123_456_789  # ns precision
    timestamp_ms, _ = divmod(timestamp_ns, 1_000_000)
    fake_last_timestamp_v7 = timestamp_ms + 1

    # counter_{hi,lo} are chosen so that "counter + 1" does not overflow
    counter_hi = random.getrandbits(11)
    counter_lo = random.getrandbits(29)
    counter = (counter_hi << 30) | counter_lo
    assert counter + 1 < 0x3FF_FFFF_FFFF

    tail_bytes = os.urandom(4)
    tail = int.from_bytes(tail_bytes, byteorder="big")

    with (
        mock.patch.multiple(
            future_uuid,
            _last_timestamp_v7=fake_last_timestamp_v7,
            _last_counter_v7=counter,
        ),
        mock.patch("time.time_ns", return_value=timestamp_ns),
        mock.patch("os.urandom", return_value=tail_bytes) as urand,
    ):
        u = future_uuid.uuid7()
        urand.assert_called_once_with(4)
        assert u.variant == future_uuid.uuid.RFC_4122
        assert u.version == 7
        assert future_uuid._last_timestamp_v7 == fake_last_timestamp_v7 + 1
        unix_ts_ms = (fake_last_timestamp_v7 + 1) & 0xFFFF_FFFF_FFFF
        assert (u.int >> 80) & 0xFFFF_FFFF_FFFF == unix_ts_ms
        # 42-bit counter advanced by 1
        assert future_uuid._last_counter_v7 == counter + 1
        assert (u.int >> 64) & 0xFFF == counter_hi
        # 42-bit counter advanced by 1 (counter_hi is untouched)
        assert (u.int >> 32) & 0x3FFF_FFFF == counter_lo + 1
        assert u.int & 0xFFFF_FFFF == tail


def test_uuid7_overflow_counter():
    # 1 Jan 2023 12:34:56.123_456_789
    timestamp_ns = 1672533296_123_456_789  # ns precision
    timestamp_ms, _ = divmod(timestamp_ns, 1_000_000)

    new_counter_hi = random.getrandbits(11)
    new_counter_lo = random.getrandbits(30)
    new_counter = (new_counter_hi << 30) | new_counter_lo

    tail = random.getrandbits(32)
    random_bits = (new_counter << 32) | tail
    random_data = random_bits.to_bytes(10, byteorder="big")

    with (
        mock.patch.multiple(
            future_uuid,
            _last_timestamp_v7=timestamp_ms,
            # same timestamp, but force an overflow on the counter
            _last_counter_v7=0x3FF_FFFF_FFFF,
        ),
        mock.patch("time.time_ns", return_value=timestamp_ns),
        mock.patch("os.urandom", return_value=random_data) as urand,
    ):
        u = future_uuid.uuid7()
        urand.assert_called_with(10)
        assert u.variant == future_uuid.uuid.RFC_4122
        assert u.version == 7
        # timestamp advanced due to overflow
        assert future_uuid._last_timestamp_v7 == timestamp_ms + 1
        unix_ts_ms = (timestamp_ms + 1) & 0xFFFF_FFFF_FFFF
        assert (u.int >> 80) & 0xFFFF_FFFF_FFFF == unix_ts_ms
        # counter overflowed, so we picked a new one
        assert future_uuid._last_counter_v7 == new_counter
        assert (u.int >> 64) & 0xFFF == new_counter_hi
        assert (u.int >> 32) & 0x3FFF_FFFF == new_counter_lo
        assert u.int & 0xFFFF_FFFF == tail
