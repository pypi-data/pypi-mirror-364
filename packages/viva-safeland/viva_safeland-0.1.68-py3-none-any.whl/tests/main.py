import cv2
import numpy as np
from viva.env import DroneEnv
from viva.modules import HMI

env = DroneEnv(
    render_mode="human",
    video="/media/juls/HDD/Videos_Dron/AgsExedra_DJI_20240914133357_0010_D.MP4",
)
env.reset()
control = HMI()
count, terminated = 0, False
while not terminated and count < 1500:
    count += 1
    # action = [np.random.uniform(-1, 1) for _ in range(3)]  # Random actions
    action, reset, terminated_command = control()
    if reset:
        env.reset()
    obs, terminated, info = env.step(action)
    terminated = terminated or terminated_command
    cv2.imshow("Observation", obs)
    if cv2.waitKey(1) == 27: 
        break
