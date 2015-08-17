#!/usr/bin/python -i
from skimage.io import imread, imsave
import numpy as np
data = imread("latest0.png")
mx = data.max()
for x in range(data.shape[0]):
	for y in range(data.shape[1]):
		data[x,y] = int((data[x,y]/(1.*mx))*(2**16-1))
imsave("normalised.png", data)
