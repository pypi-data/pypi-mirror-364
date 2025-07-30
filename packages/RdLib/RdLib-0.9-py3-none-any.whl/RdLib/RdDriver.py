import serial
import time
import re
import math
import numpy as np
from .Kalman import Kalman
import os
from .config import config
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import csv

try:
    ser = serial.Serial('/dev/ttyS0', 256000, timeout=1)
except serial.SerialException as e:
    print("Can't open current serial port:", e)
    exit()

buffer_hex = ""
First_Measurement = True
kf = None  # Kalman filter instance

def Initialize(mode: str) -> None:
    """
    Initialize the radar module with the given mode.
    
    Args:
        mode (str): "S" for Single mode or "M" for Multi mode.
    """
    if mode == "S":
        ser.write(bytes([0xFD, 0xFC, 0xFB, 0xFA, 0x02, 0x00, 0x80, 0x00, 0x04, 0x03, 0x02, 0x01]))
    elif mode == "M":
        ser.write(bytes([0xFD, 0xFC, 0xFB, 0xFA, 0x02, 0x00, 0x90, 0x00, 0x04, 0x03, 0x02, 0x01]))

def check_radar_mode(mode: str) -> None:
    """
    Change the radar detection mode if different from the current.
    
    Args:
        mode (str): Desired mode.
    """
    if config.Detection_Mode != mode:
        config.Detection_Mode = mode
        Initialize(mode)

def decode_signed_15bit(lsb: int, msb: int) -> int:
    """
    Decode a signed 15-bit integer from two bytes.
    
    Args:
        lsb (int): Least significant byte.
        msb (int): Most significant byte.
        
    Returns:
        int: Decoded signed integer value.
    """
    raw = lsb + (msb << 8)
    sign = (raw & 0x8000) >> 15
    value = raw & 0x7FFF
    return value if sign == 1 else -value

def get_angle_degrees(x: float, y: float) -> float:
    """
    Calculate the angle in degrees from Cartesian coordinates.
    
    Args:
        x (float): X coordinate.
        y (float): Y coordinate.
        
    Returns:
        float: Angle in degrees.
    """
    angle_rad = math.atan2(y, x)
    return math.degrees(angle_rad)

def Convert_Dist(x: float, y: float) -> float:
    """
    Calculate Euclidean distance from origin to (x, y).
    
    Args:
        x (float): X coordinate.
        y (float): Y coordinate.
        
    Returns:
        float: Distance.
    """
    return math.sqrt(x ** 2 + y ** 2)

def parse_coordinates(frame: str) -> tuple[int | None, int | None]:
    """
    Extract and decode x, y coordinates from the radar data frame.
    
    Args:
        frame (str): Hexadecimal string containing the frame data.
        
    Returns:
        tuple: (x, y) coordinates as signed integers or (None, None) on failure.
    """
    try:
        x_low = int(frame[8:10], 16)
        x_high = int(frame[10:12], 16)
        x = decode_signed_15bit(x_low, x_high)

        y_low = int(frame[12:14], 16)
        y_high = int(frame[14:16], 16)
        y = decode_signed_15bit(y_low, y_high)

        return x, y
    except Exception as e:
        print("Decoding error:", e)
        return None, None

def ReadRadarData() -> tuple[float, float]:
    """
    Reads radar data, applies Kalman filter if enabled,
    and returns coordinates in configured units.

    Returns:
        Tuple of (x, y) coordinates in chosen distance units.
    """
    global buffer_hex, First_Measurement, kf

    start_seq = "aaff0300"
    pattern = re.compile(rf'{start_seq}[0-9a-f]+?55[0-9a-f]{{2}}', re.IGNORECASE)
    max_attempts = 50
    ser.flushInput()

    for _ in range(max_attempts):
        if ser.in_waiting > 0:
            data = ser.read(32)
            buffer_hex += data.hex()

            for match in pattern.finditer(buffer_hex):
                frame = match.group()
                x, y = parse_coordinates(frame)

                if x is not None and y is not None:
                    if config.Kalman:
                        kalman_input = np.array([[x], [y]])
                        if First_Measurement:
                            kf = Kalman(kalman_input)
                            First_Measurement = False
                        else:
                            kf.step(kalman_input)
                            kalman_output = kf.X_k
                            x = float(kalman_output[0, 0])
                            y = float(kalman_output[1, 0])

                    buffer_hex = buffer_hex[match.end():]

                    if config.distance_units == "m":
                        return (x / 100, y / 1000)
                    elif config.distance_units == "cm":
                        return (x / 10, y / 10)
                    elif config.distance_units == "in":
                        return (x * 0.0393701, y * 0.0393701)
                    elif config.distance_units == "ft":
                        return (x * 0.00328084, y * 0.00328084)
                    else:
                        return (x, y)

        time.sleep(0.02)

    raise TimeoutError("Failed to read a valid radar frame within the time limit.")

