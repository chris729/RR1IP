#include "original2019.h"


#include <chrono>
using namespace std::chrono;

Mat binary;
Mat binary_not;
Mat mask;
Mat dst;
Mat finalmask;
Mat gray;
Mat hsv;
vector<Mat> mv;
Scalar meanvalue;

/*************************************************
Function: improcess

Description: The main body of mapping algorithm

Input: img is the location of input image.

Output: Intensity matrix

*************************************************/
Mat improcess(char *location) {

	printf("Processing image from: %s\n", location);
	Mat src = imread(location);
	vector<Mat> imageRGB;
	split(src, imageRGB);

	double R, G, B;
	B = mean(imageRGB[0])[0];
	G = mean(imageRGB[1])[0];
	R = mean(imageRGB[2])[0];

	double KR, KG, KB;
	KB = (R + G + B) / (3 * B);
	KG = (R + G + B) / (3 * G);
	KR = (R + G + B) / (3 * R);

	imageRGB[0] = imageRGB[0] * KB;
	imageRGB[1] = imageRGB[1] * KG;
	imageRGB[2] = imageRGB[2] * KR;

	merge(imageRGB, src);
    //src = src(Rect(src.cols / 2.7, src.rows / 4, src.cols / 4, src.rows / 1.85));
	Mat finalmask = ImageProcess_func(src);
 	
	return finalmask;
}


Mat ImageProcess_func(Mat &src) {
	

	cvtColor(src, gray, COLOR_BGR2GRAY); //灰度图单通道
	cvtColor(src, hsv, COLOR_BGR2HSV); //3通道HSV
	
	vector<Mat> mv;
	split(hsv, mv);
	Scalar meanvalue = mean(mv[2]);

	binary = Mat::zeros(gray.size(), gray.type());
	mask = Mat::zeros(gray.size(), gray.type());

	generateSkinMask(src);
	convert2Binary(mv[2], 2);
	
	dst = Mat::zeros(binary.size(), CV_8UC1);
	finalmask = Mat::zeros(binary.size(), CV_8UC1);


	bitwise_and(binary, mask, dst);
	bitwise_xor(dst, mask, finalmask);
	
	return finalmask;

}
/*************************************************
Function: diagIntensity

Description: Calculation of intensity for each block which has
one corresponding LED

Input: img is the shadow image.
		a is the beginning row index of the block
		b is the beginning column index of the block
		w is the width of whole image
		h is the height of whole image

Output: The intensity value of this particular block

*************************************************/
double diagIntensity(Mat &img, int a, int b, int w, int h)

{
	Rect region_of_interest = Rect(a, b, w, h);
	Mat dst = img(region_of_interest);
	//Mat dst = img.clone();
	Scalar scalar = mean(dst);//Scalar，求像素均值
	return scalar.val[0]; //使用的图像是1通道的，则scalar.val[0]中存储数据


}

/*************************************************
Function: Intensityfactor

Description: Compare the intensity of each block with overall light condition 

Input: img is the shadow image.
		a is the beginning row index of the block
		b is the beginning column index of the block
		w is the width of whole image
		h is the height of whole image

Output: The intensity factor for particular block

*************************************************/
float Intensityfactor(Mat &factor, int a, int b, int w, int h)
{
	float x;
	Rect region_of_interest = Rect(a, b, w, h);
	Mat dst = factor(region_of_interest);
	Scalar scalar = mean(dst);//Scalar，求像素均值
	if (meanvalue.val[0] > scalar.val[0]) {
		x = 1.2;
	}
	else {
		x = 0.9;
	}

	return x;//使用的图像是1通道的，则scalar.val[0]中存储数据


}

