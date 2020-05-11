/***************************************************************
Copyright 2019, Hankun Xue, All rights reserved.

Author: Hankun Xue

Date: February 27, 2019

Description: This is the implementation of the shadow detection
algorithm with skin detection.
****************************************************************/
//Based on Opencv C++ API

#include <opencv2/opencv.hpp>
#include <iostream>
#include <opencv2/highgui/highgui.hpp>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <chrono>
#include <thread>

#define FIFO_PATH_IN "/tmp/fifo_data"
#define FIFO_PATH_OUT "/tmp/fifo_cmd"

#define GENERATE_OUTPUT 0

using namespace std;
using namespace cv;
using namespace std::chrono;
