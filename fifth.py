import pyembroidery as pe
import math
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

stitchgap=20 # max length between stitches, x or y gaps greater than this will have extra points added between them

# min length of stitch is handled in a SUPER hacky way by downscaling the image then upscaling the stitch arrays.
upscale=4
dsf=1.0/upscale# downscale factor
print(f"Images will be downscaled by {dsf} for processing then stitches will be upscaled by {upscale} for output")

# in pyembroidery a unit of 1 == 0.1mm so 20 means stitches longer than 2mm will be sub-stitched.

smallthresh=7 # smaller contours than this will be deleted. make this lower if you are dealing with shapes with lots of straight lines

outfile="fifthgo"



def check_for_long_stitches(s):
    s1=[]
    s1.append(s[0])
    print(f"This contour has {len(s)} points")
    for i in range(0,len(s)-1):
        if abs(s[i][0]-s[i+1][0]) > stitchgap or abs(s[i][1]-s[i+1][1]) > stitchgap :
            print(f"Stitchgap at {i}, {s[i]},{s[i+1]}")
            l=max(abs(s[i][0]-s[i+1][0]), abs(s[i][1]-s[i+1][1]))
            n=int(math.floor(l/stitchgap))
            dx=int(math.floor((s[i+1][0]-s[i][0]) / (n+1)))
            dy=int(math.floor(( s[i+1][1]-s[i][1]) / (n+1)))
            print(f"The gap is {l} units long so will need {n} stitches infill, {dx},{dy} is stitch dx,dy")
            for j in range(1,n+1):
                ns=[0,0]
                ns[0]=s[i][0]+j*dx
                ns[1]=s[i][1]+j*dy
                s1.append(ns)
                print(f"added {ns} to stitch list")
        s1.append(s[i+1])
    print(f"Now this contour has {len(s1)} points")
    return(s1)


cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Display the resulting frame
    cv.imshow('frame', grey)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()

# this is the scale down bit
simg=cv.resize(grey, None, fx=dsf, fy=dsf, interpolation=cv.INTER_LINEAR)
ret,thresh=cv.threshold(grey,125,255,0)

contours, hierarchy=cv.findContours(thresh,cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

cv.drawContours(grey,contours,-1,(0,255,0),3)


p1= pe.EmbPattern()
print(f"THere are {len(contours)} contours found")
for c in contours:
    if len (c) < smallthresh:
        print("Really short contour, probably noise")
    else:
        contour_array=[]
        for pt in c:
            contour_array.append([pt[0][0],pt[0][1]])
        contour_array=np.multiply(contour_array,upscale-1) # now we upscale
        stitches=check_for_long_stitches(contour_array.tolist())
        p1.add_block(stitches, "blue")

pe.write_dst(p1, f"{outfile}.dst")
pe.write_png(p1, f"{outfile}.png")
