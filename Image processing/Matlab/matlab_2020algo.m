clear all; close all;
pad = 3; 

% kernals
fx = [0 1 -1]; fy = [0; 1; -1];

fyr = flipud(fy); fxr = fliplr(fx);
path = dir(['iris\*.pgm']); n = numel(path);
im=2;
images = {}; logImages = {};

for i = 1:n/2
    image = imread([path(i).folder '\' path(i).name]);
    image = imresize(image, 0.2);
    image = padarray(image, [pad pad]); images{i} = image;
    %index = image == 0; image(index) = 1;
    image = log(double(image+1)); logImages{i} = image;
    % get dx and dy of images and put images into columns of X and Y
    imdx = conv2(image,fx,"same");  imdy = conv2(image,fy,"same");
    xEdges(:,i) = reshape(imdx, [],1); yEdges(:,i) = reshape(imdy, [], 1);
end
dims = size(image);
rx = median(xEdges,2); ry = median(yEdges,2);
rx = reshape(rx,dims);ry = reshape(ry,dims);

k = zeros(2*dims);
x = dims(1);y = dims(2);

k(x+1,y+1) = 4;
k(x+2,y+1) = -1; k(x-0,y+1) = -1;
k(x+1,y+2) = -1; k(x+1,y-0) = -1;

K = fft2(k); index = K==0; K(index) = 1; 
G = 1./K; G(index) = 0; g = real(ifft2(G));

imx = conv2(rx,fxr,'same');
imy = conv2(ry,fyr,'same'); 
ims = imx+imy;

logR = conv2(ims,g,'same');


logI = logImages{im};
logL = (logI) - (logR);


inv = 255-gs(logL);

% % 90% threshold
% [counts,binLocations]=imhist(inv);
% pixels = sum(counts); c=0;
% for i = 1:numel(counts)
%     c = c+counts(i);
%     if c > 0.90*pixels
%         break
%     end
% end
% thresh = inv.*uint8(inv>binLocations(i));


%Otsu Threshold
binary = imbinarize(inv,graythresh(inv));
thresh = inv.*uint8(binary);

figure(2);
montage({gs(thresh),gs(exp(logR)),gs(images{im})});






