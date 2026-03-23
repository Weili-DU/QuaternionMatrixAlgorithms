function [embedded_images, keys] = embed_quaternion_images_complete(cover_images, secret_images, alpha)
% EMBED_QUATERNION_IMAGES_COMPLETE 完整的四元数图像隐写嵌入函数
%   输入:
%       cover_images - 1x5 cell，每个元素是 m×n×3 的 uint8 彩色图像（载体）
%       secret_images - 1x5 cell，每个元素是 p×q×3 的 uint8 彩色图像（隐秘信息）
%       alpha - 1x5 double，嵌入强度系数
%   输出:
%       embedded_images - 1x5 cell，嵌入后的彩色图像（uint8）
%       keys - 1x5 cell，每个元素是实数矩阵（密钥，即重构后的实部）

    num = 5;
    assert(length(cover_images) == num && length(secret_images) == num, ...
           '必须提供5个载体图像和5个隐秘信息图像');
    assert(length(alpha) == num, 'alpha 必须为5个元素的向量');

    fprintf('开始四元数图像隐写嵌入...\n');
    
    %% 1. 对每个载体图像进行 DWT，保存子带
    fprintf('步骤1: 对载体图像进行DWT分解...\n');
    LL_cell = cell(1, num);
    LH_cell = cell(1, num);
    HL_cell = cell(1, num);
    HH_cell = cell(1, num);

    for i = 1:num
        [LL, LH, HL, HH] = dwt2_color_simple(cover_images{i});
        LL_cell{i} = LL;
        LH_cell{i} = LH;
        HL_cell{i} = HL;
        HH_cell{i} = HH;
    end

    %% 2. 将 HH 子带转换为四元数矩阵（实部为0）
    fprintf('步骤2: 转换HH子带到四元数矩阵...\n');
    HH_quat = cell(1, num);
    for i = 1:num
        HH_quat{i} = rgb_to_quaternion_matrix_simple(HH_cell{i});
    end

    %% 3. 五个四元数矩阵同时分解（简化实现）
    fprintf('步骤3: 四元数矩阵分解...\n');
    [M_cell, S_cell] = five_quaternion_decomposition_simple(HH_quat);

    %% 4. 准备隐秘信息：调整大小并转换为四元数矩阵（实部为0）
    fprintf('步骤4: 准备隐秘信息...\n');
    W_quat = cell(1, num);
    for i = 1:num
        % 获取当前 HH 子带的大小
        target_size = [size(HH_quat{i}, 1), size(HH_quat{i}, 2)];
        secret = secret_images{i};
        % 如果尺寸不一致，调整隐秘图像大小
        if ~isequal([size(secret,1), size(secret,2)], target_size)
            secret = imresize(secret, target_size);
        end
        W_quat{i} = rgb_to_quaternion_matrix_simple(secret);
    end

    %% 5. 嵌入隐秘信息
    fprintf('步骤5: 嵌入隐秘信息...\n');
    S_new_cell = cell(1, num);
    HH_new_quat = cell(1, num);
    keys = cell(1, num);

    for i = 1:num
        % 嵌入：S_new = S_original + alpha * W
        S_new_cell{i} = quaternion_matrix_add(S_cell{i}, quaternion_matrix_scale(W_quat{i}, alpha(i)));

        % 重构 HH' = M_{i-1} * S_new * M_i^{-1}
        temp = quaternion_matrix_multiply(quaternion_matrix_multiply(M_cell{i}, S_new_cell{i}), ...
                                         quaternion_matrix_inverse_simple(M_cell{i+1}));

        % 提取虚部作为新的 HH 子带（四元数矩阵，实部为0）
        HH_new_quat{i} = imag_quaternion_matrix_simple(temp);

        % 提取实部作为密钥
        keys{i} = real_quaternion_matrix_simple(temp);
    end

    %% 6. 将新的 HH 子带从四元数转换回 RGB 图像
    fprintf('步骤6: 转换四元数矩阵回RGB...\n');
    HH_new_rgb = cell(1, num);
    for i = 1:num
        HH_new_rgb{i} = quaternion_matrix_to_rgb_simple(HH_new_quat{i});
    end

    %% 7. 逆 DWT 得到嵌入后的载体图像
    fprintf('步骤7: 逆DWT重构图像...\n');
    embedded_images = cell(1, num);
    for i = 1:num
        img_rec = idwt2_color_simple(LL_cell{i}, LH_cell{i}, HL_cell{i}, HH_new_rgb{i});
        % 裁剪到有效范围并转换为 uint8
        img_rec = max(0, min(255, img_rec));
        embedded_images{i} = uint8(img_rec);
    end

    fprintf('四元数图像隐写嵌入完成！\n');
