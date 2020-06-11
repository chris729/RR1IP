# for testing
import time
import matplotlib.pyplot as plt

# required
import picamera
import numpy as np
from scipy import signal
from skimage.transform import resize
from multiprocessing import Pool
import functions as fun
from smbus2 import SMBus, i2c_msg 

t1 = time.time()
# image width/height settings for image processing
p = 2
bufferSize = 10
plot_seq = True
plot_results = True
capture = True
class cam_settings:
    scale = 2
    w,h = 64*scale,48*scale
    zoom = (0.2,0.2,0.3,0.3)
    video_port = True
    burst = True
    if video_port==True: burst=False # cannot use both..

# filter kernals
dataType = np.float32
fx = np.array([[0, 1, -1]],dtype=dataType)
fy = np.array([[ 0], 
               [ 1], 
               [-1]],dtype=dataType)

fxr = np.array([[-1, 1, 0]],dtype=dataType)
fyr = np.array([[-1], 
                [ 1], 
                [ 0]],dtype=dataType)

# pre-compute integrartion kernal
g = fun.calculate_g(cam_settings.h,cam_settings.w,p,dataType)

# init buffer 
buffer = [np.empty((cam_settings.h * cam_settings.w * 3), dtype=np.uint8) for _ in range(bufferSize)] 
t2 = time.time()
print("first init takes {}'s".format(t2-t1))
# main loop
while(True):
    t1 = time.time()
    # init camera and settings ready for each photo 
    camera = picamera.PiCamera()
    camera.resolution = (cam_settings.w,cam_settings.h)
    camera.zoom = cam_settings.zoom
    
    camera.start_preview()
    while(1):
        input()
        break
    camera.stop_preview()
    
    # init bus for LED array
    LED_array_bus = SMBus(1)
    fun.init_LED_array(LED_array_bus)
    t2 = time.time()
    print("second init takes {}'s".format(t2-t1))
    
    # wait for capture signal
    while(not capture):
        capture = fun.wait()
  
    # once we are ready for capture, set off flash and capture sequence
    pool = Pool(4)
    fp = pool.apply_async(fun.sweep_LED,(255,LED_array_bus))
    fun.capture_seq(camera,buffer,cam_settings)
    print("Processing images")
    t1 = time.time()
    # extract Y (grey scale) component and pad with zeros
    Y = [im[:cam_settings.w*cam_settings.h].reshape((cam_settings.h,cam_settings.w)) for im in buffer]
    Y = [np.pad(im,p,'constant',constant_values=0) for im in Y]
    logY = [np.log1p(im) for im in Y]

    #do the x and y components in parallel
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
    smap = 255-fun.gs(logL)
    smap = smap*(smap>180)
    
    # resize image for shadow map
    led_values = fun.gs(resize(smap,(8, 12)))
    
    t2 = time.time()
    print("images processed and sent to LED, time taken: {}'s".format(t2-t1))
    
    # drive LED array and capture image
    fun.drive_LED(led_values,LED_array_bus)
    fun.capture_image()
    # close camera to avoid memeory issues
    camera.close()
    LED_array_bus.close()
    pool.close()
    pool.join()
    capture = False
    
    # plot for testing
    if plot_seq:
        fig = plt.figure()
        for i,im in enumerate(Y):
            fig.add_subplot(4,4,i+1)
            plt.imshow(im, cmap=plt.cm.gray)
        plt.show()
    if plot_results:
        fig = plt.figure()
        fig.add_subplot(2,3,1)
        plt.imshow(Y[0], cmap=plt.cm.gray)
        plt.title("image 0")
        fig.add_subplot(2,3,2)
        plt.imshow(np.exp(logR), cmap=plt.cm.gray)
        plt.title("Reflectance")
        fig.add_subplot(2,3,3)
        plt.imshow(255-fun.gs(logL), cmap=plt.cm.gray)
        plt.title("Illuminance")
        fig.add_subplot(2,3,4)
        plt.imshow(fun.gs(logL), cmap=plt.cm.gray)
        plt.title("logL")
        fig.add_subplot(2,3,5)
        plt.imshow(smap, cmap=plt.cm.gray)
        plt.title("shadow map")
        fig.add_subplot(2,3,3)
        plt.imshow(led_values, cmap=plt.cm.gray)
        plt.title("LED_values")
        plt.show()
                
        
    ex = input("Quit? (y/n)\n")
    fun.disable_PCA()
    if ex == "n":
        pass
    else:
        break













    