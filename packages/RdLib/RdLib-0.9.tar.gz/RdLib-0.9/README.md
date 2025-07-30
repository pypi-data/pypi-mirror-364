# Python RdLib Library for Rd03d and HLK-LD2450 for raspberrypi

For now library is using only serial communication with these radars. 
Might be necessary to set temporarily permission to the serial port:
- sudo chmod 777 /dev/ttyS0

How to install that library?
- pip install RdLib

Whole library is preconfigured to both radar. Just plug&play
But to be specific here is documentation about implementation: 

-Basic implementation  without any configuration

    from RdLib.Rd import Rd 
    rd = Rd()
    
    print(rd.get_angle())
        """
        Calculates the angle between the radar and the detected object in degrees.

        Returns:
            float: Angle in degrees.
        """
    
    print(rd.get_coordinate())
        """
        Reads radar data and returns the 2D coordinates of the detected object.

        Returns:
            tuple: (x, y) coordinates in meters.
        """
    
    print(rd.OutputDump())
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
    
    print(rd.get_distance())
        """
        Reads radar data and calculates the distance to the detected object.

        Returns:
            float: Distance to the object in meters.
        """
    
    print(rd.Kalman_Test(100,1,5,"Test2","Test2"))
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
    
    print(rd.Calibrate_Kalman())
            """
        That function gives you raw data from radar compared to the filtered by kalman.
        Important you must turn on kalman by config.set(Kalman=True)

        Returns:
            tuple: A tuple containing two sub-tuples:
                - (distance_raw_x, distance_raw_y): Raw (unfiltered) distance values.
                - (distance_filtered_x, distance_filtered_y): Filtered distance values.
        """
-Advanced implementation with config.
Example:

      from RdLib.Rd import Rd 
      from RdLib.config import config

      
      #Example of Entry Configuration
      config.set(Kalman_Save_csv=False)
      config.set(Kalman=True)
      config.set(distance_units="cm") 
      rd = Rd()

      print(rd.get_angle())
      print(rd.get_coordinate())
      print(rd.OutputDump())
      print(rd.get_distance())
      print(rd.Kalman_Test(100,1,5,"Test2","Test2"))
      print(rd.Calibrate_Kalman())

Description about all config settings:

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

-You can fine-tune the radar behavior using the Kalman_Test() function, which helps visualize the impact of your settings with a chart. This is especially important to match your specific use case.
    Kalman_Q – This parameter controls the process noise. If you're tracking fast or unpredictable movements (e.g., people walking or running), increasing this value makes the filter more responsive to sudden changes.
    Default: 0.1 – a good universal value, but not optimal for all scenarios.
    Higher values → more responsive but noisier output.
    Lower values → smoother but slower response.
    Kalman_R – This defines the measurement noise. You can increase it if your radar gives very noisy readings, to make the filter rely more on predictions.
    Measurement frequency – Setting a higher frequency (i.e., faster sampling) increases the number of measurements per second. This gives more data but can also introduce more noise and interference.
    Since these budget radars are not highly precise, it's often better to use the lowest frequency that still meets your requirements.
      
      For that is usefull Kalman_Test()
      Example of using that function:
      
              from RdLib.Rd import Rd 
              from RdLib.config import config
              import numpy as np
              config.set(Kalman=True)
              self.Kalman_Chart_Path = 'YourPath' it will be easier if it is a folder only for measurements
              
              #rd.Kalman_Test(true_lenght,measure_frequency,quentity_measure,chart_comment,file_name)
              rd.Kalman_Test(100,1,5,"Test2","Test2")
  -Chart example:
  
  ![Chart_Example](Test_Charts/Test1.png)


              
              
