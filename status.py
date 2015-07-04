#!/usr/bin/python

import sqlite3
import sys
import os

conn = sqlite3.connect("status.db")
c = conn.cursor()

status = None
op = ""


def save():
	global status
	try:
		c.execute("DROP TABLE status")
	except sqlite3.OperationalError:
		pass
	
	if status == None:
		return
		
	op = "CREATE TABLE status("+",".join(status.keys())+")"
	c.execute(op)
	op = "INSERT INTO status("+",".join(status.keys())+") VALUES ("+",".join("?" for _ in range(len(status.keys())))+")"
	c.execute(op, status.values())
	conn.commit()
		
def load():
	global status
	op = "PRAGMA TABLE_INFO(status)"
	c.execute(op)
	f = c.fetchall()
	if (len(f) == 0):
		status = None
		return
	keys = [str(e[1]) for e in f]
	
	op = "SELECT "+",".join(keys)+" FROM status"
	c.execute(op)
	
	f = c.fetchall()
	if len(f) == 0:
		status = None
	elif len(f) > 1:
		raise Exception("Too many status entries")
	else:
		status = {}
		for i,k in enumerate(keys):
			status[k] = f[0][i]
	
	
load()

def print_status(out=sys.stdout):
	global status
	if status == None:
		print("No Experiment")
	else:
		for k in status.keys():
			print("%s = %s" % (str(k), str(status[k])))
	
	
if __name__ == "__main__":
	print_status()
