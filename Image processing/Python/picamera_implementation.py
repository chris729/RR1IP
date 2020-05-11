# for testing
import time
import matplotlib.pyplot as plt

# required
import picamera
import numpy as np
from scipy import signal

# normalize to 8-bit greyscale
def gs(im):
    im = im-im.min()
    im = 255*im/im.max()
    return np.uint8(im)
    
t1 = time.time()
# constants
imscale = 3
w = 32*imscale
h = 32*imscale
p = 2
bufferSize = 10

video_port = False
burst = True


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

 
# init camera and settings 
camera = picamera.PiCamera()
camera.resolution = (w,h)
camera.zoom = (0.4,0.4,0.6,0.6)
# take a rapid sequence using video port
buffer = [np.empty((h * w * 3), dtype=np.uint8) for _ in range(bufferSize)] 

print("Image equence starting..........")
camera.start_preview()
camera.capture_sequence(buffer, format='yuv', use_video_port=video_port, burst=burst)
camera.stop_preview()
print("Sequence captured, calculating edges")

# extract Y component and pad with zeros
Y = [im[:w*h].reshape((h,w)) for im in buffer]
Y = [np.pad(im,p,'constant',constant_values=0) for im in Y]
logY = [np.log1p(im) for im in Y]

# take the edge maps of the images
xEdges = np.array([signal.convolve2d(im,fx,mode='same') for im in logY])
yEdges = np.array([signal.convolve2d(im,fy,mode='same') for im in logY])

# get the median of the images for shadowless version
mx = np.median(xEdges,0)
my = np.median(yEdges,0)

# now we need to re-intergrate the image using the method shown by Weiss

# --------- this can and will be computed offline --------------
a = np.zeros((2*(h+2*p) , 2*(w+2*p)), dtype=dataType)
x,y = mx.shape[0],mx.shape[1]
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
# --------- this can and will be computed offline --------------


# reconstruct the shadowless image
print("Median edges calculated, reconstructing image")

imx = signal.convolve2d(mx,fxr,'same')
imy = signal.convolve2d(my,fyr,'same')
im = imx+imy
logR = signal.convolve2d(im,g,'same')

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




