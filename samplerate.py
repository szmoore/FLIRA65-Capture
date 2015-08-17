#!/usr/bin/python -i
import numpy as np
import pylab as P
w = open("samples.dat","r")
data = np.asarray([float(f.strip()) for f in w.readlines()])
w.close()
data = np.diff(data)
n = P.hist(data, 30, normed=True)
w = (n[1][1]-n[1][0])/2
P.bar(n[1][:-1], n[0], w)
P.show()
