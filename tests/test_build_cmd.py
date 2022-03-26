import unittest
from struct import pack

from iotools.build_cmd import BuildCommands, DATA_CMDS, RESP_CMDS, SET_RESP_HEAD


class BuildCmdTests(unittest.TestCase):

    def test_all_responses(self):
        self.assertEqual(pack('B', SET_RESP_HEAD) + pack('>I', 127),
                         BuildCommands(resp_cmds=RESP_CMDS).pack_response_header())

    def test_invalid_response(self):
        resp_cmd = {'fake response': {"command": 900,
                                      "unpack": ">3f",
                                      "raw length": 12}
                    }
        with self.assertRaises(ValueError):
            BuildCommands(resp_cmds=resp_cmd)

    def test_fill_all_streaming_slots_with_commands(self):
        eight_cmds = {key: value for idx, (key, value) in enumerate(DATA_CMDS.items()) if idx < 8}
        hex_cmds = [80] + [cmd["command"] for _, cmd in eight_cmds.items()]
        self.assertEqual(BuildCommands(data_cmds=eight_cmds).pack_data_cmds(),
                          pack('BBBBBBBBB', *hex_cmds)
                          )

    def test_invalid_data_command(self):
        data_cmd = {'fake sensor': {"command": 1020,
                                    "unpack": ">3h",
                                    "return length": 8,
                                    "raw length": 15}
                    }
        with self.assertRaises(ValueError):
            BuildCommands(data_cmds=data_cmd)

    def test_too_many_streaming_slots(self):
        
        with self.assertRaises(ValueError):
            BuildCommands(data_cmds=DATA_CMDS)


if __name__ == '__main__':
    unittest.main()