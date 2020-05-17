# for testing
import time
import matplotlib.pyplot as plt

# required
import picamera
import numpy as np
from scipy import signal
from multiprocessing import Pool

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
    
# constants
imscale = 5
w = 32*imscale
h = 32*imscale
p = 2
bufferSize = 10
video_port = True
burst = True
if video_port==True: burst=False

# filter filter kernals
dataType = np.float32
fx = np.array([[0, 1, -1]],dtype=dataType)
fy = np.array([[ 0], 
               [ 1], 
               [-1]],dtype=dataType)

fxr = np.array([[-1, 1, 0]],dtype=dataType)
fyr = np.array([[-1], 
                [ 1], 
                [ 0]],dtype=dataType)


# --------- finding the re-integration matrix --------------
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
# ----------------------

# init camera and settings 
camera = picamera.PiCamera()
camera.resolution = (w,h)
camera.zoom = (0.4,0.4,0.6,0.6)
buffer = [np.empty((h * w * 3), dtype=np.uint8) for _ in range(bufferSize)] 

# -------------------------------- START OF IMAGE PROCESSING ----------------------

# take a rapid sequence using video port
print("Image sequence starting..........")
t1 = time.time()
#camera.start_preview()
camera.capture_sequence(buffer, format='yuv', use_video_port=video_port, burst=burst)
#camera.stop_preview()
print("Sequence captured, calculating edges")

# extract Y (grey scale) component and pad with zeros
Y = [im[:w*h].reshape((h,w)) for im in buffer]
Y = [np.pad(im,p,'constant',constant_values=0) for im in Y]
logY = [np.log1p(im) for im in Y]

# tt1 = time.time()
#do the x and y components in parallel
with Pool(2) as pool:
    imxp = pool.apply_async(improcess,(logY,fx,fxr))
    imyp = pool.apply_async(improcess,(logY,fy,fyr))
    imx = imxp.get()
    imy = imyp.get()

# tt2 = time.time()
# print("Improcess || time taken: " + str(tt2-tt1) + "s")

# sequencially
# tt1 = time.time()
# imx = improcess(logY,fx,fxr)
# imy = improcess(logY,fy,fyr)
# tt2 = time.time()
# print("Improcess >> time taken: " + str(tt2-tt1) + "s")

im = imx+imy
# this convolution takes the longest, g is very large
logR = signal.convolve(im,g,'same')

# find the illuminance image
logL = logY[0] - logR

# create the shadow map
smap = 255-gs(logL)
smap = smap*(smap>180)

t2 = time.time()
print("Time taken: " + str(t2-t1) + "s")

fig = plt.figure()
fig.add_subplot(1,3,1)
plt.imshow(Y[0], cmap=plt.cm.gray)

fig.add_subplot(1,3,2)
plt.imshow(np.exp(logR), cmap=plt.cm.gray)

fig.add_subplot(1,3,3)
plt.imshow(255-gs(logL), cmap=plt.cm.gray)

plt.show()




