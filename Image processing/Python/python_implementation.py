from skimage import io,restoration
from skimage.transform import resize
import numpy as np
import matplotlib.pyplot as plt
from sklearn import decomposition
from scipy.signal import convolve2d as conv2
from scipy.signal import convolve as conv
import glob

def show(im):
    plt.imshow(im,cmap=plt.cm.gray)

def gs(im):
    im = im-im.min()
    im = 255*im/im.max()
    return np.uint8(im)
 
pad = 3
precision = np.float64

fx = np.array([[0, 1, -1]],dtype=precision)
fy = np.array([[0], [1], [-1]],dtype=precision)
fxr = np.array([[-1, 1, 0]],dtype=precision)
fyr = np.array([[-1], [1], [0]],dtype=precision)

path = glob.glob("images/*.pgm")

images = []
logImages = []
for im in path:
    temp = io.imread(im,as_gray = True)
    temp = resize(temp,(250,250))
    temp = np.pad(temp,pad,'constant',constant_values=0)
    images.append(temp)
    temp = np.log1p(temp,dtype=precision)
    logImages.append(temp)  

xEdges = np.zeros((temp.size,len(path)))
yEdges = np.zeros((temp.size,len(path)))
dims = temp.shape

for i,im in enumerate(logImages):
    dx = conv2(im,fx,'same')
    xEdges[:,i] = np.reshape(dx,(1,im.size))
    dy = conv2(im,fy,'same')
    yEdges[:,i] = np.reshape(dy,(1,im.size))

rx = np.median(xEdges,1)
ry = np.median(yEdges,1)
rx = np.reshape(rx,dims)
ry = np.reshape(ry,dims)   


x = dims[0]
y = dims[1]

k = np.zeros((2*x,2*y),dtype=precision)
k[x+1,y+1] = 4
k[x+2,y+1] = -1
k[x-0,y+1] = -1
k[x+1,y+2] = -1
k[x+1,y-0] = -1

K = np.fft.fft2(k) 
I = K==0 
K[I] = 1
G = 1/K
G[I] = 0
g = np.real(np.fft.ifft2(G))


imx = conv2(rx,fxr,'same')
imy = conv2(ry,fyr,'same')
ims = imx+imy
# calculate new image
logR = conv2(ims,g,'same')
#show(gs(logR))
#R = np.exp(logR)
#show(gs(R))
logL = logImages[0] - logR

smap = 255-gs(logL)
smap = smap*(smap>180)
show(smap)


