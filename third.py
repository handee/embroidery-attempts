import pyembroidery as pe
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

img=cv.imread('uk.png')
imgrey=cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret,thresh=cv.threshold(imgrey,125,255,0)

contours, hierarchy=cv.findContours(thresh,cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

cv.drawContours(imgrey,contours,-1,(0,255,0),3)
#plt.subplot(121),plt.imshow(img)
#plt.subplot(122),plt.imshow(imgrey)

#plt.show()

outfile="thirdgo"

smallthresh=7

p1= pe.EmbPattern()
print(f"THere are {len(contours)} contours found")
for c in contours:
    print(f"This contour is {len(c)} points long")
    if len (c) < smallthresh:
        print("Really short contour, probably noise")
    
    else:
        print("Adding the contour of an object to our pattern")
        stitches=[];
        for pt in c:
            stitches.append([pt[0][0],pt[0][1]])
        p1.add_block(stitches, "blue")

pe.write_dst(p1, f"{outfile}.dst")
pe.write_png(p1, f"{outfile}.png")
