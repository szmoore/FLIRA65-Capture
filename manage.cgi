#!/usr/bin/python

import sys
import os
import signal
import cgi
import status as s
import subprocess
import datetime
import shutil

import zipfile

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

def link(text, value=None):
	if value == None:
		value = text
	return '<a href="%s">%s</a>' % (str(text), str(value))

def parse_form(form):
	#s.load()
	for k in form.keys():
		if not is_experiment(k):
			continue
			
		if form.getvalue(k) == 'Download':
			print(bold("<p>"+link("download.zip","Click to Download "+k)+"</p>"))
			shutil.make_archive("download", "zip", root_dir=".", base_dir=k)
		elif form.getvalue(k) == 'Delete':
			if k+"_confirm_delete" in form.keys() and form.getvalue(k+"_confirm_delete") == "Yes":
				# Only delete paths lower than the current wd
				root = os.getcwd()
				k = os.path.abspath(k)
				if k[0:len(root)] != root or k.count("/") <= root.count("/"):
					print(bold(red("<p> Path to delete not below root!</p>")))
					return

				print(bold("<p>Delete %s CONFIRMED</p>" % k))
				shutil.rmtree(k)
			else:
				print(bold(red("<p>Delete %s UNCONFIRMED</p>" % k)))
	#s.save()
	
def reload_page(timeout):
	print("<script type='text/javascript'>")
	print("	var url = window.location.href;"
		"var i = url.indexOf('?');"
		"if (i < 0) {i = url.length;}"
		"url = url.substr(0,i);"
		"setTimeout(function() {window.location.href=this}.bind(url), %d);" % int(timeout))
	print("</script>")
	sys.exit(os.system("./run.py"))
		
	
def submit(name, value, color='black'):
	return "<input type='submit' name='%s' value='%s' style='color:%s; font-weight:bold;'/>" % (str(name), str(value), str(color))
	
def is_experiment(path):
	return os.path.isdir(path) and "experiment" in os.listdir(path) and os.path.isfile(path+"/experiment")

if __name__ == "__main__":
	#sys.stderr = open("index.err", "w", 0)
	print("Content-type: text/html\r\n\r\n")

	form = cgi.FieldStorage()
	if len(form) > 0:
		parse_form(form)
		#reload_page(1000)
		

	boilerplate_start()
	print("<form action='manage.cgi'>")
	print("<pre>")
	print("<b>Experiment Directories</b>")
	print("<hr>")
	for root, dirs, files in os.walk("."):
		if "experiment" not in files:
			continue
		experiment_state = open(root+"/experiment", "r").read().strip()
		pad = " "*(30-len(root))
		if experiment_state == "Running":
			print(bold("Running:  ")+link(root)+pad+submit(root, "Download"))
		else:
			print(bold(green("Finished: "))+link(root)+pad+submit(root, "Download")+"\t"+submit(root, "Delete", "red")+
				red("<input type='checkbox' name='"+root+"_confirm_delete' value='Yes'/>Confirm Deletion"))
		for d in dirs:
			print(" --- "+str(d))
		
	print("<hr>")
	print("</pre>")
	print("</form>")
	


	boilerplate_end()

		


	sys.exit(0)
