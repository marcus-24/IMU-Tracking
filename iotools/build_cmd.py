from typing import Dict
import struct
import json
import os

'''Load imu commands'''
config_dir = os.path.join('iotools', 'config')
data_path = os.path.join(config_dir, 'data_commands.json')
resp_path = os.path.join(config_dir, 'response_commands.json')

with (open(data_path) as data_file, open(resp_path) as resp_file):
    DATA_COMMANDS = json.load(data_file)
    RESPONSE_COMMANDS = json.load(resp_file)

'''Define defaults'''
DEFAULT_DATA_COMMANDS = {key: value for key, value in DATA_COMMANDS.items() if key != "empty slot"}
DEFAULT_RESP_COMMANDS = {key: value for key, value in RESPONSE_COMMANDS.items() if key in ["success bit", "timestamp", "data length"]}

# TODO: Look into a Creation design pattern for this


class BuildCommands:
    """Class to compile commands
    """

    def __init__(self,
                 data_commands: Dict[str, Dict[str, str | int]] = DEFAULT_DATA_COMMANDS,
                 resp_commands: Dict[str, Dict[str, str | int]] = DEFAULT_RESP_COMMANDS,
                 max_slots: int = 9):

        # Why I used default factory
        # https://www.micahsmith.com/blog/2020/01/dataclasses-mutable-defaults/
        # https://stackoverflow.com/questions/52063759/passing-default-list-argument-to-dataclasses

        self._data_commands = data_commands
        self._resp_commands = resp_commands
        self._max_slots = max_slots  # at the time of writing this code, yost lab IMUs only take 8 streaming slots + 1 for set slot command

        '''Define number of bytes from IMU's returned data'''
        self._num_bytes = sum([cmd["data length"] for _, cmd in data_commands.items()]
                              + [cmd["data length"] for _, cmd in resp_commands.items()])

    @property
    def num_bytes(self) -> int:
        return self._num_bytes

    @staticmethod
    def _hex_to_int(cmd: str) -> int:
        return int(cmd, 16)

    def pack_response_header(self) -> bytes:
        """_summary_

        Returns:
            bytes: _description_

        """
        int_cmd = sum([self._hex_to_int(cmd["command"]) for _, cmd in self._resp_commands.items()])
        return struct.pack('B', 0xDD) + struct.pack('>I', int_cmd)

    def pack_data_commands(self) -> bytes:
        """Pack hex commands into bytes to send to IMU
        Returns:
            bytes: hex commands packed into bytes
        """

        cmd_len = len(self._data_commands)  # length of data command slots
        n_empty = (self._max_slots - cmd_len)  # number of empty slots

        '''compile pack characters'''
        pack_chars = ''.join([cmd["pack"] for _, cmd in self._data_commands.items()])
        pack_chars += ''.join(n_empty * [DATA_COMMANDS["empty slot"]["pack"]])  # add empty slots if not all were used

        '''compile hex commands'''
        hex_cmds = [self._hex_to_int(cmd["command"]) for _, cmd in self._data_commands.items()]
        hex_cmds += n_empty * [self._hex_to_int(DATA_COMMANDS["empty slot"]["command"])]  # add empty slots if not all were used

        return struct.pack(pack_chars, *hex_cmds)

