from typing import Dict, NewType
from struct import pack
import json
import os

'''Load imu commands'''
abs_path = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.join(abs_path, 'config')
data_path = os.path.join(config_dir, 'data_commands.json')
resp_path = os.path.join(config_dir, 'response_commands.json')

with (open(data_path) as data_file, open(resp_path) as resp_file):
    DATA_CMDS = json.load(data_file)
    RESP_CMDS = json.load(resp_file)

'''Define defaults'''
DEFAULT_DATA_CMDS = {key: value for key, value in DATA_CMDS.items()
                     if key in ["button state", "gyroscope", "accelerometer", "magnetometer norm", "temperature C"]}
DEFAULT_RESP_CMDS = {key: value for key, value in RESP_CMDS.items()
                     if key in ["success bit", "timestamp", "data length"]}

'''On time commands'''
SET_RESP_HEAD = 221
SET_SLOT = 80  # TODO: Find a way to make command format consistent
EMPTY_SLOT = 255
# TODO: Look into a Creation design pattern for this

CmdType = NewType('CmdType', Dict[str, Dict[str, str | int]])


class BuildCommands:
    """Class to compile IMU commands"""

    def __init__(self,
                 max_slots: int = 8,
                 data_cmds: CmdType = DEFAULT_DATA_CMDS,
                 resp_cmds: CmdType = DEFAULT_RESP_CMDS):

        self._max_slots = max_slots  # at the time of writing this code, yost lab IMUs only
        # take 8 streaming slots
        self.data_cmds = data_cmds
        self.resp_cmds = resp_cmds

        # TODO: Throw value error if response header is not in resp_cmds

        '''Define length of response header'''
        self._resp_num_bytes = sum([cmd["raw length"] for _, cmd in resp_cmds.items()])

        '''Define number of bytes from IMU's returned data'''
        data_num_bytes = sum([cmd['raw length'] for _, cmd in data_cmds.items()])  # TODO: Think about using calcsize
        self._total_num_bytes = data_num_bytes + self._resp_num_bytes

        # self._command_names = list(resp_cmds.keys()) + list(data_cmds.keys())

    @staticmethod
    def _check_cmd_input(user_cmds: CmdType, default_cmds: CmdType, msg: str):
        for _, cmd in user_cmds.items():
            if cmd not in default_cmds.values():
                raise ValueError(msg)

    @property
    def resp_cmds(self) -> CmdType:
        return self._resp_cmds

    @resp_cmds.setter
    def resp_cmds(self, user_cmds: CmdType):
        self._check_cmd_input(user_cmds, RESP_CMDS, "Response header command does not exist")
        self._resp_cmds = user_cmds

    @property
    def data_cmds(self) -> CmdType:
        return self._data_cmds
    
    @data_cmds.setter
    def data_cmds(self, user_cmds: CmdType):
        self._check_cmd_input(user_cmds, DATA_CMDS, "IMU data command does not exist")

        '''Check if too many commands are set'''
        if len(user_cmds) > self._max_slots:
            raise ValueError("Too many commands are set")
        self._data_cmds = user_cmds

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
        int_cmd = sum([cmd["command"] for _, cmd in self._resp_cmds.items()])
        return pack('B', SET_RESP_HEAD) + pack('>I', int_cmd)

    def pack_data_cmds(self) -> bytes:
        """Pack hex commands into bytes to send to IMU
        Returns:
            bytes: hex commands packed into bytes
        """

        cmd_len = len(self._data_cmds)  # length of data command slots
        n_empty = (self._max_slots - cmd_len)  # number of empty slots 

        '''compile pack characters'''
        pack_chars = (self._max_slots + 1) * 'B'  # set whole pack to binary (add one for set slot cmd)

        '''compile hex commands'''
        # Set slot, list of data commands, fill remainder with empty slots
        hex_cmds = [SET_SLOT] + [cmd["command"] for _, cmd in self._data_cmds.items()] + (n_empty * [EMPTY_SLOT])

        return pack(pack_chars, *hex_cmds)
