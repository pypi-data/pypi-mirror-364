import cv2
import numpy as np
from viva.env import DroneEnv
from viva.modules import HMI

env = DroneEnv(
    render_mode="human",
    video="/media/juls/HDD/Videos_Dron/DJI_20240910181532_0005_D.MP4",
)
env.reset()
control = HMI()
terminated = False
while not terminated:
    action, reset, terminated_command = control()
    if reset:
        env.reset()
    obs, terminated, info = env.step(action)
    terminated = terminated or terminated_command
    cv2.imshow("Observation", obs)
    if cv2.waitKey(1) == 27: 
        break
