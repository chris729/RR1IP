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

def capture_seq(buffer):
    # take a rapid sequence using video port
    print("Image sequence starting..........")
    t1 = time.time()
    camera.start_preview()
    camera.capture_sequence(buffer, format='yuv', use_video_port=video_port, burst=burst)
    camera.stop_preview()
    print("Sequence captured, calculating edges")
    return buffer
    
# normalize to 8-bit greyscale
def gs(im):
    im = im-im.min()
    im = 255*im/im.max()
    return np.uint8(im)

# function that does a major component of the image processing
def improcess(logY,f,fr):
    Edges = np.array([signal.convolve(im,f,mode='same') for im in logY])
    m = np.median(Edges,0)
    im = signal.convolve(m,fr,'same')
    return im
    
# computes g - the integration kernal
def calculate_g(h,w,p,dataType):    
    x,y = h+2*p,w+2*p
    a = np.zeros((2*x , 2*y), dtype=dataType)
    a[x+1,y+1] = 4
    a[x+2,y+1] = -1
    a[x-0,y+1] = -1
    a[x+1,y+2] = -1
    a[x+1,y-0] = -1
    A = np.fft.fft2(a)
    index = A==0
    A[index]=1
    G = 1/A
    G[index]=0
    g = np.real(np.fft.ifft2(G)) 
   
# waits for camera to be pressed
def wait():
    
    return True
    
# sweeps led array light to get light variation    
def sweep_LED():

    return True

# drives the shadow map to LED for shadow removal    
def drive_LED(smap):

    return True

# captures the final image
def capture_image():

    return True