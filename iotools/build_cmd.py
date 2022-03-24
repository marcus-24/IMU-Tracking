from typing import Dict
from struct import pack, calcsize
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
DEFAULT_RESP_COMMANDS = {key: value for key, value in RESPONSE_COMMANDS.items()
                         if key in ["success bit", "timestamp", "data length"]}

'''On time commands'''
SET_RESP_HEAD = 221
SET_SLOT = 80  # TODO: Find a way to make command format consistent
EMPTY_SLOT = 255
# TODO: Look into a Creation design pattern for this


class BuildCommands:
    """Class to compile IMU commands"""

    def __init__(self,
                 data_commands: Dict[str, Dict[str, str | int]] = DEFAULT_DATA_COMMANDS,
                 resp_commands: Dict[str, Dict[str, str | int]] = DEFAULT_RESP_COMMANDS,
                 max_slots: int = 9):

        self._data_commands = data_commands
        self._resp_commands = resp_commands
        self._max_slots = max_slots  # at the time of writing this code, yost lab IMUs only
        # take 8 streaming slots + 1 for set slot command

    # TODO: Throw value error if response header is not in resp_commands

        '''Define length of response header'''
        self._resp_num_bytes = sum([cmd["raw length"] for _, cmd in resp_commands.items()])

        '''Define number of bytes from IMU's returned data'''
        data_num_bytes = sum([cmd['raw length'] for _, cmd in data_commands.items()]) # TODO: Think about using calcsize
        self._total_num_bytes = data_num_bytes + self._resp_num_bytes

    @property
    def resp_commands(self) -> Dict[str, Dict[str, str | int]]:
        return self._resp_commands

    @property
    def data_commands(self) -> Dict[str, Dict[str, str | int]]:
        return self._data_commands

    @property
    def resp_num_bytes(self) -> int:
        return self._resp_num_bytes

    @property
    def total_num_bytes(self) -> int:
        return self._total_num_bytes

    def pack_response_header(self) -> bytes:
        """Pack response header command into bytes
        Returns:
            bytes: converted response header command
        """
        int_cmd = sum([cmd["command"] for _, cmd in self._resp_commands.items()])
        return pack('B', SET_RESP_HEAD) + pack('>I', int_cmd)

    def pack_data_commands(self) -> bytes:
        """Pack hex commands into bytes to send to IMU
        Returns:
            bytes: hex commands packed into bytes
        """

        cmd_len = len(self._data_commands)  # length of data command slots
        n_empty = (self._max_slots - cmd_len) - 1  # number of empty slots (remove one for set slot command)

        '''compile pack characters'''
        pack_chars = self._max_slots * 'B'  # set whole pack to binary

        '''compile hex commands'''
        # Set slot, list of data commands, fill remainder with empty slots
        hex_cmds = [SET_SLOT] + [cmd["command"] for _, cmd in self._data_commands.items()] + (n_empty * [EMPTY_SLOT])

        return pack(pack_chars, *hex_cmds)