def ReadRadarDataWithRaw() -> tuple[float, float]:
    """
    Reads and processes a data frame from radar, returns raw and Kalman-filtered distance.

    Returns:
    - Tuple of (raw_distance, filtered_distance), both in selected units.
    """
    global buffer_hex, First_Measurement, kf

    start_seq = "aaff0300"
    pattern = re.compile(rf'{start_seq}[0-9a-f]+?55[0-9a-f]{{2}}', re.IGNORECASE)
    max_attempts = 50
    ser.flushInput()
    
    for _ in range(max_attempts):

        if ser.in_waiting > 0:
            data = ser.read(32)
            buffer_hex += data.hex()

            for match in pattern.finditer(buffer_hex):
                frame = match.group()
                x_raw, y_raw = parse_coordinates(frame)

                if x_raw is None or y_raw is None:
                    continue

                x_filtered, y_filtered = x_raw, y_raw

                if config.Kalman:
                    kalman_input = np.array([[x_raw], [y_raw]])
                    if First_Measurement:
                        kf = Kalman(kalman_input)
                        First_Measurement = False
                    else:
                        kf.step(kalman_input)
                        kalman_output = kf.X_k
                        x_filtered = float(kalman_output[0, 0])
                        y_filtered = float(kalman_output[1, 0])

                buffer_hex = buffer_hex[match.end():]

                def convert_units(x: float, y: float) -> tuple[float, float]:
                    unit = config.distance_units
                    if unit == "m":
                        return x / 100, y / 100
                    elif unit == "cm":
                        return x / 10, y / 10
                    elif unit == "in":
                        return x * 0.0393701, y * 0.0393701
                    elif unit == "ft":
                        return x * 0.00328084, y * 0.00328084
                    return x, y

                x_raw, y_raw = convert_units(x_raw, y_raw)
                x_filtered, y_filtered = convert_units(x_filtered, y_filtered)

                distance_raw = Convert_Dist(x_raw, y_raw)
                distance_filtered = Convert_Dist(x_filtered, y_filtered)

                return distance_raw, distance_filtered

        time.sleep(0.02)

    raise TimeoutError("Failed to read a valid radar frame within the time limit.")

def kalman_test(true_lenght: float, measure_frequency: float, quantity_measure: int, chart_comment: str, file_name: str) -> None:
    import os
    os.makedirs(config.Kalman_Chart_Path, exist_ok=True)

    plt.ion()
    fig, ax = plt.subplots()
    times, dist_raw_vals, dist_filt_vals = [], [], []

    line_raw, = ax.plot([], [], 'r-', label='Raw')
    line_filt, = ax.plot([], [], 'b-', label='Kalman')
    if true_lenght != None:
        ax.axhline(y=true_lenght, color='g', linestyle='--', label=f'Expected ({true_lenght} cm)')
    ax.set_title(chart_comment)
    ax.set_xlabel('Measurement Number')
    ax.set_ylabel('Distance [cm]')
    ax.grid(True)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend()

    if config.Kalman_Save_csv:
        with open(f"{config.Kalman_Chart_Path}/{file_name}.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Index", "Raw [cm]", "Kalman [cm]"])

            for i in range(quantity_measure):
                dist_raw, dist_filt = ReadRadarDataWithRaw()
                print(f"{i}: Raw = {dist_raw:.2f} cm | Kalman = {dist_filt:.2f} cm")
                writer.writerow([i, f"{dist_raw:.2f}", f"{dist_filt:.2f}"])

                times.append(i)
                dist_raw_vals.append(dist_raw)
                dist_filt_vals.append(dist_filt)

                line_raw.set_data(times, dist_raw_vals)
                line_filt.set_data(times, dist_filt_vals)
                ax.relim()
                ax.autoscale_view()

                plt.draw()
                plt.pause(0.01)
                time.sleep(1/measure_frequency)

    else:
        for i in range(quantity_measure):
            dist_raw, dist_filt = ReadRadarDataWithRaw()
            print(f"{i}: Raw = {dist_raw:.2f} cm | Kalman = {dist_filt:.2f} cm")

            times.append(i)
            dist_raw_vals.append(dist_raw)
            dist_filt_vals.append(dist_filt)

            line_raw.set_data(times, dist_raw_vals)
            line_filt.set_data(times, dist_filt_vals)
            ax.relim()
            ax.autoscale_view()

            plt.draw()
            plt.pause(0.01)
            time.sleep(1/measure_frequency)

    plt.ioff()
    plt.savefig(f"{config.Kalman_Chart_Path}/{file_name}.png")
    print("Kalman test completed.")
