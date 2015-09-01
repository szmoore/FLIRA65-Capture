#!/usr/bin/python

# Wrapper to FLIRA65-Capture for things that are too hard to write in C
# Could use a POpen.poll to do more advanced monitoring. At the moment basically just a wrapper.

import sys
import os
import datetime
import time
import subprocess
import status as s
import shutil
import signal

global child_process
child_process = None

def cleanup(signal, frame):
	if child_process != None:
		if child_process.poll() == None:
			child_process.send_signal(signal) # Need to kill the child as well
	print("Finished.")
	with open(s.status["directory"]+"/experiment", "w") as f:
		f.write("Stopped")	
	s.status = None
	s.save()
	sys.exit(0)

def main(argv):
	global child_process
	os.environ["LD_LIBRARY_PATH"] = os.environ.get("LD_LIBRARY_PATH", "")+":"+os.getcwd()+"/contrib/lib"
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
	initialFiles = len([f for f in os.listdir("data") if 'png' in f])
	maxFrames = int(s.status["maxFrames"])
	while (s.status != None and (s.status["maxFrames"] < 0 or s.status["currentFrame"] < s.status["maxFrames"])):
		s.load()
		#error = subprocess.call(["./FLIRA65-Capture", "-f", "-1", "-D", s.status["directory"]])
		child_process = subprocess.Popen(["./FLIRA65-Capture", "-f", str(maxFrames), "-D", s.status["directory"], '-F', s.status["bitdepth"], '-T', s.status["period"]])
		while child_process.poll() is None:
			time.sleep(1)
			files = [f for f in os.listdir("data") if 'png' in f]
			s.status["currentFrame"] = len(files)-initialFiles
			if len(files) == 0:
				continue
			latest = s.status["directory"]+"/"+files[-1]
			s.status["lastFrame"] = "<a href='%s'>%s</a>" % (s.status["directory"]+"/"+files[-1], files[-1])
			s.save()

		if (maxFrames > 0):
			maxFrames = maxFrames-s.status["currentFrame"]
		s.save()
		pass
		
	cleanup(None,None)
	return 0 # redundant

if __name__ == "__main__":
	sys.exit(main(sys.argv))
