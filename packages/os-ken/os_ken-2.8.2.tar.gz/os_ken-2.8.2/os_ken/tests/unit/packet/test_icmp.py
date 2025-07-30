# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import inspect
import logging
import struct
import unittest

from os_ken.lib.packet import icmp
from os_ken.lib.packet import packet_utils


LOG = logging.getLogger(__name__)


class Test_icmp(unittest.TestCase):

    echo_id = None
    echo_seq = None
    echo_data = None

    unreach_mtu = None
    unreach_data = None
    unreach_data_len = None

    te_data = None
    te_data_len = None

    def setUp(self):
        self.type_ = icmp.ICMP_ECHO_REQUEST
        self.code = 0
        self.csum = 0
        self.data = b''

        self.ic = icmp.icmp(self.type_, self.code, self.csum, self.data)

        self.buf = bytearray(struct.pack(
            icmp.icmp._PACK_STR, self.type_, self.code, self.csum))
        self.csum_calc = packet_utils.checksum(self.buf)
        struct.pack_into('!H', self.buf, 2, self.csum_calc)

    def setUp_with_echo(self):
        self.echo_id = 13379
        self.echo_seq = 1
        self.echo_data = b'\x30\x0e\x09\x00\x00\x00\x00\x00' \
            + b'\x10\x11\x12\x13\x14\x15\x16\x17' \
            + b'\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f' \
            + b'\x20\x21\x22\x23\x24\x25\x26\x27' \
            + b'\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f' \
            + b'\x30\x31\x32\x33\x34\x35\x36\x37'
        self.data = icmp.echo(
            id_=self.echo_id, seq=self.echo_seq, data=self.echo_data)

        self.type_ = icmp.ICMP_ECHO_REQUEST
        self.code = 0
        self.ic = icmp.icmp(self.type_, self.code, self.csum, self.data)

        self.buf = bytearray(struct.pack(
            icmp.icmp._PACK_STR, self.type_, self.code, self.csum))
        self.buf += self.data.serialize()
        self.csum_calc = packet_utils.checksum(self.buf)
        struct.pack_into('!H', self.buf, 2, self.csum_calc)

    def setUp_with_dest_unreach(self):
        self.unreach_mtu = 10
        self.unreach_data = b'abc'
        self.unreach_data_len = len(self.unreach_data)
        self.data = icmp.dest_unreach(
            data_len=self.unreach_data_len, mtu=self.unreach_mtu,
            data=self.unreach_data)

        self.type_ = icmp.ICMP_DEST_UNREACH
        self.code = icmp.ICMP_HOST_UNREACH_CODE
        self.ic = icmp.icmp(self.type_, self.code, self.csum, self.data)

        self.buf = bytearray(struct.pack(
            icmp.icmp._PACK_STR, self.type_, self.code, self.csum))
        self.buf += self.data.serialize()
        self.csum_calc = packet_utils.checksum(self.buf)
        struct.pack_into('!H', self.buf, 2, self.csum_calc)

    def setUp_with_TimeExceeded(self):
        self.te_data = b'abc'
        self.te_data_len = len(self.te_data)
        self.data = icmp.TimeExceeded(
            data_len=self.te_data_len, data=self.te_data)

        self.type_ = icmp.ICMP_TIME_EXCEEDED
        self.code = 0
        self.ic = icmp.icmp(self.type_, self.code, self.csum, self.data)

        self.buf = bytearray(struct.pack(
            icmp.icmp._PACK_STR, self.type_, self.code, self.csum))
        self.buf += self.data.serialize()
        self.csum_calc = packet_utils.checksum(self.buf)
        struct.pack_into('!H', self.buf, 2, self.csum_calc)

    def test_init(self):
        self.assertEqual(self.type_, self.ic.type)
        self.assertEqual(self.code, self.ic.code)
        self.assertEqual(self.csum, self.ic.csum)
        self.assertEqual(str(self.data), str(self.ic.data))

    def test_init_with_echo(self):
        self.setUp_with_echo()
        self.test_init()

    def test_init_with_dest_unreach(self):
        self.setUp_with_dest_unreach()
        self.test_init()

    def test_init_with_TimeExceeded(self):
        self.setUp_with_TimeExceeded()
        self.test_init()

    def test_parser(self):
        _res = icmp.icmp.parser(bytes(self.buf))
        if type(_res) is tuple:
            res = _res[0]
        else:
            res = _res

        self.assertEqual(self.type_, res.type)
        self.assertEqual(self.code, res.code)
        self.assertEqual(self.csum_calc, res.csum)
        self.assertEqual(str(self.data), str(res.data))

    def test_parser_with_echo(self):
        self.setUp_with_echo()
        self.test_parser()

    def test_parser_with_dest_unreach(self):
        self.setUp_with_dest_unreach()
        self.test_parser()

    def test_parser_with_TimeExceeded(self):
        self.setUp_with_TimeExceeded()
        self.test_parser()

    def test_serialize(self):
        data = bytearray()
        prev = None
        buf = self.ic.serialize(data, prev)

        res = struct.unpack_from(icmp.icmp._PACK_STR, bytes(buf))

        self.assertEqual(self.type_, res[0])
        self.assertEqual(self.code, res[1])
        self.assertEqual(self.csum_calc, res[2])

    def test_serialize_with_echo(self):
        self.setUp_with_echo()
        self.test_serialize()

        data = bytearray()
        prev = None
        buf = self.ic.serialize(data, prev)
        echo = icmp.echo.parser(bytes(buf), icmp.icmp._MIN_LEN)
        self.assertEqual(repr(self.data), repr(echo))

    def test_serialize_with_dest_unreach(self):
        self.setUp_with_dest_unreach()
        self.test_serialize()

        data = bytearray()
        prev = None
        buf = self.ic.serialize(data, prev)
        unreach = icmp.dest_unreach.parser(bytes(buf), icmp.icmp._MIN_LEN)
        self.assertEqual(repr(self.data), repr(unreach))

    def test_serialize_with_TimeExceeded(self):
        self.setUp_with_TimeExceeded()
        self.test_serialize()

        data = bytearray()
        prev = None
        buf = self.ic.serialize(data, prev)
        te = icmp.TimeExceeded.parser(bytes(buf), icmp.icmp._MIN_LEN)
        self.assertEqual(repr(self.data), repr(te))

    def test_to_string(self):
        icmp_values = {'type': repr(self.type_),
                       'code': repr(self.code),
                       'csum': repr(self.csum),
                       'data': repr(self.data)}
        _ic_str = ','.join(['%s=%s' % (k, icmp_values[k])
                            for k, v in inspect.getmembers(self.ic)
                            if k in icmp_values])
        ic_str = '%s(%s)' % (icmp.icmp.__name__, _ic_str)

        self.assertEqual(str(self.ic), ic_str)
        self.assertEqual(repr(self.ic), ic_str)

    def test_to_string_with_echo(self):
        self.setUp_with_echo()
        self.test_to_string()

    def test_to_string_with_dest_unreach(self):
        self.setUp_with_dest_unreach()
        self.test_to_string()

    def test_to_string_with_TimeExceeded(self):
        self.setUp_with_TimeExceeded()
        self.test_to_string()

    def test_default_args(self):
        ic = icmp.icmp()
        buf = ic.serialize(bytearray(), None)
        res = struct.unpack(icmp.icmp._PACK_STR, bytes(buf[:4]))

        self.assertEqual(res[0], 8)
        self.assertEqual(res[1], 0)
        self.assertEqual(buf[4:], b'\x00\x00\x00\x00')

        # with data
        ic = icmp.icmp(type_=icmp.ICMP_DEST_UNREACH, data=icmp.dest_unreach())
        buf = ic.serialize(bytearray(), None)
        res = struct.unpack(icmp.icmp._PACK_STR, bytes(buf[:4]))

        self.assertEqual(res[0], 3)
        self.assertEqual(res[1], 0)
        self.assertEqual(buf[4:], b'\x00\x00\x00\x00')

    def test_json(self):
        jsondict = self.ic.to_jsondict()
        ic = icmp.icmp.from_jsondict(jsondict['icmp'])
        self.assertEqual(str(self.ic), str(ic))

    def test_json_with_echo(self):
        self.setUp_with_echo()
        self.test_json()

    def test_json_with_dest_unreach(self):
        self.setUp_with_dest_unreach()
        self.test_json()

    def test_json_with_TimeExceeded(self):
        self.setUp_with_TimeExceeded()
        self.test_json()


