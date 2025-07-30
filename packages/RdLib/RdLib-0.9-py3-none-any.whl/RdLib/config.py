# config.py
import numpy as np

class Config:
    def __init__(self):
        # If False, the Kalman filter is disabled in all types of measurements.
        # If True, the Kalman filter is enabled in all types of measurements.
        self.Kalman = False

        # Path where graphs from the Kalman test function will be saved.
        self.Kalman_Chart_Path = '~/Documents/Kalman_Test'

        # If False, the program will not save measurements to a CSV file at the path above.
        self.Kalman_Save_csv = False

        # Q matrix for the Kalman filter – adjusts filter responsiveness.
        self.Kalman_Q = np.diag([0.1, 0.1, 0.1, 0.1])

        # R matrix for the Kalman filter – represents measurement noise; higher values mean more trust in predictions than measurements.
        self.Kalman_R = np.diag([50, 50])

        # Path to the Raspberry Pi serial port.
        self.Serial_Port = '/dev/ttyS0'

        # Baud rate for communication with Rd03D and HLK-LD2450 radars.
        self.Serial_Speed = '256000'

        # Communication type: "Serial" or "Gpio" GPIO is not supported in that version
        self.ctype = "Serial"

        # Detection mode: 'S' for single target, 'M' for multiple targets. Multiple targets are not supported in that version
        self.Detection_Mode = 'S' 

        # Distance units: "in", "ft", "m", or "cm"
        self.distance_units = "m"

        # If True, enables more verbose output in the terminal for debugging purposes.
        self.debug = False

    def set(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

config = Config()
