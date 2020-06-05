clear all; close all;
pad = 3; 

% kernals
fx = [0 1 -1]; fy = [0; 1; -1];

fyr = flipud(fy); fxr = fliplr(fx);
path = 'C:\Users\cthom\OneDrive - The University of Melbourne\Documents\University\Capstone\shadow pics';
path = dir([path '\' 'iris\*.pgm']); n = numel(path);
im=2;
images = {}; logImages = {};

for i = 1:n
    image = imread([path(i).folder '\' path(i).name]);
    image = imresize(image,0.7);
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

% 90% threshold
[counts,binLocations]=imhist(inv);
pixels = sum(counts); c=0;
for i = 1:numel(counts)
    c = c+counts(i);
    if c > 0.90*pixels
        break
    end
end
thresh = inv.*uint8(inv>binLocations(i));


subplot(1,4,1); imshow(gs(images{1}))
subplot(1,4,2); imshow(gs(exp(logR)))
subplot(1,4,3); imshow(gs(logL))
subplot(1,4,4); imshow(gs(thresh))
% imresize(thresh, [8 12])

% subplot(5,4,1); imshow(gs(images{1}))
% subplot(5,4,2); imshow(gs(logImages{1}))
% subplot(5,4,3); imshow(abs((reshape(xEdges(:,1), dims))))
% subplot(5,4,4); imshow(abs((reshape(yEdges(:,1), dims))))
% 
% subplot(5,4,5); imshow(gs(images{3}))
% subplot(5,4,6); imshow(gs(logImages{3}))
% subplot(5,4,7); imshow(abs((reshape(xEdges(:,3), dims))))
% subplot(5,4,8); imshow(abs((reshape(yEdges(:,3), dims))))
% 
% subplot(5,4,9); imshow(gs(images{4}))
% subplot(5,4,10); imshow(gs(logImages{4}))
% subplot(5,4,11); imshow(abs((reshape(xEdges(:,4), dims))))
% subplot(5,4,12); imshow(abs((reshape(yEdges(:,4), dims))))
% 
% subplot(5,4,13); imshow(gs(images{7}))
% subplot(5,4,14); imshow(gs(logImages{7}))
% subplot(5,4,15); imshow(abs((reshape(xEdges(:,7), dims))))
% subplot(5,4,16); imshow(abs((reshape(yEdges(:,7), dims))))
% 
% subplot(5,4,17); imshow(gs(exp(logR)))
% subplot(5,4,18); imshow(gs(logR))
% subplot(5,4,19); imshow(abs(rx))
% subplot(5,4,20); imshow(abs(ry))


 figure(99);
% 
count = 1;
for i = [1,3,5,7,9,11,13,15]
    a = abs(reshape(xEdges(:,i),dims));
    subplot(2,8,count); imshow(a(290:480,90:210))
    b = abs(reshape(yEdges(:,i),dims));
    subplot(2,8,count+8); imshow(b(290:480,90:210))
count = count+1;
end

dxplot = abs(rx);
dyplot = abs(ry);
r = gs(exp(logR));
figure(100);
subplot(1,3,1); imshow(dxplot(290:480,90:210))
subplot(1,3,2); imshow(dyplot(290:480,90:210))
subplot(1,3,3); imshow(r(290:480,90:210))


subplot(1,2,1); imshow(images{1})
subplot(1,2,2); imshow(r)


n = thresh(180:420,10:280);
I = images{1};
I = I(180:420,10:280);
A = double(imresize(n, [8 12]));
fprintf([repmat(sprintf('%% %dd',max(floor(log10(abs(A(:)))))+2+any(A(:)<0)),1,size(A,2)) '\n'],A');
B = gs(A);
subplot(1,3,1); imshow(I)
subplot(1,3,2); imshow(n)
subplot(1,3,3); imshow(B)

