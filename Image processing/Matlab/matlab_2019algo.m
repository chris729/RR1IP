% import image
im = imread('iris.png');
im = imresize(im,0.4);
figure(1);imshow(im);

% Grey world algorithm
R = mean(im(:,:,1));
G = mean(im(:,:,2));
B = mean(im(:,:,3));
KB = (R + G + B) / (3 * B);
KG = (R + G + B) / (3 * G);
KR = (R + G + B) / (3 * R);
im(:,:,1) = im(:,:,1)*KR;
im(:,:,2) = im(:,:,2)*KG;
im(:,:,3) = im(:,:,3)*KB;
figure(2);imshow(im);

% skin mask
ycrcb = rgb2ycbcr(im);
cb = ycrcb(:,:,2);
cr = ycrcb(:,:,3);
cb_thresh = (cb>85 & cb<135);
cr_thresh = (cr>135 & cr<180);
mask = cb_thresh&cr_thresh;
figure(3);imshow(mask);

% binary mask
hsv = rgb2hsv(im);
binary = imbinarize(hsv(:,:,3),graythresh(hsv(:,:,3)));
figure(4);imshow(binary);

% final mask
finalmask = binary & mask;
finalmask = bitxor(finalmask, mask); 
figure(5);imshow(finalmask);