class Test_echo(unittest.TestCase):

    def setUp(self):
        self.id_ = 13379
        self.seq = 1
        self.data = b'\x30\x0e\x09\x00\x00\x00\x00\x00' \
            + b'\x10\x11\x12\x13\x14\x15\x16\x17' \
            + b'\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f' \
            + b'\x20\x21\x22\x23\x24\x25\x26\x27' \
            + b'\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f' \
            + b'\x30\x31\x32\x33\x34\x35\x36\x37'
        self.echo = icmp.echo(
            self.id_, self.seq, self.data)
        self.buf = struct.pack('!HH', self.id_, self.seq)
        self.buf += self.data

    def test_init(self):
        self.assertEqual(self.id_, self.echo.id)
        self.assertEqual(self.seq, self.echo.seq)
        self.assertEqual(self.data, self.echo.data)

    def test_parser(self):
        _res = icmp.echo.parser(self.buf, 0)
        if type(_res) is tuple:
            res = _res[0]
        else:
            res = _res
        self.assertEqual(self.id_, res.id)
        self.assertEqual(self.seq, res.seq)
        self.assertEqual(self.data, res.data)

    def test_serialize(self):
        buf = self.echo.serialize()
        res = struct.unpack_from('!HH', bytes(buf))
        self.assertEqual(self.id_, res[0])
        self.assertEqual(self.seq, res[1])
        self.assertEqual(self.data, buf[struct.calcsize('!HH'):])

    def test_default_args(self):
        ec = icmp.echo()
        buf = ec.serialize()
        res = struct.unpack(icmp.echo._PACK_STR, bytes(buf))

        self.assertEqual(res[0], 0)
        self.assertEqual(res[1], 0)


