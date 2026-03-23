function [LL, LH, HL, HH] = dwt2_color(rgb, wname)
% 对彩色图像的每个通道进行二维离散小波变换
    R = rgb(:,:,1);
    G = rgb(:,:,2);
    B = rgb(:,:,3);

    [LL_R, LH_R, HL_R, HH_R] = dwt2(R, wname);
    [LL_G, LH_G, HL_G, HH_G] = dwt2(G, wname);
    [LL_B, LH_B, HL_B, HH_B] = dwt2(B, wname);

    LL = cat(3, LL_R, LL_G, LL_B);
    LH = cat(3, LH_R, LH_G, LH_B);
    HL = cat(3, HL_R, HL_G, HL_B);
    HH = cat(3, HH_R, HH_G, HH_B);
end

function rgb = idwt2_color(LL, LH, HL, HH, wname)
% 对彩色图像的每个通道进行逆二维离散小波变换
    R = idwt2(LL(:,:,1), LH(:,:,1), HL(:,:,1), HH(:,:,1), wname);
    G = idwt2(LL(:,:,2), LH(:,:,2), HL(:,:,2), HH(:,:,2), wname);
    B = idwt2(LL(:,:,3), LH(:,:,3), HL(:,:,3), HH(:,:,3), wname);

    % 确保尺寸一致（idwt2 可能返回略大的矩阵，需要裁剪）
    target_size = [size(LL,1)*2, size(LL,2)*2];
    R = R(1:target_size(1), 1:target_size(2));
    G = G(1:target_size(1), 1:target_size(2));
    B = B(1:target_size(1), 1:target_size(2));

    rgb = cat(3, R, G, B);
end