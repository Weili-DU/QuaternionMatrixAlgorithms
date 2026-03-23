% 水印嵌入脚本 - 完成图中要求的步骤

% 步骤0: 准备隐秘信息（logo.png）
fprintf('=== 步骤0: 准备隐秘信息 ===\n');
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
fprintf('\n=== 步骤1: 执行DWT变换 ===\n');
try
    % 运行DWT.m进行DWT变换
    run('DWT.m');
    fprintf('DWT变换完成！\n');
catch ME
    fprintf('DWT变换出错: %s\n', ME.message);
    return;
end

% 步骤2: 读取DWT结果并将HH子带转换为四元数矩阵
fprintf('\n=== 步骤2: HH子带转四元数矩阵 ===\n');
try
    % 定义图像文件名列表
    image_files = {'apple.png', 'balloon..png', 'cat.png', 'fox.png', 'girl.png'};
    output_dir = 'DWT_results';
    
    % 读取所有HH子带
    num_images = length(image_files);
    HH_cell = cell(1, num_images);
    
    for i = 1:num_images
        [~, name, ~] = fileparts(image_files{i});
        mat_file = fullfile(output_dir, [name, '_dwt_results.mat']);
        
        % 加载mat文件
        load(mat_file, 'HH');
        HH_cell{i} = HH;
        
        fprintf('已加载第%d个HH子带，尺寸: %dx%dx%d\n', i, size(HH,1), size(HH,2), size(HH,3));
    end
    
    % 处理HH子带，转换为四元数矩阵
    HH_quat = process_HH_subband(HH_cell);
    fprintf('\nHH子带转四元数矩阵完成！\n');
    
catch ME
    fprintf('HH子带处理出错: %s\n', ME.message);
    return;
end

% 步骤3: 嵌入隐秘信息（logo）到四元数矩阵
fprintf('\n=== 步骤3: 嵌入隐秘信息 ===\n');
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
    
    fprintf('\n隐秘信息嵌入完成！\n');
    
catch ME
    fprintf('嵌入隐秘信息出错: %s\n', ME.message);
    return;
end

% 步骤4: 将嵌入水印后的四元数矩阵转换回RGB图像
fprintf('\n=== 步骤4: 四元数矩阵转回RGB图像 ===\n');
try
    HH_with_watermark_rgb = cell(1, num_images);
    for i = 1:num_images
        % 将四元数矩阵转换回RGB图像
        HH_with_watermark_rgb{i} = quaternion_matrix_to_rgb(HH_quat_with_watermark{i}, 'double');
        fprintf('已转换第%d个嵌入水印的HH子带\n', i);
    end
    
    fprintf('\n四元数矩阵转回RGB图像完成！\n');
    
catch ME
    fprintf('转换四元数矩阵出错: %s\n', ME.message);
    return;
end

% 步骤5: 保存结果
fprintf('\n=== 步骤5: 保存结果 ===\n');
try
    % 创建保存水印结果的目录
    watermark_dir = 'Watermark_results';
    if ~exist(watermark_dir, 'dir')
        mkdir(watermark_dir);
    end
    
    % 保存嵌入水印后的HH子带
    for i = 1:num_images
        [~, name, ~] = fileparts(image_files{i});
        save(fullfile(watermark_dir, [name, '_watermark.mat']), ...
             'HH_quat', 'HH_quat_with_watermark', 'HH_with_watermark_rgb');
        fprintf('已保存第%d个嵌入水印的结果\n', i);
    end
    
    fprintf('\n结果保存完成！\n');
    
catch ME
    fprintf('保存结果出错: %s\n', ME.message);
    return;
end

fprintf('\n=== 水印嵌入流程完成 ===\n');
fprintf('已完成图中要求的所有步骤：\n');
fprintf('1. 对载体图像进行DWT变换\n');
fprintf('2. 将HH子带转换为四元数矩阵\n');
fprintf('3. 嵌入隐秘信息（logo）到四元数矩阵\n');
fprintf('4. 将嵌入水印后的四元数矩阵转换回RGB图像\n');
fprintf('5. 保存结果\n');