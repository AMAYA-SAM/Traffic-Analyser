import cv2
import numpy as np 
from diff_density import diff_density
import time
import sys

#DIFFERENT TRAFFIC DENSITY DATA
TRAFFIC = ["EMPTY", "V LIGHT", "LIGHT", "MODERATE", "HIGH", "V HIGH"]
TRAFFIC_THRESH = [3, 24, 29, 34, 38]
TRAFFIC_TIME = [0.0, 2.0, 3.0, 4.0, 5.0, 6.0]
TRAFFIC_COLOR = [(240,240,240), (0,255,0), (0,128,0), (0,69,255), (0,0,128), (0,0,255)]

#Frame rate of input traffic video is 10, please change for different source
MAX_FPS = 10

# This is to generalize all lanes as they will have different 
# source, bg, roi and traffic
lanes = []
# lanes.append([SOURCE, BG, X, Y, WIDTH, HEIGHT, TRAFFIC]) to add a lane
SRC, BG, X, Y, W, H, TR = range(7)

path = "traffic_video/"
lanes.append([path+"1.avi", 
	path+"1_bg.png",
	450, 0, 100, 540, 0])
lanes.append([path+"2.avi", 
	path+"2_bg.png",
	450, 0, 100, 540, 0])
lanes.append([path+"3.avi", 
	path+"3_bg.png",
	450, 0, 100, 540, 0])
lanes.append([path+"4.avi", 
	path+"4_bg.png",
	450, 0, 100, 540, 0])

no_of_lanes = len(lanes)

#Which lane has green light and corresponding timer
green = 0
timer = 2.0

cam = []
f = []
bg = []
gray = []

#Initializing cam reader lists
for n in range(no_of_lanes):
	cam.append( cv2.VideoCapture(lanes[n][SRC]) )
	ret, frame = cam[n].read()
	if(ret is False):
		print("Video could not be loaded")
		exit()
	f.append( frame )
	gray.append( cv2.cvtColor(f[n], cv2.COLOR_BGR2GRAY))
	bg.append( cv2.imread(lanes[n][BG], 0) )

#For FPS management
max_frame_period = 1.0/MAX_FPS
delay = 0
timet = time.time()
#initializing vars
init_time =timet
final_time =timet

valid = True
while(valid):

	init_time = final_time

	for i in range(no_of_lanes):

		_, f[i] = cam[i].read()
		if f[i] is None:
			print("No video input")
			valid = False
			break

		gray[i] = cv2.cvtColor(f[i], cv2.COLOR_BGR2GRAY)

		d = diff_density(gray[i], bg[i], lanes[i][X], lanes[i][Y], lanes[i][W], lanes[i][H])

		#Calculate traffic index based on d
		lanes[i][TR] = 0
		for t in TRAFFIC_THRESH:
			if(d > t):
				lanes[i][TR]+=1

		#Add appropriate traffic message to screen
		if(green == i):
			cv2.putText(f[i], str(round(timer,2)), (0,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,255), 4)
		else:
			cv2.putText(f[i], TRAFFIC[lanes[i][TR]], (0,50), cv2.FONT_HERSHEY_SIMPLEX, 1, TRAFFIC_COLOR[lanes[i][TR]], 3)

		res = cv2.resize(f[i], None, fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)

		cv2.imshow(str(i+1), res)

	k = cv2.waitKey(1)
	if k&255 == 27:
		break

	timet = time.time()
	final_time = timet
	frame_period = final_time - init_time
	extra_time = max_frame_period - frame_period
	delay -= extra_time

	#Creating a delay to stay in MAX_FPS range
	if(delay<0):
		time.sleep((-delay))
		delay=0.0

	timet = time.time()
	final_time = timet
	actual_frame_period = final_time - init_time

	timer = timer - actual_frame_period
	if(timer <= 0.0):
		#Green light to next lane
		green = (green+1)%no_of_lanes
		timer = TRAFFIC_TIME[lanes[green][TR]]

	sys.stdout.write("FPS ")
	sys.stdout.write(str(1/actual_frame_period))
	sys.stdout.write('\r')
	sys.stdout.flush()

#Releasing all vars
for i in range(no_of_lanes):
	cam[i].release()

cv2.destroyAllWindows()