class Test_dest_unreach(unittest.TestCase):

    def setUp(self):
        self.mtu = 10
        self.data = b'abc'
        self.data_len = len(self.data)
        self.dest_unreach = icmp.dest_unreach(
            data_len=self.data_len, mtu=self.mtu, data=self.data)
        self.buf = struct.pack('!xBH', self.data_len, self.mtu)
        self.buf += self.data

    def test_init(self):
        self.assertEqual(self.data_len, self.dest_unreach.data_len)
        self.assertEqual(self.mtu, self.dest_unreach.mtu)
        self.assertEqual(self.data, self.dest_unreach.data)

    def test_parser(self):
        _res = icmp.dest_unreach.parser(self.buf, 0)
        if type(_res) is tuple:
            res = _res[0]
        else:
            res = _res
        self.assertEqual(self.data_len, res.data_len)
        self.assertEqual(self.mtu, res.mtu)
        self.assertEqual(self.data, res.data)

    def test_serialize(self):
        buf = self.dest_unreach.serialize()
        res = struct.unpack_from('!xBH', bytes(buf))
        self.assertEqual(self.data_len, res[0])
        self.assertEqual(self.mtu, res[1])
        self.assertEqual(self.data, buf[struct.calcsize('!xBH'):])

    def test_default_args(self):
        du = icmp.dest_unreach()
        buf = du.serialize()
        res = struct.unpack(icmp.dest_unreach._PACK_STR, bytes(buf))

        self.assertEqual(res[0], 0)
        self.assertEqual(res[1], 0)


class Test_TimeExceeded(unittest.TestCase):

    def setUp(self):
        self.data = b'abc'
        self.data_len = len(self.data)
        self.te = icmp.TimeExceeded(
            data_len=self.data_len, data=self.data)
        self.buf = struct.pack('!xBxx', self.data_len)
        self.buf += self.data

    def test_init(self):
        self.assertEqual(self.data_len, self.te.data_len)
        self.assertEqual(self.data, self.te.data)

    def test_parser(self):
        _res = icmp.TimeExceeded.parser(self.buf, 0)
        if type(_res) is tuple:
            res = _res[0]
        else:
            res = _res
        self.assertEqual(self.data_len, res.data_len)
        self.assertEqual(self.data, res.data)

    def test_serialize(self):
        buf = self.te.serialize()
        res = struct.unpack_from('!xBxx', bytes(buf))
        self.assertEqual(self.data_len, res[0])
        self.assertEqual(self.data, buf[struct.calcsize('!xBxx'):])

    def test_default_args(self):
        te = icmp.TimeExceeded()
        buf = te.serialize()
        res = struct.unpack(icmp.TimeExceeded._PACK_STR, bytes(buf))

        self.assertEqual(res[0], 0)
