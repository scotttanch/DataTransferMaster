import pyrealsense2.pyrealsense2 as rs
import time
import numpy as np
import matplotlib.pyplot as plt
import sys

def reorient():
	pipe.stop()
	pipe.start(cfg)

pipe = rs.pipeline()

cfg = rs.config()
cfg.enable_stream(rs.stream.pose)

pipe.start(cfg)

x_pos = [0]
y_pos = [0]
z_pos = [0]

while(True):
	try:
		frames = pipe.wait_for_frames()
		pose = frames.get_pose_frame()
		if pose:

			#Get new position and rotation
			position = pose.get_pose_data().translation

			#If new position is some distance from the last position record it, change this later to record if 
			#There is an input signal from the survey wheel

			trigger = True
			if trigger == True:

				x_pos.append(round(-position.z,2))
				y_pos.append(round(position.x,2))
				z_pos.append(round(position.y,2))
				print(x_pos[-1],",",y_pos[-1],",",z_pos[-1])
				time.sleep(1)

	except KeyboardInterrupt:
		break

print("Interupted")
pipe.stop()
sys.exit(0)
