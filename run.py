#!/usr/bin/python

import sys
import os
import datetime
import time
import subprocess
import status as s
import shutil
import signal

def cleanup(signal, frame):
	print("Finished.")
	with open(s.status["directory"]+"/experiment", "w") as f:
		f.write("Stopped")	
	s.status = None
	s.save()
	sys.exit(0)

def main(argv):
	signal.signal(signal.SIGINT, cleanup)
	signal.signal(signal.SIGQUIT, cleanup)
	if s.status == None:	
		try:
			maxFrames = int(argv[2])
		except:
			maxFrames = -1
		try:
			direct = str(argv[1])
		except:
			direct = None
		s.status = {
			"directory" : direct,
			"pid" : os.getpid(),
			"maxFrames" : maxFrames,
			"currentFrame" : 0,
			"timestamp" : int(datetime.datetime.now().strftime("%s"))
		}
		s.save()
	
	
	try:
		if s.status["directory"][-1] == '/':
			s.status["directory"] = s.status["directory"][0:-1]
	except:
		s.status["directory"] = "data/"+datetime.datetime.now().strftime("%F/%H:%M")
		
	if not os.path.exists(s.status["directory"]):
		os.makedirs(s.status["directory"])
	with open(s.status["directory"]+"/experiment", "w") as f:
		f.write("Running")
		
	s.status["pid"] = os.getpid()
	s.status["currentFrame"] = 0
	s.save()
	lasttime = float(datetime.datetime.now().strftime("%s.%f"))
	while (s.status != None and (s.status["maxFrames"] < 0 or s.status["currentFrame"] < s.status["maxFrames"])):
		s.load()
		error = subprocess.call(["./FLIRA65-Capture", "-f", "1", "-p", "latest"])
		timestamp = float(datetime.datetime.now().strftime("%s.%f"))
		s.status["timestamp"] = timestamp

		if error == 0:
			s.status["sampleRate"] = timestamp-lasttime
			lasttime = timestamp
			s.status["currentFrame"] += 1;
			s.status["lastCapture"] = "Success"
			shutil.copy2("latest0.png", s.status["directory"]+"/%.3f.png" % timestamp)
		else:
			s.status["lastCapture"] = "Error"
		s.save()
		pass
		
	cleanup(None,None)
	return 0 # redundant

if __name__ == "__main__":
	sys.exit(main(sys.argv))