end

%% ==================== 辅助函数 ====================

function [LL, LH, HL, HH] = dwt2_color_simple(rgb)
% 简化的彩色图像DWT变换
    % 转换为double类型
    if isa(rgb, 'uint8')
        rgb = double(rgb);
    end
    
    R = rgb(:,:,1);
    G = rgb(:,:,2);
    B = rgb(:,:,3);

    % 检查是否有小波工具箱，如果没有则使用简化版本
    if exist('dwt2', 'file') == 2
        [LL_R, LH_R, HL_R, HH_R] = dwt2(R, 'haar');
        [LL_G, LH_G, HL_G, HH_G] = dwt2(G, 'haar');
        [LL_B, LH_B, HL_B, HH_B] = dwt2(B, 'haar');
    else
        % 使用简化版本
        [LL_R, LH_R, HL_R, HH_R] = dwt2_simple(R, 'haar');
        [LL_G, LH_G, HL_G, HH_G] = dwt2_simple(G, 'haar');
        [LL_B, LH_B, HL_B, HH_B] = dwt2_simple(B, 'haar');
    end

    LL = cat(3, LL_R, LL_G, LL_B);
    LH = cat(3, LH_R, LH_G, LH_B);
    HL = cat(3, HL_R, HL_G, HL_B);
    HH = cat(3, HH_R, HH_G, HH_B);
end

function rgb = idwt2_color_simple(LL, LH, HL, HH)
% 简化的彩色图像逆DWT变换
    % 检查是否有小波工具箱，如果没有则使用简化版本
    if exist('idwt2', 'file') == 2
        R = idwt2(LL(:,:,1), LH(:,:,1), HL(:,:,1), HH(:,:,1), 'haar');
        G = idwt2(LL(:,:,2), LH(:,:,2), HL(:,:,2), HH(:,:,2), 'haar');
        B = idwt2(LL(:,:,3), LH(:,:,3), HL(:,:,3), HH(:,:,3), 'haar');
    else
        % 使用简化版本
        R = idwt2_simple(LL(:,:,1), LH(:,:,1), HL(:,:,1), HH(:,:,1), 'haar');
        G = idwt2_simple(LL(:,:,2), LH(:,:,2), HL(:,:,2), HH(:,:,2), 'haar');
        B = idwt2_simple(LL(:,:,3), LH(:,:,3), HL(:,:,3), HH(:,:,3), 'haar');
    end

    % 确保尺寸一致
    target_size = [size(LL,1)*2, size(LL,2)*2];
    R = R(1:target_size(1), 1:target_size(2));
    G = G(1:target_size(1), 1:target_size(2));
    B = B(1:target_size(1), 1:target_size(2));

    rgb = cat(3, R, G, B);
end

function Q = rgb_to_quaternion_matrix_simple(rgb_image)
% 简化的RGB到四元数矩阵转换
    if isa(rgb_image, 'uint8')
        rgb_image = double(rgb_image);
    end
    
    [m, n, ~] = size(rgb_image);
    Q = zeros(m, n, 4); % 四元数矩阵：[实部, i, j, k]
    
    % 实部设为0，RGB作为虚部
    Q(:,:,1) = 0; % 实部
    Q(:,:,2) = rgb_image(:,:,1); % i虚部对应R
    Q(:,:,3) = rgb_image(:,:,2); % j虚部对应G
    Q(:,:,4) = rgb_image(:,:,3); % k虚部对应B
