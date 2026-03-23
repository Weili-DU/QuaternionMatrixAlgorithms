function synthesized_images = inverse_filter_synthesis(HH_new_quat, LL_cell, LH_cell, HL_cell, wname)
% INVERSE_FILTER_SYNTHESIS 逆滤波合成：将嵌入后的HH子带与原始LL, LH, HL子带合成彩色图像
%   输入:
%       HH_new_quat - 1×5 cell，嵌入隐秘信息后的HH子带（四元数矩阵形式）
%       LL_cell - 1×5 cell，原始LL子带（RGB图像，double类型）
%       LH_cell - 1×5 cell，原始LH子带（RGB图像，double类型）
%       HL_cell - 1×5 cell，原始HL子带（RGB图像，double类型）
%       wname - 小波基名称，如'haar', 'db4'等
%   输出:
%       synthesized_images - 1×5 cell，合成后的含隐秘信息彩色图像（uint8）

    num = length(HH_new_quat);
    synthesized_images = cell(1, num);
    
    for i = 1:num
        fprintf('正在合成第 %d 张图像...\n', i);
        
        %% 1. 将四元数矩阵形式的HH子带转换为RGB图像
        HH_rgb = quaternion_matrix_to_rgb(HH_new_quat{i});
        
        %% 2. 确保所有子带具有相同的尺寸
        % 由于四元数转换可能改变数据类型，确保所有子带为double类型
        LL = double(LL_cell{i});
        LH = double(LH_cell{i});
        HL = double(HL_cell{i});
        HH = double(HH_rgb);
        
        % 获取子带尺寸
        [h_ll, w_ll, ~] = size(LL);
        [h_hh, w_hh, ~] = size(HH);
        
        % 如果尺寸不一致，进行调整（通常HH子带大小是LL子带的一半）
        if h_hh ~= h_ll || w_hh ~= w_ll
            % 如果HH子带比LL子带小，需要插值放大
            if h_hh < h_ll && w_hh < w_ll
                HH = imresize(HH, [h_ll, w_ll], 'bilinear');
            % 如果HH子带比LL子带大，需要裁剪
            elseif h_hh > h_ll || w_hh > w_ll
                HH = HH(1:min(h_hh, h_ll), 1:min(w_hh, w_ll), :);
            end
        end
        
        %% 3. 对每个RGB通道分别进行逆小波变换
        R = idwt2_channel(LL(:,:,1), LH(:,:,1), HL(:,:,1), HH(:,:,1), wname);
        G = idwt2_channel(LL(:,:,2), LH(:,:,2), HL(:,:,2), HH(:,:,2), wname);
        B = idwt2_channel(LL(:,:,3), LH(:,:,3), HL(:,:,3), HH(:,:,3), wname);
        
        %% 4. 合并RGB通道
        synthesized = cat(3, R, G, B);
        
        %% 5. 裁剪并转换为uint8类型
        synthesized = max(0, min(255, synthesized));
        synthesized_images{i} = uint8(synthesized);
        
        fprintf('  第 %d 张图像合成完成，尺寸: %d×%d\n', i, size(synthesized,1), size(synthesized,2));
    end
end

function channel = idwt2_channel(LL, LH, HL, HH, wname)
% 对单个通道进行逆离散小波变换
% 输入: LL, LH, HL, HH - 四个子带（double类型）
% 输出: channel - 重构后的图像通道（double类型）

    % 执行逆DWT
    channel = idwt2(LL, LH, HL, HH, wname);
    
    % 处理可能的尺寸问题（idwt2可能返回比预期略大的矩阵）
    expected_h = size(LL, 1) * 2;
    expected_w = size(LL, 2) * 2;
    
    if size(channel, 1) > expected_h || size(channel, 2) > expected_w
        channel = channel(1:expected_h, 1:expected_w);
    elseif size(channel, 1) < expected_h || size(channel, 2) < expected_w
        % 如果尺寸偏小，填充零
        temp = zeros(expected_h, expected_w);
        temp(1:size(channel,1), 1:size(channel,2)) = channel;
        channel = temp;
    end
end