from typing import Iterable
import unittest
from struct import pack
from itertools import islice

from iotools.build_cmd import BuildCommands, DATA_CMDS, RESP_CMDS, SET_RESP_HEAD


class BuildCmdTests(unittest.TestCase):

    def test_all_responses(self):
        self.assertEqual(pack('B', SET_RESP_HEAD) + pack('>I', 127),
                         BuildCommands(resp_cmds=RESP_CMDS).pack_response_header())

    def test_invalid_response(self):
        data_cmd = {'fake sensor': {"command": 900,
                                    "pack": "C",
                                    "unpack": ">3f",
                                    "return length": 10,
                                    "raw length": 12}
                    }
        with self.assertRaises(ValueError):
            BuildCommands(data_cmds=data_cmd)

    def test_fill_all_slots(self):
        eight_cmds = {key: value for idx, (key, value) in enumerate(DATA_CMDS.items()) if idx < 8}
        hex_cmds = [80] + [cmd["command"] for _, cmd in eight_cmds.items()]
        self.assertEquals(BuildCommands(data_cmds=eight_cmds).pack_data_cmds(),
                          pack('BBBBBBBBB', *hex_cmds)
                          )


if __name__ == '__main__':
    unittest.main()