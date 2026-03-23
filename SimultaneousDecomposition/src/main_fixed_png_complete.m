% 完整的四元数图像隐写算法主程序 - 直接生成PNG格式图像
% 所有功能集成在一个文件中，不依赖外部函数

fprintf('=== 四元数图像隐写算法主程序（完整集成版） ===\n');

% 检查图像文件是否存在
image_files = {'apple.png', 'balloon..png', 'cat.png', 'fox.png', 'girl.png'};
logo_file = 'logo.png';

% 验证文件存在性
for i = 1:length(image_files)
    if ~exist(image_files{i}, 'file')
        fprintf('警告: 图像文件 %s 不存在\n', image_files{i});
    end
end

if ~exist(logo_file, 'file')
    fprintf('警告: 隐秘图像文件 %s 不存在\n', logo_file);
end

% 加载载体图像
fprintf('加载载体图像...\n');
cover = cell(1, 5);
for i = 1:5
    if exist(image_files{i}, 'file')
        cover{i} = imread(image_files{i});
        fprintf('成功加载: %s (尺寸: %dx%dx%d)\n', ...
                image_files{i}, size(cover{i}, 1), size(cover{i}, 2), size(cover{i}, 3));
    else
        % 如果文件不存在，创建测试图像
        fprintf('创建测试图像替代 %s...\n', image_files{i});
        cover{i} = create_test_image(512, 512, i);
    end
end

% 加载隐秘信息
fprintf('加载隐秘信息...\n');
secret_img = [];
if exist(logo_file, 'file')
    secret_img = imread(logo_file);
    fprintf('成功加载隐秘图像: %s (尺寸: %dx%dx%d)\n', ...
            logo_file, size(secret_img, 1), size(secret_img, 2), size(secret_img, 3));
else
    % 如果logo不存在，创建测试隐秘图像
    fprintf('创建测试隐秘图像...\n');
    secret_img = create_test_secret(256, 256);
end

% 创建5个隐秘信息副本
secret = cell(1, 5);
for i = 1:5
    secret{i} = secret_img;  % 所有载体嵌入相同隐秘信息
end

% 嵌入强度（可根据论文表4.1选择）
alpha = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2];

fprintf('嵌入强度系数: %s\n', mat2str(alpha));

% 执行嵌入
fprintf('开始执行四元数隐写嵌入...\n');
try
    % 直接在主程序中实现嵌入算法
    [embedded_images, keys] = embed_quaternion_images_internal(cover, secret, alpha);
    fprintf('嵌入成功完成！\n');
    
    % 显示结果
    fprintf('显示嵌入结果...\n');
    for i = 1:5
        figure('Position', [100, 100, 800, 400]);
        
        subplot(1,3,1);
        imshow(cover{i});
        title(sprintf('原始载体 %d', i), 'FontSize', 12);
        
        subplot(1,3,2);
        imshow(embedded_images{i});
        title(sprintf('嵌入后图像 %d', i), 'FontSize', 12);
        
        subplot(1,3,3);
        diff = double(embedded_images{i}) - double(cover{i});
        imshow(diff, []);
        title(sprintf('差异图像 %d', i), 'FontSize', 12);
        
        % 计算PSNR
        mse = mean((double(cover{i}(:)) - double(embedded_images{i}(:))).^2);
        if mse == 0
            psnr = Inf;
        else
            psnr = 20 * log10(255 / sqrt(mse));
        end
        
        fprintf('图像 %d: PSNR = %.2f dB\n', i, psnr);
    end
    
    % 保存PNG格式的结果
    fprintf('保存PNG格式结果...\n');
    if ~exist('results_png_complete', 'dir')
        mkdir('results_png_complete');
    end
    
    for i = 1:5
        % 保存原始载体图像
        imwrite(cover{i}, sprintf('results_png_complete/cover_%d.png', i));
        
        % 保存嵌入后的图像
        imwrite(embedded_images{i}, sprintf('results_png_complete/embedded_%d.png', i));
        
        % 保存隐秘信息图像
        imwrite(secret{i}, sprintf('results_png_complete/secret_%d.png', i));
        
        % 保存密钥为文本文件（可选）
        key_data = keys{i};
        save(sprintf('results_png_complete/key_%d.txt', i), 'key_data', '-ascii');
    end
    
    fprintf('所有PNG格式结果已保存到 results_png_complete 目录\n');
    fprintf('=== 程序执行完成 ===\n');
    
catch ME
    fprintf('错误: %s\n', ME.message);
    fprintf('详细错误信息:\n');
    for i = 1:length(ME.stack)
        fprintf('  文件: %s, 行: %d, 函数: %s\n', ...
                ME.stack(i).file, ME.stack(i).line, ME.stack(i).name);
    end
end

%% ==================== 四元数隐写嵌入算法（内部实现） ====================

