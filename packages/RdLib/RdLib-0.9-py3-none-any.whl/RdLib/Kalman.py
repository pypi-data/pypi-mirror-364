import numpy as np
from .config import config
class Kalman:
    def __init__(self, initial_measurement):
        self.k = 0
        self.Dt = 1

        self.F = np.array([
            [1, 0, self.Dt, 0],
            [0, 1, 0, self.Dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        self.Q = config.Kalman_Q
        self.K_k = np.zeros((4, 2))
        

        # Inicjalizacja stanu na podstawie pierwszego pomiaru (pozycja), prędkości = 0
        self.X_k = np.array([
            [initial_measurement[0, 0]],
            [initial_measurement[1, 0]],
            [0.0],
            [0.0]
        ])

        self.Y_k = np.array([
            [0.0],
            [0.0]
        ])

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

        self.R = np.array([
            [50, 0],
            [0, 50]
        ])

        self.P_p = np.eye(4) * 1

    def prediction(self):
        self.X_k = self.F @ self.X_k
        return self.X_k

    def covariation_error_prediction(self):
        self.P_p = self.F @ self.P_p @ self.F.T + self.Q
        return self.P_p

    def Innovation(self, z_k):
        self.Y_k = z_k - (self.H @ self.X_k)
        return self.Y_k

    def Innovation_Covariation(self):
        self.S_k = self.H @ self.P_p @ self.H.T + self.R
        return self.S_k

    def KalmanGain(self):
        self.K_k = self.P_p @ self.H.T @ np.linalg.inv(self.S_k)
        return self.K_k

    def update(self):
        I = np.eye(self.P_p.shape[0])
        self.X_k = self.X_k + self.K_k @ self.Y_k
        self.P_p = (I - self.K_k @ self.H) @ self.P_p

    def step(self, z_k):
        self.prediction()
        self.covariation_error_prediction()
        self.Innovation(z_k)
        self.Innovation_Covariation()
        self.KalmanGain()
        self.update()



    
    