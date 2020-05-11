function [X] = gs(X)
% this function converts a matrix X to an 8 bit greyscale image 
    X = double(X); 
    X = X - min(min(X));
    X = 255*(X/max(max(X)));
    X = uint8(X);
end

