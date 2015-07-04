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
	print("<html><head><title>FLIRA65 Manage Data</title></head>");
	print('<body bgcolor="#99cc99" text="#000000" link="#2020ff" vlink="#4040cc">')
	print('<div style="width:50%; align:float-left; border:1px solid black;">') 
	print("<h1>FLIRA65 Manage Data</h1>")
	print("<p>")
	print('<button onclick="alert(\'%s\')"><b>HELP</b></button>' % str(g_help_text))
	print('<a href="/index.cgi"><button>Experiment Control</button></a>')


def boilerplate_end():
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

	s.save()
	
def reload_page(timeout):
	print("<script type='text/javascript'>")
	print("	var url = window.location.href;"
		"var i = url.indexOf('?');"
		"if (i < 0) {i = url.length;}"
		"url = url.substr(0,i);"
		"setTimeout(function() {window.location.href=this}.bind(url), %d);" % int(timeout))
	print("</script>")
	sys.exit(os.system("./run.py"))
		
	

	

if __name__ == "__main__":
	#sys.stderr = open("index.err", "w", 0)
	print("Content-type: text/html\r\n\r\n")

	form = cgi.FieldStorage()

		

	boilerplate_start()
	
	print("<pre>")
	print("<b>Experiment Directories</b>")
	print("<hr>")
	for root, dirs, files in os.walk("."):
		if "experiment" not in files:
			continue
		experiment_state = open(root+"/experiment", "r").read().strip()
		if experiment_state == "Running":
			print(bold("Running: ")+link(root)+"\t<button>"+bold("Download")+"</button>")
		else:
			print(bold(green("Finished: "))+link(root)+"\t<button>"+bold("Download")+"</button>\t<button>"+bold(red("Delete"))+"</button>")
		for d in dirs:
			print(" --- "+str(d))
		
	print("<hr>")
	print("</pre>")
	


	boilerplate_end()

		


	sys.exit(0)
