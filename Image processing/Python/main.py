# for testing
import time
import matplotlib.pyplot as plt

# required
import picamera
import numpy as np
from scipy import signal
from multiprocessing import Pool
import functions as fun
from PIL import Image

# image width/height settings for image processing
w,h = 60,40 
p = 2
bufferSize = 10
video_port = True
burst = True
if video_port==True: burst=False # cannot use both..

# filter kernals
dataType = np.float16
fx = np.array([[0, 1, -1]],dtype=dataType)
fy = np.array([[ 0], 
               [ 1], 
               [-1]],dtype=dataType)

fxr = np.array([[-1, 1, 0]],dtype=dataType)
fyr = np.array([[-1], 
                [ 1], 
                [ 0]],dtype=dataType)


# pre-compute integrartion kernal
g = fun.calculate_g(h,w,p,dataType)

# init buffer 
buffer = [np.empty((h * w * 3), dtype=np.uint8) for _ in range(bufferSize)] 
capture = 0

# main loop
while(True):
    # init camera and settings ready for each photo 
    camera = picamera.PiCamera()
    camera.resolution = (w,h)
    camera.zoom = (0.4,0.4,0.6,0.6)
    
    # wait for capture signal
    while(!capture):
        capture = fun.wait()
    
    # once we are ready for capture, set off flash and capture sequence
    with Pool(2) as pool:
        bp = pool.apply_async(fun.capture_seq,buffer)
        fp = pool.apply_async(fun.sweep_LED)
        flash = fp.get()
        buffer = bp.get()
        
    # extract Y (grey scale) component and pad with zeros
    Y = [im[:w*h].reshape((h,w)) for im in buffer]
    Y = [np.pad(im,p,'constant',constant_values=0) for im in Y]
    logY = [np.log1p(im) for im in Y]

    #do the x and y components in parallel
    with Pool(2) as pool:
        imxp = pool.apply_async(fun.improcess,(logY,fx,fxr))
        imyp = pool.apply_async(fun.improcess,(logY,fy,fyr))
        imx = imxp.get()
        imy = imyp.get()

    im = imx+imy
    # this convolution takes the longest, g is very large
    # in future the image could be segmented and sections conv'd in parallel
    logR = signal.convolve(im,g,'same')

    # find the illuminance image
    logL = logY[0] - logR

    # create the shadow map
    smap = 255-gs(logL)
    #smap = smap*(smap>180)
    
    # resize image for shadow map
    smap = Image.resize(smap,(12 8))
    
    # drive LED array and capture image
    fun.drive_LED(smap)
    fun.capture_image()
    # close camera to avoid memeory issues
    camera.close()
    capture = False
    
    # plot for testing
    if plot:
        fig = plt.figure()
        fig.add_subplot(1,3,1)
        plt.imshow(Y[0], cmap=plt.cm.gray)
        fig.add_subplot(1,3,2)
        plt.imshow(np.exp(logR), cmap=plt.cm.gray)
        fig.add_subplot(1,3,3)
        plt.imshow(255-gs(logL), cmap=plt.cm.gray)
        plt.show()













    