function [embedded_images, keys] = embed_quaternion_images_internal(cover_images, secret_images, alpha)
% 四元数图像隐写嵌入算法（内部实现）
% 所有功能集成在一个函数中

    num = 5;
    assert(length(cover_images) == num && length(secret_images) == num, ...
           '必须提供5个载体图像和5个隐秘信息图像');
    assert(length(alpha) == num, 'alpha 必须为5个元素的向量');

    fprintf('开始四元数图像隐写嵌入（内部实现）...\n');
    
    %% 1. 对每个载体图像进行 DWT，保存子带
    fprintf('步骤1: 对载体图像进行DWT分解...\n');
    LL_cell = cell(1, num);
    LH_cell = cell(1, num);
    HL_cell = cell(1, num);
    HH_cell = cell(1, num);

    for i = 1:num
        [LL, LH, HL, HH] = dwt2_color_internal(cover_images{i});
        LL_cell{i} = LL;
        LH_cell{i} = LH;
        HL_cell{i} = HL;
        HH_cell{i} = HH;
    end

    %% 2. 将 HH 子带转换为四元数矩阵（实部为0）
    fprintf('步骤2: 转换HH子带到四元数矩阵...\n');
    HH_quat = cell(1, num);
    for i = 1:num
        HH_quat{i} = rgb_to_quaternion_matrix_internal(HH_cell{i});
    end

    %% 3. 五个四元数矩阵同时分解（简化实现）
    fprintf('步骤3: 四元数矩阵分解...\n');
    [M_cell, S_cell] = five_quaternion_decomposition_internal(HH_quat);

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
        W_quat{i} = rgb_to_quaternion_matrix_internal(secret);
    end

    %% 5. 嵌入隐秘信息
    fprintf('步骤5: 嵌入隐秘信息...\n');
    S_new_cell = cell(1, num);
    HH_new_quat = cell(1, num);
    keys = cell(1, num);

    for i = 1:num
        % 嵌入：S_new = S_original + alpha * W
        S_new_cell{i} = quaternion_matrix_add_internal(S_cell{i}, quaternion_matrix_scale_internal(W_quat{i}, alpha(i)));

        % 重构 HH' = M_{i-1} * S_new * M_i^{-1}
        temp = quaternion_matrix_multiply_internal(quaternion_matrix_multiply_internal(M_cell{i}, S_new_cell{i}), ...
                                         quaternion_matrix_inverse_internal(M_cell{i+1}));

        % 提取虚部作为新的 HH 子带（四元数矩阵，实部为0）
        HH_new_quat{i} = imag_quaternion_matrix_internal(temp);

        % 提取实部作为密钥
        keys{i} = real_quaternion_matrix_internal(temp);
    end

    %% 6. 将新的 HH 子带从四元数转换回 RGB 图像
    fprintf('步骤6: 转换四元数矩阵回RGB...\n');
    HH_new_rgb = cell(1, num);
    for i = 1:num
        HH_new_rgb{i} = quaternion_matrix_to_rgb_internal(HH_new_quat{i});
    end

    %% 7. 逆 DWT 得到嵌入后的载体图像
    fprintf('步骤7: 逆DWT重构图像...\n');
    embedded_images = cell(1, num);
    for i = 1:num
        img_rec = idwt2_color_internal(LL_cell{i}, LH_cell{i}, HL_cell{i}, HH_new_rgb{i});
        % 裁剪到有效范围并转换为 uint8
        img_rec = max(0, min(255, img_rec));
        embedded_images{i} = uint8(img_rec);
    end

    fprintf('四元数图像隐写嵌入完成！\n');
end

%% ==================== 内部辅助函数 ====================

function [LL, LH, HL, HH] = dwt2_color_internal(rgb)
% 彩色图像DWT变换（内部实现）
    % 转换为double类型
    if isa(rgb, 'uint8')
        rgb = double(rgb);
    end
    
    R = rgb(:,:,1);
    G = rgb(:,:,2);
    B = rgb(:,:,3);

    % 使用简化版本（不依赖小波工具箱）
    [LL_R, LH_R, HL_R, HH_R] = dwt2_simple_internal(R, 'haar');
    [LL_G, LH_G, HL_G, HH_G] = dwt2_simple_internal(G, 'haar');
    [LL_B, LH_B, HL_B, HH_B] = dwt2_simple_internal(B, 'haar');

    LL = cat(3, LL_R, LL_G, LL_B);
    LH = cat(3, LH_R, LH_G, LH_B);
    HL = cat(3, HL_R, HL_G, HL_B);
    HH = cat(3, HH_R, HH_G, HH_B);
end

function rgb = idwt2_color_internal(LL, LH, HL, HH)
% 彩色图像逆DWT变换（内部实现）
    % 使用简化版本
    R = idwt2_simple_internal(LL(:,:,1), LH(:,:,1), HL(:,:,1), HH(:,:,1), 'haar');
    G = idwt2_simple_internal(LL(:,:,2), LH(:,:,2), HL(:,:,2), HH(:,:,2), 'haar');
    B = idwt2_simple_internal(LL(:,:,3), LH(:,:,3), HL(:,:,3), HH(:,:,3), 'haar');

    % 确保尺寸一致
    target_size = [size(LL,1)*2, size(LL,2)*2];
    R = R(1:target_size(1), 1:target_size(2));
    G = G(1:target_size(1), 1:target_size(2));
    B = B(1:target_size(1), 1:target_size(2));

    rgb = cat(3, R, G, B);
