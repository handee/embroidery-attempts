import pyembroidery as pe
import math
import numpy as np
import cv2 as cv
import argparse
from matplotlib import pyplot as plt

stitchgap=20 # max length between stitches, x or y gaps greater than this will have extra points added between them

# min length of stitch is handled in a SUPER hacky way by downscaling the image then upscaling the stitch arrays.
upscale=3
dsf=0.5 # downscale factor
print(f"Images will be downscaled by {dsf} for processing then stitches will be upscaled by {upscale} for output")

# in pyembroidery a unit of 1 == 0.1mm so 20 means stitches longer than 2mm will be sub-stitched.

smallthresh=7 # smaller contours than this will be deleted. make this lower if you are dealing with shapes with lots of straight lines

canny1=125
canny2=205

parser=argparse.ArgumentParser()
parser.add_argument('filename', help='filename to act upon', nargs='?', const='input.png', default='input.png')
args=parser.parse_args()
print(args)
outfile="emb-"+args.filename
print(outfile)

win='Hacky Embroidery Stuff'

def on_trackbar(val):
    global canny1 
    global canny2 
    if (canny2>val):
        canny1 = val 
def on_trackbar2(val):
    global canny1 
    global canny2 
    if (canny1<val):
        canny2 = val 


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



cv.namedWindow(win)
cv.createTrackbar('Canny1', win,0,255,on_trackbar)
cv.createTrackbar('Canny2', win,0,255,on_trackbar2)

frame=cv.imread(args.filename)
while(1):
    grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
 
    w=grey.shape[1]
    h=grey.shape[0]
    nw=int(w*dsf)
    nh=int(h*dsf)
# this is the scale down bit
    simg=cv.resize(grey, (nw,nh), interpolation=cv.INTER_LINEAR)
    canny=cv.Canny(simg,canny1,canny2)

    contours, hierarchy=cv.findContours(canny,cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    cv.drawContours(simg,contours,-1,(0,255,0),3)
       # Display the resulting frame
       
    cv.imshow(win, simg)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cv.destroyAllWindows()


p1= pe.EmbPattern()
print(f"THere are {len(contours)} contours found")
for c in contours:
    if len (c) < smallthresh:
        print("Really short contour, probably noise")
    else:
        contour_array=[]
        for pt in c:
            contour_array.append([pt[0][0],pt[0][1]])
        contour_array=np.multiply(contour_array,upscale) # now we upscale
        stitches=check_for_long_stitches(contour_array.tolist())
        p1.add_block(stitches, "blue")

pe.write_pes(p1, f"{outfile}.pes")
pe.write_png(p1, f"{outfile}.png")
