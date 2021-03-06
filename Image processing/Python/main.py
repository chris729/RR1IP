# for testing
import time
t1 = time.time()
import matplotlib.pyplot as plt

# required
import picamera
import numpy as np
from scipy import signal
from skimage.transform import resize
from multiprocessing import Pool
import functions as fun
from smbus2 import SMBus, i2c_msg
import gphoto2 as gp
import os

# kill off any gphoto process from startup
os.system('pkill -f gphoto2')
# setting config is much easier with CLI than python interface so we do it here
# should also add standard passport photo settings here so it's all automated
os.system('gphoto2 --set-config capturetarget=1')

# image width/height settings for image processing
p = 2
bufferSize = 8
plot_seq = True
plot_results = True
class cam_settings:
    # increase scale for plotting high res images for testing, slows processing down
    scale = 5
    w,h = 64*scale,48*scale
    zoom = (0.25,0.25,0.35,0.35)
    rotation = 180
    video_port = True
    # if we dont want to use video port we will use burst setting
    if video_port==True: burst=False 
    else: burst = True

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

# pre-compute integrartion kernal, depends only on image size and filter kernals
g = fun.calculate_g(cam_settings.h,cam_settings.w,p,dataType)

# init buffer 
buffer = [np.empty((cam_settings.h * cam_settings.w * 3), dtype=np.uint8) for _ in range(bufferSize)] 
t2 = time.time()
print("first init takes {}'s".format(t2-t1))

# main loop
while(True):
    t1 = time.time()
    # init camera and settings ready for each photo 
    picam = picamera.PiCamera()
    picam.resolution = (cam_settings.w,cam_settings.h)
    picam.zoom = cam_settings.zoom
    picam.rotation = cam_settings.rotation
    Cannon = gp.Camera()
    Cannon.init()
        
    # init bus for LED array
    LED_array_bus = SMBus(1)
    fun.init_LED_array(LED_array_bus)
    t2 = time.time()
    print("second init takes {}'s".format(t2-t1))   
    
    # wait for trigger, show camera preview for aligning picam and array
    picam.start_preview()
    fun.wait()
    picam.stop_preview()

    # take photo to compare result
    im1 = fun.capture_image(Cannon)  

    # once we are ready for capture, set off flash and capture sequence
    t0 = time.time()
    pool = Pool(4)
    fp = pool.apply_async(fun.sweep_LED,(100,LED_array_bus))
    fun.capture_seq(picam,buffer,cam_settings)
    t1 = time.time()
    # extract Y (grey scale) component and pad with zeros before filtering
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
    # need more adaptive threshold
    smap = smap*(smap>140)
    
    # resize image for shadow map
    led_values = fun.gs(resize(np.uint8(smap),(8, 12)))
    # reduce brightness by 0% before lighting up
    led_values = np.uint8(led_values - 0*led_values)
    t2 = time.time()
    print("Time for shadow detection: {}'s".format(t2-t1))
    
    # drive LED array and capture image
    t1 = time.time()
    fun.drive_LED(led_values,LED_array_bus)
    im2 = fun.capture_image(Cannon)
    fun.disable_PCA()
    t2 = time.time()
    print("Time for shadow removal and image capture: {}'s".format(t2-t1))
    print(led_values)
    # close camera to avoid memeory issues
    
    tend = time.time()
    print("Time from trigger to result: {}'s".format(tend-t0))
    picam.close()
    LED_array_bus.close()
    pool.close()
    pool.join()
    Cannon.exit()
    
    # plot for testing
    if plot_seq:
        fig = plt.figure()
        for i,im in enumerate(Y):
            fig.add_subplot(4,4,i+1)
            plt.imshow(im, cmap=plt.cm.gray)
        plt.show()
        fig.savefig("sequence")
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
        fig.savefig("results")
                
        
    ex = input("Quit? (y/n)\n")
    if ex == "n":
        pass
    else:
        # if existing get the two latest photos for comparison
        os.system('gphoto2 --get-file '+im1.folder+'/'+im1.name)
        os.system('gphoto2 --get-file '+im2.folder+'/'+im2.name)
        break











    