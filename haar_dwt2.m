function [LL, LH, HL, HH] = haar_dwt2(img)
    % 确保图像尺寸为偶数
    [rows, cols] = size(img);
    if mod(rows, 2) ~= 0
        img = img(1:end-1, :);
        rows = rows - 1;
    end
    if mod(cols, 2) ~= 0
        img = img(:, 1:end-1);
        cols = cols - 1;
    end
    
    % 水平方向变换
    img_h = zeros(rows, cols);
    for i = 1:rows
        for j = 1:2:cols
            avg = (double(img(i,j)) + double(img(i,j+1)))/2;
            diff = (double(img(i,j)) - double(img(i,j+1)))/2;
            img_h(i,j) = avg;
            img_h(i,j+1) = diff;
        end
    end
    
    % 垂直方向变换
    img_v = zeros(rows, cols);
    for j = 1:cols
        for i = 1:2:rows
            avg = (img_h(i,j) + img_h(i+1,j))/2;
            diff = (img_h(i,j) - img_h(i+1,j))/2;
            img_v(i,j) = avg;
            img_v(i+1,j) = diff;
        end
    end
    
    % 提取子带
    LL = img_v(1:2:end, 1:2:end);
    LH = img_v(1:2:end, 2:2:end);
    HL = img_v(2:2:end, 1:2:end);
    HH = img_v(2:2:end, 2:2:end);
end