end

function rgb_image = quaternion_matrix_to_rgb_simple(Q)
% 简化的四元数矩阵到RGB转换
    [m, n, ~] = size(Q);
    rgb_image = zeros(m, n, 3);
    
    % 从虚部提取RGB值
    rgb_image(:,:,1) = Q(:,:,2); % R
    rgb_image(:,:,2) = Q(:,:,3); % G
    rgb_image(:,:,3) = Q(:,:,4); % B
    
    % 转换为uint8
    rgb_image = uint8(max(0, min(255, rgb_image)));
end

function Q_imag = imag_quaternion_matrix_simple(Q)
% 提取四元数矩阵的虚部
    Q_imag = Q;
    Q_imag(:,:,1) = 0; % 实部设为0
end

function real_part = real_quaternion_matrix_simple(Q)
% 提取四元数矩阵的实部
    real_part = Q(:,:,1);
end

function [M_cell, S_cell] = five_quaternion_decomposition_simple(A_cell)
% 简化的五个四元数矩阵分解
    num = length(A_cell);
    assert(num == 5, '需要5个四元数矩阵');
    
    % 简化实现：返回单位矩阵和原始矩阵
    M_cell = cell(1, 6);
    S_cell = cell(1, 5);
    
    % 创建单位矩阵
    for i = 1:6
        if i <= 5
            m = size(A_cell{i}, 1);
            M_cell{i} = create_quaternion_identity(m);
        else
            n = size(A_cell{5}, 2);
            M_cell{i} = create_quaternion_identity(n);
        end
    end
    
    % S矩阵设为原始矩阵
    for i = 1:5
        S_cell{i} = A_cell{i};
    end
end

function I = create_quaternion_identity(n)
% 创建四元数单位矩阵
    I = zeros(n, n, 4);
    for i = 1:n
        I(i,i,1) = 1; % 实部为1
        I(i,i,2:4) = 0; % 虚部为0
    end
end

function C = quaternion_matrix_multiply(A, B)
% 四元数矩阵乘法（简化实现）
    [m, n, ~] = size(A);
    [n2, p, ~] = size(B);
    assert(n == n2, '矩阵维度不匹配');
    
    C = zeros(m, p, 4);
    
    for i = 1:m
        for j = 1:p
            sum_q = zeros(1, 4);
            for k = 1:n
                a = squeeze(A(i,k,:))';
                b = squeeze(B(k,j,:))';
                % 四元数乘法
                q = [a(1)*b(1) - dot(a(2:4), b(2:4)), ...
                     a(1)*b(2:4) + b(1)*a(2:4) + cross(a(2:4), b(2:4))];
                sum_q = sum_q + q;
            end
            C(i,j,:) = sum_q;
        end
    end
end

function C = quaternion_matrix_add(A, B)
% 四元数矩阵加法
    C = A + B;
end

function C = quaternion_matrix_scale(A, scalar)
% 四元数矩阵标量乘法
    C = A * scalar;
end

function A_inv = quaternion_matrix_inverse_simple(A)
% 简化的四元数矩阵求逆（假设为对角矩阵）
    [m, n, ~] = size(A);
    assert(m == n, '矩阵必须是方阵');
    
    A_inv = zeros(m, n, 4);
    
    for i = 1:m
        for j = 1:n
            if i == j
                % 对角元素求逆
                q = squeeze(A(i,j,:))';
                norm_sq = sum(q.^2);
                if norm_sq > 1e-10
                    A_inv(i,j,:) = [q(1), -q(2), -q(3), -q(4)] / norm_sq;
                else
                    A_inv(i,j,:) = [0, 0, 0, 0];
                end
            else
                A_inv(i,j,:) = [0, 0, 0, 0];
            end
        end
    end
end