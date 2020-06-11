# for testing
import time

# required
import numpy as np
from scipy import signal
import RPi.GPIO as GPIO
from smbus2 import SMBus, i2c_msg 
from PCA_Constants import *

# consts
OE_PIN = 7

def capture_seq(camera,buffer,settings):
    # take a rapid sequence using video port
    
    t1 = time.time()
    #camera.start_preview()
    print("Image sequence starting: {}".format(t1))
    camera.capture_sequence(buffer, format='yuv', use_video_port=settings.video_port, burst=settings.burst)
    #camera.stop_preview()
    t2 = time.time()
    print("time taken for image sequence: {}'s".format(t2-t1))
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
    return g

# Enabling the PCA_Driver 
def enable_PCA():
    GPIO.output(OE_PIN,0)

# Disabling the PCA_Driver
def disable_PCA():
    GPIO.output(OE_PIN,1)

def initPCADriver(address,bus):
    # Initializing GPIO Stuff    
    if (not writePCARegister(address,MODE1,MODE1_DATA,bus)): 
        print("Test connections")
        return False
    if (not writePCARegister(address,PWMALL,0x00,bus)):
        print("Test connections")
        return False
    if (not writePCARegister(address,IREFALL,IREFALL_4MA,bus)):
        print("Test connections")
        return False
    else: return True
    
def init_LED_array(bus):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OE_PIN,GPIO.OUT)
    disable_PCA()
    for chip in [ADDR1,ADDR2,ADDR3,ADDR4]:
        if (not initPCADriver(chip,bus)):
            print("driver: {} init failed\n".format(chip))
    
    #if here then all settings wrote successfully
    # write them all to 0
    for chip in [ADDR1,ADDR2,ADDR3,ADDR4]:
        for i in range(24):
            writePCARegister(chip,0x0A+i,0,bus)
            
    enable_PCA()

def writePCARegister(chipAddr, regAddr, data,bus): 
    cmd = [regAddr|CTRL_NO_AIF, data]
    msg = i2c_msg.write(chipAddr|ADDR_WRITE,cmd)
    bus.i2c_rdwr(msg)
    return True
    
# sweeps led array light to get light variation    
def sweep_LED(intensity,bus):
    time.sleep(0.05)
    t1 = time.time()
    print("sweep starting: {}".format(t1))
    light_column(0,intensity,bus)
    for i in range(1,12):
        light_column(i-1,0,bus)
        light_column(i,intensity,bus)
        time.sleep(0.01)
    light_column(i,0,bus)
    t2 = time.time()
    print("time taken for sweep: {}'s".format(t2-t1))
    return True

def light_column(x1,intensity,bus):
        x2 = x1+12
        for chip in [ADDR1,ADDR2,ADDR3,ADDR4]:
            writePCARegister(chip,0x0A+x1,intensity,bus)
            writePCARegister(chip,0x0A+x2,intensity,bus)

# drives the shadow map to LED for shadow removal    
def drive_LED(smap):

    return True


# waits for camera to be pressed
def wait():
    yes = None
    while yes != "y":
        yes = input("Run? y for yes, crt-c for no \n")
    return True


# captures the final image
def capture_image():

    return True