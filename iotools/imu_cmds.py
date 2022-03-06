from collections import namedtuple
from dataclasses import dataclass, field
from typing import List
import struct

# %% List of slot commands
'''Build sensor command tuple'''
SensorCommand = namedtuple('SensorCommand', ['command', 'pack', 'unpack', 'num_bytes'])

'''List of sensor commands'''
set_slot = SensorCommand(0x50, 'B', None, 0)  # set streaming slots
button_state = SensorCommand(0xfa, 'B', None, 1)  # read when button is pressed or released
gyro = SensorCommand(0x26, 'B', '>3f', 12)  # xyz gyroscope readings (rad/s)
acc = SensorCommand(0x27, 'B', '>3f', 12)  # xyz accelerometer (g)
mag_norm = SensorCommand(0x23, 'B', '>3f', 12)  # xyz normalized magnetometer
temp_C = SensorCommand(0x2B, 'B', '>3f', 4)  # sensor temperature (celsius)
empty_slot = SensorCommand(0xff, 'B', None, 0)  # need an empty slot in case all slots are not filled in stream

# %% Class to build commands


@dataclass
class BuildCommands:
    """Class to compile commands
    """
    # Why I used default factory
    # https://www.micahsmith.com/blog/2020/01/dataclasses-mutable-defaults/
    # https://stackoverflow.com/questions/52063759/passing-default-list-argument-to-dataclasses
    _commands: List[SensorCommand] = field(default_factory=lambda: [set_slot, button_state, gyro, acc, mag_norm, temp_C])
    max_slots: int = 9  # at the time of writing this code, yost lab IMUs only take 8 streaming slots + 1 for set slot command

    def __post_init__(self):
        
        '''Define number of bytes from IMU's returned data'''
        # TODO: Number of bytes is dependant on response header (page 22)
        checksum_len = 1
        timing_len = 4  # 
        data_len = 1
        self._num_bytes = sum([cmds.num_bytes for cmds in self._commands]) + checksum_len + timing_len + data_len

        '''Fill in any unused slots with empty command'''
        self._commands.extend([empty_slot for _ in range(self.max_slots - len(self._commands))])

    @property
    def num_bytes(self) -> int:
        return self._num_bytes

    @property
    def commands(self) -> List[SensorCommand]:
        return self._commands

    def pack_commands(self) -> bytes:
        """Back hex commands into bytes to send to IMU
        Returns:
            bytes: hex commands packed into bytes
        """

        pack_chars = ''.join([cmds.pack for cmds in self._commands])
        hex_cmds = [cmds.command for cmds in self._commands]

        return struct.pack(pack_chars, *hex_cmds)