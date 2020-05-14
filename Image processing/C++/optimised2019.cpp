#include "optimised2019.h"

//sudo g++ -Wall `pkg-config --cflags opencv` optimised2019.cpp `pkg-config --libs opencv` -o imp -pthread

void im_mean(vector<Mat> const &im, double const &in,int col){
	double &out = const_cast<double &>(in);
	out = mean(im[col])[0];
}

void grey_world(vector<Mat> const &im, double R, double G, double B, int col){
	double val;
	vector<Mat> &imageRGB = const_cast<vector<Mat> &>(im);
	
	switch (col)
	{
		case 0 : val = B; break;
		case 1 : val = G; break;
		case 2 : val = R; break;	
	}
	
	double K = (R + G + B) / (3 * val);
	imageRGB[col] = K*imageRGB[col];
}

void skin_mask(Mat src, Mat const &in){
	cv::Size size = src.size();
	Mat &mask = const_cast<Mat &>(in);
	int w = src.cols;
	int h = src.rows;
	
	Mat ycrcb = Mat::zeros(size, CV_8U);
	cvtColor(src, ycrcb, COLOR_BGR2YCrCb);
		
	for (int row = 0; row < h; row++) {
		for (int col = 0; col < w; col++) { 
			int cr = ycrcb.at<Vec3b>(row, col)[1];
			int cb = ycrcb.at<Vec3b>(row, col)[2];
			// skin detect
			if ((cb > 85 && cb < 135) && (cr > 135 && cr < 180)) {
				mask.at<uchar>(row, col) = 255;
			}
			else {
				mask.at<uchar>(row, col) = 0;
			}
		}
	}
}

void binary_mask(Mat src, Mat const &in){
	cv::Size size = src.size();
	Mat &binary = const_cast<Mat &>(in);
	vector<Mat> mv;
	Mat hsv = Mat::zeros(size, CV_8U);
	cvtColor(src, hsv, COLOR_BGR2HSV);
	split(hsv, mv);
	threshold(mv[2], binary, 0, 255, THRESH_BINARY | THRESH_OTSU);
}

int main(int argc, char **argv) {
	// image path
	char *image_path = (char*) "/home/pi/Downloads/input.JPG";
	
	// start timer
	cout << "Timing Chris's optimised image processing algo" << endl;
	auto start = high_resolution_clock::now();
		
	// import image and resize
	Mat src = imread(image_path);
	//cv::resize(src,src,cv::Size(),0.3,0.3);
	cv::Size size = src.size();
	
	// Split RGB to run grey world algo
	double R, G, B;
	vector<Mat> imageRGB;
	split(src, imageRGB);
	
	// mean of matrix is now done in threads
	thread meanB(im_mean,imageRGB,ref(B),0);
	thread meanG(im_mean,imageRGB,ref(G),1);
	thread meanR(im_mean,imageRGB,ref(R),2);
	
	Mat mask = Mat::zeros(size, CV_8U);

	meanB.join();
	meanG.join();
	meanR.join();
	
	// next using the average RGB vals impliment grey world algo in parallel
	thread GWB(grey_world,ref(imageRGB),R,G,B,0);
	thread GWG(grey_world,ref(imageRGB),R,G,B,1);
	thread GWR(grey_world,ref(imageRGB),R,G,B,2);
	
	Mat binary = Mat::zeros(size, CV_8U);

	GWB.join();
	GWG.join();
	GWR.join();
	
	// merge back into one image	
	merge(imageRGB, src);
	
	// Start new thread for skin mask
	thread SM(skin_mask, src, ref(mask));

	// Start a thread for binary mask
	thread BM(binary_mask, src, ref(binary));
	
	Mat dst = Mat::zeros(size, CV_8U);
	Mat finalmask = Mat::zeros(size, CV_8U);

	// join threads
	SM.join();
	BM.join();
	
	// bitwise operations to create final mask
	bitwise_and(binary, mask, dst);
	bitwise_xor(dst, mask, finalmask);
	
	auto stop = high_resolution_clock::now();
	auto duration = duration_cast<milliseconds>(stop-start);
	
	cout << "Time taken: " << duration.count() << " ms" << endl;
	
	imwrite("/home/pi/Downloads/mask_opt.jpg",finalmask); 
	//namedWindow("original",CV_WINDOW_AUTOSIZE);
	//namedWindow("finalmask",CV_WINDOW_AUTOSIZE);
	//imshow("original",src);
	//imshow("finalmask",finalmask);
	//waitKey(0);
}
