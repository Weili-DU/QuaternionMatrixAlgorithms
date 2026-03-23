function [LL, LH, HL, HH] = dwt2_simple(img, wavelet_name)
% 简化的二维离散小波变换实现
% 如果MATLAB没有小波工具箱，使用这个替代函数

    [m, n] = size(img);
    
    % 简化的Haar小波变换
    if strcmpi(wavelet_name, 'haar')
        % 水平方向变换
        LL = (img(1:2:end, 1:2:end) + img(2:2:end, 1:2:end) + ...
              img(1:2:end, 2:2:end) + img(2:2:end, 2:2:end)) / 4;
        LH = (img(1:2:end, 1:2:end) + img(2:2:end, 1:2:end) - ...
              img(1:2:end, 2:2:end) - img(2:2:end, 2:2:end)) / 4;
        HL = (img(1:2:end, 1:2:end) - img(2:2:end, 1:2:end) + ...
              img(1:2:end, 2:2:end) - img(2:2:end, 2:2:end)) / 4;
        HH = (img(1:2:end, 1:2:end) - img(2:2:end, 1:2:end) - ...
              img(1:2:end, 2:2:end) + img(2:2:end, 2:2:end)) / 4;
    else
        % 默认使用简单的下采样
        LL = img(1:2:end, 1:2:end);
        LH = img(1:2:end, 2:2:end);
        HL = img(2:2:end, 1:2:end);
        HH = img(2:2:end, 2:2:end);
    end
end

function img_rec = idwt2_simple(LL, LH, HL, HH, wavelet_name)
% 简化的二维逆离散小波变换

    [m, n] = size(LL);
    img_rec = zeros(m*2, n*2);
    
    if strcmpi(wavelet_name, 'haar')
        % 简化的Haar小波逆变换
        for i = 1:m
            for j = 1:n
                img_rec(2*i-1, 2*j-1) = LL(i,j) + LH(i,j) + HL(i,j) + HH(i,j);
                img_rec(2*i-1, 2*j)   = LL(i,j) - LH(i,j) + HL(i,j) - HH(i,j);
                img_rec(2*i, 2*j-1)   = LL(i,j) + LH(i,j) - HL(i,j) - HH(i,j);
                img_rec(2*i, 2*j)     = LL(i,j) - LH(i,j) - HL(i,j) + HH(i,j);
            end
        end
    else
        % 默认使用简单的上采样
        img_rec(1:2:end, 1:2:end) = LL;
        img_rec(1:2:end, 2:2:end) = LH;
        img_rec(2:2:end, 1:2:end) = HL;
        img_rec(2:2:end, 2:2:end) = HH;
    end
end