end

function [LL, LH, HL, HH] = dwt2_simple_internal(img, wavelet_name)
% 简化的二维离散小波变换实现
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

function img_rec = idwt2_simple_internal(LL, LH, HL, HH, wavelet_name)
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

function Q = rgb_to_quaternion_matrix_internal(rgb_image)
% RGB到四元数矩阵转换（内部实现）
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

function rgb_image = quaternion_matrix_to_rgb_internal(Q)
% 四元数矩阵到RGB转换（内部实现）
    [m, n, ~] = size(Q);
    rgb_image = zeros(m, n, 3);
    
    % 从虚部提取RGB值
    rgb_image(:,:,1) = Q(:,:,2); % R
    rgb_image(:,:,2) = Q(:,:,3); % G
    rgb_image(:,:,3) = Q(:,:,4); % B
    
    % 转换为uint8
    rgb_image = uint8(max(0, min(255, rgb_image)));
end

function [M_cell, S_cell] = five_quaternion_decomposition_internal(A_cell)
% 简化的五个四元数矩阵分解（内部实现）
    num = length(A_cell);
    assert(num == 5, '需要5个四元数矩阵');
    
    % 简化实现：返回单位矩阵和原始矩阵
    M_cell = cell(1, 6);
    S_cell = cell(1, 5);
    
    % 创建单位矩阵
    for i = 1:6
        if i <= 5
            m = size(A_cell{i}, 1);
            M_cell{i} = create_quaternion_identity_internal(m);
        else
            n = size(A_cell{5}, 2);
            M_cell{i} = create_quaternion_identity_internal(n);
        end
    end
    
    % S矩阵设为原始矩阵
    for i = 1:5
        S_cell{i} = A_cell{i};
    end
end

function I = create_quaternion_identity_internal(n)
% 创建四元数单位矩阵（内部实现）
    I = zeros(n, n, 4);
    for i = 1:n
        I(i,i,1) = 1; % 实部为1
        I(i,i,2:4) = 0; % 虚部为0
    end
end

function C = quaternion_matrix_multiply_internal(A, B)
% 四元数矩阵乘法（内部实现）
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

function C = quaternion_matrix_add_internal(A, B)
% 四元数矩阵加法（内部实现）
    C = A + B;
end

function C = quaternion_matrix_scale_internal(A, scalar)
% 四元数矩阵标量乘法（内部实现）
    C = A * scalar;
end

function A_inv = quaternion_matrix_inverse_internal(A)
% 简化的四元数矩阵求逆（内部实现）
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

function Q_imag = imag_quaternion_matrix_internal(Q)
% 提取四元数矩阵的虚部（内部实现）
    Q_imag = Q;
    Q_imag(:,:,1) = 0; % 实部设为0
end

function real_part = real_quaternion_matrix_internal(Q)
% 提取四元数矩阵的实部（内部实现）
    real_part = Q(:,:,1);
end

%% ==================== 辅助函数 ====================

function img = create_test_image(height, width, idx)
% 创建测试图像
    img = zeros(height, width, 3, 'uint8');
    
    % 根据索引创建不同的图案
    switch idx
        case 1
            % 红色渐变
            [X, Y] = meshgrid(1:width, 1:height);
            img(:,:,1) = uint8(255 * X / width);
        case 2
            % 绿色渐变
            [X, Y] = meshgrid(1:width, 1:height);
            img(:,:,2) = uint8(255 * Y / height);
        case 3
            % 蓝色渐变
            [X, Y] = meshgrid(1:width, 1:height);
            img(:,:,3) = uint8(255 * (X + Y) / (width + height));
        case 4
            % 彩色条纹
            for i = 1:height
                img(i,:,1) = uint8(255 * mod(i, 50) / 50);
                img(i,:,2) = uint8(255 * mod(i+25, 50) / 50);
                img(i,:,3) = uint8(255 * mod(i+50, 50) / 50);
            end
        case 5
            % 随机噪声
            img = uint8(rand(height, width, 3) * 255);
    end
end

function secret = create_test_secret(height, width)
% 创建测试隐秘图像
    secret = zeros(height, width, 3, 'uint8');
    
    % 白色背景
    secret(:,:,:) = 255;
    
    % 添加文字
    if license('test', 'image_toolbox')
        % 如果有图像处理工具箱，使用insertText
        secret = insertText(secret, [width/4, height/2], 'SECRET', ...
                           'FontSize', 30, 'BoxColor', 'black', 'TextColor', 'white');
    else
        % 如果没有工具箱，创建简单图案
        center_x = width / 2;
        center_y = height / 2;
        radius = min(width, height) / 4;
        
        [X, Y] = meshgrid(1:width, 1:height);
        circle_mask = ((X - center_x).^2 + (Y - center_y).^2) <= radius^2;
        
        secret(repmat(circle_mask, [1, 1, 3])) = 0; % 黑色圆形
    end
end