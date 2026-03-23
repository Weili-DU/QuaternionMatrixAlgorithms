% 水印嵌入脚本（PNG输出版）- 直接生成PNG格式图像

fprintf('=== 水印嵌入脚本（PNG输出版） ===\n');

% 步骤0: 准备隐秘信息（logo.png）
fprintf('步骤0: 准备隐秘信息...\n');
try
    % 读取logo
    logo = imread('logo.png');
    fprintf('原始logo尺寸: %dx%dx%d\n', size(logo,1), size(logo,2), size(logo,3));
    
    % 调整logo尺寸以适应HH子带（256x256）
    logo_resized = imresize(logo, [256, 256]);
    fprintf('调整后logo尺寸: %dx%dx%d\n', size(logo_resized,1), size(logo_resized,2), size(logo_resized,3));
    
    % 转换为double类型
    logo_double = double(logo_resized);
    
catch ME
    fprintf('准备隐秘信息出错: %s\n', ME.message);
    return;
end

% 步骤1: 对载体图像进行DWT变换
fprintf('\n步骤1: 执行DWT变换...\n');
try
    % 定义图像文件名列表
    image_files = {'apple.png', 'balloon..png', 'cat.png', 'fox.png', 'girl.png'};
    
    % 创建DWT结果目录
    dwt_dir = 'DWT_results_png';
    if ~exist(dwt_dir, 'dir')
        mkdir(dwt_dir);
    end
    
    % 对每个图像进行DWT变换
    num_images = length(image_files);
    LL_cell = cell(1, num_images);
    LH_cell = cell(1, num_images);
    HL_cell = cell(1, num_images);
    HH_cell = cell(1, num_images);
    
    for i = 1:num_images
        fprintf('处理第%d个图像: %s\n', i, image_files{i});
        
        % 读取图像
        img = imread(image_files{i});
        
        % 对每个通道进行DWT（使用简化版本）
        R = double(img(:,:,1));
        G = double(img(:,:,2));
        B = double(img(:,:,3));
        
        % 检查是否有小波工具箱
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
        
        % 组合各子带
        LL_cell{i} = cat(3, LL_R, LL_G, LL_B);
        LH_cell{i} = cat(3, LH_R, LH_G, LH_B);
        HL_cell{i} = cat(3, HL_R, HL_G, HL_B);
        HH_cell{i} = cat(3, HH_R, HH_G, HH_B);
        
        fprintf('  第%d个图像DWT完成，HH子带尺寸: %dx%dx%d\n', i, size(HH_cell{i},1), size(HH_cell{i},2), size(HH_cell{i},3));
    end
    
    fprintf('DWT变换完成！\n');
    
catch ME
    fprintf('DWT变换出错: %s\n', ME.message);
    return;
end

% 步骤2: 将HH子带转换为四元数矩阵
fprintf('\n步骤2: HH子带转四元数矩阵...\n');
try
    % 处理HH子带，转换为四元数矩阵
    HH_quat = cell(1, num_images);
    for i = 1:num_images
        HH_quat{i} = rgb_to_quaternion_matrix(HH_cell{i});
        fprintf('已转换第%d个HH子带\n', i);
    end
    
    fprintf('HH子带转四元数矩阵完成！\n');
    
catch ME
    fprintf('HH子带处理出错: %s\n', ME.message);
    return;
end

% 步骤3: 嵌入隐秘信息（logo）到四元数矩阵
fprintf('\n步骤3: 嵌入隐秘信息...\n');
try
    % 定义嵌入强度
    alpha = 0.1;  % 嵌入强度因子
    
    % 将logo转换为四元数矩阵
    logo_quat = rgb_to_quaternion_matrix(logo_double);
    fprintf('Logo已转换为四元数矩阵，尺寸: %dx%d\n', size(logo_quat,1), size(logo_quat,2));
    
    % 嵌入隐秘信息到每个HH四元数矩阵
    HH_quat_with_watermark = cell(1, num_images);
    for i = 1:num_images
        fprintf('正在嵌入第%d个HH子带...\n', i);
        [m, n] = size(HH_quat{i});
        HH_quat_with_watermark{i} = Quaternion.zeros(m, n);
        
        % 逐元素嵌入
        for row = 1:m
            for col = 1:n
                % 嵌入公式: HH_with_watermark = HH_original + alpha * logo
                HH_quat_with_watermark{i}(row, col) = HH_quat{i}(row, col) + alpha * logo_quat(row, col);
            end
        end
        fprintf('已嵌入第%d个HH子带\n', i);
    end
    
    fprintf('隐秘信息嵌入完成！\n');
    
catch ME
    fprintf('嵌入隐秘信息出错: %s\n', ME.message);
    return;
end

% 步骤4: 将嵌入水印后的四元数矩阵转换回RGB图像
fprintf('\n步骤4: 四元数矩阵转回RGB图像...\n');
try
    HH_with_watermark_rgb = cell(1, num_images);
    for i = 1:num_images
        % 将四元数矩阵转换回RGB图像
        HH_with_watermark_rgb{i} = quaternion_matrix_to_rgb(HH_quat_with_watermark{i}, 'double');
        fprintf('已转换第%d个嵌入水印的HH子带\n', i);
    end
    
    fprintf('四元数矩阵转回RGB图像完成！\n');
    
catch ME
    fprintf('转换四元数矩阵出错: %s\n', ME.message);
    return;
end

% 步骤5: 使用逆滤波合成完整图像并保存为PNG
fprintf('\n步骤5: 合成完整图像并保存为PNG...\n');
try
    % 创建保存PNG结果的目录
    png_dir = 'Watermark_results_png';
    if ~exist(png_dir, 'dir')
        mkdir(png_dir);
    end
    
    % 使用逆滤波合成完整图像
    embedded_images = inverse_filter_synthesis(HH_with_watermark_rgb, LL_cell, LH_cell, HL_cell, 'haar');
    
    % 保存PNG格式的图像
    for i = 1:num_images
        [~, name, ~] = fileparts(image_files{i});
        
        % 保存原始载体图像
        original_img = imread(image_files{i});
        imwrite(original_img, fullfile(png_dir, [name, '_original.png']));
        
        % 保存嵌入水印后的图像
        embedded_img = uint8(embedded_images{i});
        imwrite(embedded_img, fullfile(png_dir, [name, '_embedded.png']));
        
        % 保存差异图像
        diff_img = double(embedded_img) - double(original_img);
        diff_img = uint8(max(0, min(255, diff_img + 128))); % 调整对比度
        imwrite(diff_img, fullfile(png_dir, [name, '_difference.png']));
        
        % 保存隐秘信息图像
        imwrite(uint8(logo_resized), fullfile(png_dir, [name, '_watermark.png']));
        
        fprintf('已保存第%d个图像的PNG结果\n', i);
    end
    
    fprintf('PNG格式结果保存完成！\n');
    
catch ME
    fprintf('保存PNG结果出错: %s\n', ME.message);
    return;
end

fprintf('\n=== 水印嵌入流程完成（PNG输出版） ===\n');
fprintf('已生成PNG格式的图像文件，保存在 Watermark_results_png 目录中:\n');
fprintf('• *_original.png - 原始载体图像\n');
fprintf('• *_embedded.png - 嵌入水印后的图像\n');
fprintf('• *_difference.png - 差异图像\n');
fprintf('• *_watermark.png - 隐秘信息图像\n');