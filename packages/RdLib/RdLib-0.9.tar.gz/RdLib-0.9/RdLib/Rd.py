from .config import config
from .RdDriver import Initialize, ReadRadarData, Convert_Dist, get_angle_degrees, ReadRadarDataWithRaw , kalman_test

class Rd:
    def __init__(self):
        """
        Initializes the radar system using the detection mode specified in the configuration.
        """
        Initialize(config.Detection_Mode)

    def get_distance(self) -> float:
        """
        Reads radar data and calculates the distance to the detected object.

        Returns:
            float: Distance to the object in meters.
        """
        x, y = ReadRadarData()
        distance = Convert_Dist(x, y)
        return distance

    def Calibrate_Kalman(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Calibrates the radar system using Kalman filtering.

        Returns:
            tuple: A tuple containing two sub-tuples:
                - (distance_raw_x, distance_raw_y): Raw (unfiltered) distance values.
                - (distance_filtered_x, distance_filtered_y): Filtered distance values.
        """
        distance_raw, distance_filtered = ReadRadarDataWithRaw()
        return (distance_raw, distance_filtered)

    def get_coordinate(self) -> tuple[float, float]:
        """
        Reads radar data and returns the 2D coordinates of the detected object.

        Returns:
            tuple: (x, y) coordinates in meters.
        """
        x, y = ReadRadarData()
        return (x, y)

    def get_angle(self) -> float:
        """
        Calculates the angle between the radar and the detected object in degrees.

        Returns:
            float: Angle in degrees.
        """
        x, y = ReadRadarData()
        angle = get_angle_degrees(x, y)
        return angle

    def OutputDump(self) -> tuple[float, float, float, float, float, float]:
        """
        Returns a full snapshot of radar data.

        Returned values:
            - x (float): X coordinate of the object
            - y (float): Y coordinate of the object
            - distance (float): Converted distance from the radar to the object
            - angle (float): Angle to the object in degrees
            - detection_mode (float): Current radar detection mode
            - raw_distance (float): Raw distance (before conversion)

        Returns:
            tuple: (x, y, distance, angle, detection_mode, raw_distance)
        """
        x, y = ReadRadarData()
        distance = Convert_Dist(x, y)
        angle = get_angle_degrees(x, y)
        detection_mode = config.Detection_Mode
        raw_distance = ((x ** 2 + y ** 2) ** 0.5)

        return (x, y, distance, angle, detection_mode, raw_distance)
    def Kalman_Test(self,true_length: float, measure_frequency: float, quantity_measure: int, chart_comment: str, file_name: str) -> None:
        """
        Runs a Kalman filter test on distance measurements and visualizes the results.

        Parameters:
        - true_length (float): Expected distance in cm (used as a reference line on the chart).
        - measure_frequency (float): Delay between measurements in seconds.
        - quantity_measure (int): Number of total measurements.
        - chart_comment (str): Title of the chart.
        - file_name (str): Name used to save CSV and chart image.

        Behavior:
        - Collects distance measurements (raw and filtered).
        - Plots real-time updates of both raw and Kalman-filtered data.
        - Saves data to CSV and chart to PNG if configured to do so.
        """
        kalman_test(true_length,measure_frequency,quantity_measure,chart_comment,file_name)