# standard imports
import unittest
from struct import pack

# local imports
from iotools.build_cmd import BuildCommands, DATA_CMDS, RESP_CMDS, SET_RESP_HEAD, SET_SLOT


class BuildCmdTests(unittest.TestCase):

    def setUp(self) -> None:
        self.bldg_cmd = BuildCommands()

    def test_all_responses(self):
        self.bldg_cmd.resp_cmds = RESP_CMDS
        response_cmd_total = 127  # sum of all the response commands
        self.assertEqual(pack('B', SET_RESP_HEAD) + pack('>I', response_cmd_total),
                         self.bldg_cmd.pack_response_header())

    def test_invalid_response(self):
        resp_cmd = {'fake response': {"command": 900,
                                      "unpack": ">3f",
                                      "raw length": 12}
                    }
        
        with self.assertRaises(ValueError):
            self.bldg_cmd.resp_cmds = resp_cmd

    def test_fill_all_streaming_slots_with_commands(self):
        '''Set up data commands'''
        n_cmds = 8  # number of commands to extract
        eight_cmds = {key: value for idx, (key, value) in enumerate(DATA_CMDS.items()) if idx < n_cmds}

        '''Set hex commands'''
        hex_cmds = [SET_SLOT] + [cmd["command"] for _, cmd in eight_cmds.items()]
        self.bldg_cmd.data_cmds = eight_cmds

        self.assertEqual(self.bldg_cmd.pack_data_cmds(),
                         pack('BBBBBBBBB', *hex_cmds))

    def test_invalid_data_command(self):
        data_cmd = {'fake sensor': {"command": 1020,
                                    "unpack": ">3h",
                                    "return length": 8,
                                    "raw length": 15}
                    }
        with self.assertRaises(ValueError):
            self.bldg_cmd.data_cmds = data_cmd

    def test_too_many_streaming_slots(self):
        
        with self.assertRaises(ValueError):
            self.bldg_cmd.data_cmds = DATA_CMDS


if __name__ == '__main__':
    unittest.main()