/*************************************************
Function: diagToArray

Description: Transform shadow image to intensity weight
			 matrix

Input: img is the shadow image.
		A is the intensity matrix that we want

Output: None

*************************************************/
void diagramToArray(Mat &img, Mat &factor,int offset, double *A)
{
	
	int led_width = 12;
	int led_height = 8;
	int w = img.cols / led_width;
	int h = img.rows / led_height;//分成96块

	printf("Intensity Matrix:\n");
	
	for (int i = 0; i < led_height; i++)
	{
		for (int j = 0; j < led_width; j++)
		{
			// printf("%f\n", diagIntensity(img, w*j, h*i, w, h));
			// printf("%d\n", (int)diagIntensity(img, w*j, h*i, w, h));
			float x = Intensityfactor(factor, w*j, h*i, w, h);
			//A[led_width * i + j] = x * diagIntensity(img, w*j, h*i, w, h) + offset;//
            A[led_width * i + j] = x * diagIntensity(img, w*j, h*i, w, h) ;
			if (A[led_width * i + j]>255){
                A[led_width * i + j]=255;
            }
            printf("%3d ", (int)A[led_width * i + j]);
		}
		printf("\n");
	}
}


/*************************************************
Function: Get Skin Mask

Description: generate Skin Mask algorithm

Input: image is the input image.

Output: mask 

*************************************************/
Mat generateSkinMask(Mat &image) {
	int w = image.cols;
	int h = image.rows;
	Mat ycrcb;
	cvtColor(image, ycrcb, COLOR_BGR2YCrCb);

	for (int row = 0; row < h; row++) {
		for (int col = 0; col < w; col++) {
			int y = ycrcb.at<Vec3b>(row, col)[0];  //vector 3个元素 b为uchar
			int cr = ycrcb.at<Vec3b>(row, col)[1];
			int cb = ycrcb.at<Vec3b>(row, col)[2];
			// skin detect
			if ((cb > 85 && cb < 135) && (cr > 135 && cr < 180)) {
				mask.at<uchar>(row, col) = 255; //白色
			}
			else {
				mask.at<uchar>(row, col) = 0;
			}
		}
	}
	return mask;
}

/*************************************************
Function: Get Binary figure

Description: Transfer grayscale figure to binary figure with 5 different threshold finding methods 

Input: gray is the input image, method is the selection of threshold

Output: binary figure

*************************************************/
Mat convert2Binary(Mat &gray, int method) {
	int w = gray.cols;
	int h = gray.rows;

	if (method == 1) {
		Scalar s = mean(gray);
		int m = s[0];
		printf("current threshold value: %d", m);
		int pv = 0;
		for (int row = 0; row < h; row++) {
			for (int col = 0; col < w; col++) {
				pv = gray.at<uchar>(row, col);
				if (pv > m) {
					binary.at<uchar>(row, col) = 255;
				}
				else {
					binary.at<uchar>(row, col) = 0;
				}
			}
		}

	}
	else if (method == 2) {
		threshold(gray, binary, 0, 255, THRESH_BINARY | THRESH_OTSU);
		threshold(gray, binary_not, 0, 255, THRESH_BINARY_INV | THRESH_OTSU);
	}
	else if (method == 3) {
		threshold(gray, binary, 0, 255, THRESH_BINARY | THRESH_TRIANGLE);
	}
	else if (method == 4) {
		adaptiveThreshold(gray, binary, 255, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY_INV, 25, 5);

	}
	else if (method == 5) {
		adaptiveThreshold(gray, binary, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, 25, 10);
	}
	return binary;
	
}

//sudo g++ `pkg-config --cflags opencv` original2019.cpp `pkg-config --libs opencv` -o improcess_original

int main(int argc, char **argv) {
	char *image_path = (char*) "/home/pi/Downloads/input.JPG";
	int lightinfo = 100;						//Stores light reading result from socket connection with sensor
	double led_light[96] = {0};				//To hold LED Matrix string display on terminal
	
	auto start = high_resolution_clock::now();
	
	Mat img = imread(image_path);
	Mat mask = improcess(image_path);
	
	auto stop = high_resolution_clock::now();
	auto duration = duration_cast<milliseconds>(stop-start);
	
	cout << "Time taken: " << duration.count() << " ms" << endl;
	
	imwrite("/home/pi/Downloads/mask.jpg",finalmask); 
	
	namedWindow("original",CV_WINDOW_AUTOSIZE);
	namedWindow("mask",CV_WINDOW_AUTOSIZE);
	imshow("original",img);
	imshow("mask",mask);
	waitKey(0);
}
