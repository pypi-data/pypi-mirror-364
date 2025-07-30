from unittest import mock
import random
import future_uuid
import uuid


def test_uuid6():
    u = future_uuid.uuid6()
    assert u.variant == future_uuid.uuid.RFC_4122
    assert u.version == 6

    fake_nanoseconds = 0x1571_20A1_DE1A_C533
    fake_node_value = 0x54E1_ACF6_DA7F
    fake_clock_seq = 0x14C5
    with (
        mock.patch.object(future_uuid, "_last_timestamp_v6", None),
        mock.patch.object(uuid, "getnode", return_value=fake_node_value),
        mock.patch("time.time_ns", return_value=fake_nanoseconds),
        mock.patch("random.getrandbits", return_value=fake_clock_seq),
    ):
        u = future_uuid.uuid6()
        assert u.variant == future_uuid.uuid.RFC_4122
        assert u.version == 6

        # 32 (top) | 16 (mid) | 12 (low) == 60 (timestamp)
        assert u.time == 0x1E901FCA_7A55_B92
        assert u.fields[0] == 0x1E901FCA  # 32 top bits of time
        assert u.fields[1] == 0x7A55  # 16 mid bits of time
        # 4 bits of version + 12 low bits of time
        assert (u.fields[2] >> 12) & 0xF == 6
        assert (u.fields[2] & 0xFFF) == 0xB92
        # 2 bits of variant + 6 high bits of clock_seq
        assert (u.fields[3] >> 6) & 0xF == 2
        assert u.fields[3] & 0x3F == fake_clock_seq >> 8
        # 8 low bits of clock_seq
        assert u.fields[4] == fake_clock_seq & 0xFF
        assert u.fields[5] == fake_node_value


def test_uuid6_uniqueness():
    # Test that UUIDv6-generated values are unique.

    # Unlike UUIDv8, only 62 bits can be randomized for UUIDv6.
    # In practice, however, it remains unlikely to generate two
    # identical UUIDs for the same 60-bit timestamp if neither
    # the node ID nor the clock sequence is specified.
    uuids = {future_uuid.uuid6() for _ in range(1000)}
    assert len(uuids) == 1000
    versions = {u.version for u in uuids}
    assert versions == {6}

    timestamp = 0x1EC9414C_232A_B00
    fake_nanoseconds = (timestamp - 0x1B21DD21_3814_000) * 100

    with mock.patch("time.time_ns", return_value=fake_nanoseconds):

        def gen():
            with mock.patch.object(future_uuid, "_last_timestamp_v6", None):
                return future_uuid.uuid6(node=0, clock_seq=None)

        # By the birthday paradox, sampling N = 1024 UUIDs with identical
        # node IDs and timestamps results in duplicates with probability
        # close to 1 (not having a duplicate happens with probability of
        # order 1E-15) since only the 14-bit clock sequence is randomized.
        N = 1024
        uuids = {gen() for _ in range(N)}
        assert {u.node for u in uuids} == {0}
        assert {u.time for u in uuids} == {timestamp}
        assert len(uuids) < N, "collision property does not hold"


def test_uuid6_node():
    # Make sure the given node ID appears in the UUID.
    #
    # Note: when no node ID is specified, the same logic as for UUIDv1
    # is applied to UUIDv6. In particular, there is no need to test that
    # getnode() correctly returns positive integers of exactly 48 bits
    # since this is done in test_uuid1_eui64().
    assert future_uuid.uuid6().node.bit_length() <= 48

    assert future_uuid.uuid6(0).node == 0

    # tests with explicit values
    max_node = 0xFFFF_FFFF_FFFF
    assert future_uuid.uuid6(max_node).node == max_node
    big_node = 0xE_1234_5678_ABCD  # 52-bit node
    res_node = 0x0_1234_5678_ABCD  # truncated to 48 bits
    assert future_uuid.uuid6(big_node).node == res_node

    # randomized tests
    for _ in range(10):
        # node with > 48 bits is truncated
        for b in [24, 48, 72]:
            node = (1 << (b - 1)) | random.getrandbits(b)
            assert node.bit_length() == b
            u = future_uuid.uuid6(node=node)
            assert u.node == node & 0xFFFF_FFFF_FFFF


def test_uuid6_clock_seq():
    # Make sure the supplied clock sequence appears in the UUID.
    #
    # For UUIDv6, clock sequence bits are stored from bit 48 to bit 62,
    # with the convention that the least significant bit is bit 0 and
    # the most significant bit is bit 127.
    def get_clock_seq(u):
        return (u.int >> 48) & 0x3FFF

    u = future_uuid.uuid6()
    assert get_clock_seq(u).bit_length() <= 14

    # tests with explicit values
    big_clock_seq = 0xFFFF  # 16-bit clock sequence
    res_clock_seq = 0x3FFF  # truncated to 14 bits
    u = future_uuid.uuid6(clock_seq=big_clock_seq)
    assert get_clock_seq(u) == res_clock_seq

    # some randomized tests
    for _ in range(10):
        # clock_seq with > 14 bits is truncated
        for b in [7, 14, 28]:
            node = random.getrandbits(48)
            clock_seq = (1 << (b - 1)) | random.getrandbits(b)
            assert clock_seq.bit_length() == b
            u = future_uuid.uuid6(node=node, clock_seq=clock_seq)
            assert get_clock_seq(u) == clock_seq & 0x3FFF


def test_uuid6_test_vectors():
    # https://www.rfc-editor.org/rfc/rfc9562#name-test-vectors
    # (separators are put at the 12th and 28th bits)
    timestamp = 0x1EC9414C_232A_B00
    fake_nanoseconds = (timestamp - 0x1B21DD21_3814_000) * 100
    # https://www.rfc-editor.org/rfc/rfc9562#name-example-of-a-uuidv6-value
    node = 0x9F6BDECED846
    clock_seq = (3 << 12) | 0x3C8

    with (
        mock.patch.object(future_uuid, "_last_timestamp_v6", None),
        mock.patch("time.time_ns", return_value=fake_nanoseconds),
    ):
        u = future_uuid.uuid6(node=node, clock_seq=clock_seq)
        assert str(u).upper() == "1EC9414C-232A-6B00-B3C8-9F6BDECED846"
        #   32          16      4      12       2      14         48
        # time_hi | time_mid | ver | time_lo | var | clock_seq | node
        assert u.time == timestamp
        assert u.int & 0xFFFF_FFFF_FFFF == node
        assert (u.int >> 48) & 0x3FFF == clock_seq
        assert (u.int >> 62) & 0x3 == 0b10
        assert (u.int >> 64) & 0xFFF == 0xB00
        assert (u.int >> 76) & 0xF == 0x6
        assert (u.int >> 80) & 0xFFFF == 0x232A
        assert (u.int >> 96) & 0xFFFF_FFFF == 0x1EC9_414C
