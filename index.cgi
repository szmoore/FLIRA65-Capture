#!/usr/bin/python

import sys
import os
import signal
import cgi
import status as s
import subprocess
import datetime

try:
	g_help_text = open("help", "r").read().replace("\n", "\\n")	
except:
	g_help_text = "No help available."


def boilerplate_start():
	print("<html><head><title>FLIRA65 Capture Control</title></head>");
	print('<body bgcolor="#99cc99" text="#000000" link="#2020ff" vlink="#4040cc" onload="loadTime()">')
	print('<div style="width:50%; align:float-left; border:1px solid black;">') 
	print("<h1>FLIRA65 Capture Control</h1>")
	print("<p>")
	print('<button onclick="alert(\'%s\')"><b>HELP</b></button>' % str(g_help_text))
	print('<a href="manage.cgi"><button>Manage data files</button></a>')
	
	print("<script type='text/javascript'>")
	print("function loadTime() {")
	print("var now = new Date();")
	print('var strDateTime = [[now.getFullYear(), AddZero(now.getMonth() + 1), AddZero(now.getDate()) ].join("-"), [AddZero(now.getHours()), AddZero(now.getMinutes()), AddZero(now.getSeconds())].join(":"), now.getHours() >= 12 ? "PM" : "AM"].join(" ");')
	print('document.getElementById("date").value = strDateTime;}')
	print('function AddZero(num) {return (num >= 0 && num < 10) ? "0" + num : num + "";}')
	print("</script>")


def boilerplate_end():
	print("</div>")
	if os.path.isfile("latest.png"):
		print('<div style="width:50%; align:float-right; border:1px solid black;">')
		print("<pre>")
		print("<b>Latest Image</b>")
		print("<hr>")
		print('<img src="latest.png?'+datetime.datetime.now().strftime("%s")+'" width="40%"/>')
		print("</hr>")
		print("</div>")

	print("</body>")
	print("</html>")

def red(text):
	return '<span style="color:red;">'+str(text)+'</span>'

def green(text):
	return '<span style="color:green;">'+str(text)+'</span>'

def bold(text):
	return '<b>'+str(text)+'</b>'

def link(text):
	return '<a href="%s">%s</a>' % (str(text), str(text))

def parse_form(form):
	s.load()
	if s.status != None:
		try:
			daemon_pid = s.status["pid"]
			os.kill(daemon_pid, signal.SIGQUIT)	
		except:
			pass
		s.status = None
		s.save()
		return

	if form.getvalue("submitted") == "SINGLE":
		os.environ["LD_LIBRARY_PATH"] = os.environ.get("LD_LIBRARY_PATH", "")+":"+os.getcwd()+"/contrib/lib"
		if os.path.exists("latest0.png"):
			os.unlink("latest0.png")
		error = subprocess.call(["./FLIRA65-Capture", "-e", "100", "-f", "1", "-p", "single", "-t", "png"])
		if error != 0:
			print(bold(red("Error %d performing capture" % error)))
		return

		
				
	
	dir = form.getvalue("directory")
	dir = os.path.abspath(dir)
	root = os.getcwd()
	if dir[0:len(root)] != root or dir.count("/") <= root.count("/"):
		print(bold(red("Invalid data directory; must be below root.")))
		s.status = None
		s.save()
		return
		
	os.system("date --set '%s'" % form.getvalue("date")) 

	keys = ["directory", "maxFrames", "date", "period", "bitdepth"]
	s.status = {}
	for k in keys:
		s.status[k] = form.getvalue(k)

	try:
		s.status["maxFrames"] = int(s.status["maxFrames"])
	except:
		s.status["maxFrames"] = -1

	s.save()
	
def reload_page(timeout):
	print("<script type='text/javascript'>")
	print("	var url = window.location.href;"
		"var i = url.indexOf('?');"
		"if (i < 0) {i = url.length;}"
		"url = url.substr(0,i);"
		"setTimeout(function() {window.location.href=this}.bind(url), %d);" % int(timeout))
	print("</script>")

def run_daemon():

	pid = os.fork()
	if pid > 0:
		sys.exit(0)

	oldcwd = os.getcwd()	
	os.chdir("/")
	os.setsid()
	os.umask(0)
	pid = os.fork()
	if pid > 0:
		sys.exit(0)

	os.close(sys.stdin.fileno())
	os.close(sys.stdout.fileno())
	os.close(sys.stderr.fileno())
	si = file("/dev/null", "r")
	so = file(oldcwd+"/log.out", "w")
	se = file(oldcwd+"/log.err", "w", 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())
	os.chdir(oldcwd)
	sys.exit(os.system("./run.py"))
	# stdout seems to often get flushed twice :S 
	# but this is CGI and firefox ignores everything after the first </html> so it's all good...
	

	

if __name__ == "__main__":
	#sys.stderr = open("index.err", "w", 0)
	print("Content-type: text/html\r\n\r\n")

	form = cgi.FieldStorage()

		

	boilerplate_start()
	
	for root, dirs, files in os.walk("."):
		if "experiment" not in files:
			continue
		if s.status == None:
			f = open(root+"/experiment","w")
			f.write("Stopped\n")
			f.close()
			
	
	if "submitted" in form:
		parse_form(form)
		reload_page(1000)
		
	if s.status != None:
		reload_page(3000)

	print('<form action="index.cgi">')
	print("<pre id='status' style='display:block;'>")
	print("<b>Experiment Status</b>")
	sys.stdout.write("<hr>")

	if s.status != None:
		if "submitted" not in form:
			print("Experiment is running")

		s.print_status()
		action = "STOP"
	else:
		print("Waiting to configure New Experiment\n")
		print("<b>\tData directory    </b> <input id='directory' name='directory' type='text' value='data/'></input>")
		print("<b>\tStart Time        </b> <input id='date' name='date' type='text' value='' readonly='readonly'></input>")
		print("<b>\tMaximum Frames    </b> <input name='maxFrames' type='number' value=''></input>")
		print("<b>\tSample Period(us) </b> <input name='period' type='number' value='0'></input>")
		print("<b>\tBit depth         </b> <input name='bitdepth' type='radio' value='8' checked='yes'>Mono8</input> <input name='bitdepth' type='radio' value='14'>Mono14</input>")
		action = "START"
	print("</form>")
	print("<hr>")
	print("<input id='submitted' name='submitted' type='text' value='' style='display:none;'/>")
	print("<input id='submit' type='submit' value='%s EXPERIMENT' onclick='document.getElementById(\"submit\").value=\"%s\"; document.getElementById(\"submitted\").value=\"%s\"; loadTime();'/>" % (action, action+"ING", action+"ING"))
	if s.status == None:
		print("<input id='submit' type='submit' value='SINGLE CAPTURE' onclick='loadTime(); document.getElementById(\"submitted\").value=\"SINGLE\"'/>")
	
	print("</pre>")


			

	boilerplate_end()
		
	if "submitted" in form and s.status != None:
		run_daemon()
		


	sys.exit(0)
