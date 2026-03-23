% 批量处理多张彩色图像

% 定义要处理的图像文件名列表
image_files = {'apple.png', 'balloon..png', 'cat.png', 'fox.png', 'girl.png'};

% 创建保存结果的目录
output_dir = 'DWT_results';
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

% 循环处理每张图像
for i = 1:length(image_files)
    % 读取彩色图像
    img = imread(image_files{i});  % 假设是RGB图像
    
    % 分离RGB三个通道
    R = img(:,:,1);  % 红色通道
    G = img(:,:,2);  % 绿色通道
    B = img(:,:,3);  % 蓝色通道
    
    % 对每个通道分别进行二维离散小波变换
    % 使用手动实现的Haar小波变换
    [LL_R, LH_R, HL_R, HH_R] = haar_dwt2(R);
    [LL_G, LH_G, HL_G, HH_G] = haar_dwt2(G);
    [LL_B, LH_B, HL_B, HH_B] = haar_dwt2(B);
    
    % 重构每个通道的子带（如果需要合并显示）
    LL = cat(3, LL_R, LL_G, LL_B);  % 合并三个通道的LL子带
    LH = cat(3, LH_R, LH_G, LH_B);  % 合并水平细节
    HL = cat(3, HL_R, HL_G, HL_B);  % 合并垂直细节
    HH = cat(3, HH_R, HH_G, HH_B);  % 合并对角细节（论文中用于嵌入的部分）
    
    % 保存结果
    [~, name, ~] = fileparts(image_files{i});
    save(fullfile(output_dir, [name, '_dwt_results.mat']), 'LL', 'LH', 'HL', 'HH');
    
    % 显示处理进度
    fprintf('已处理图像 %d/%d: %s\n', i, length(image_files), image_files{i});
end

fprintf('所有图像处理完成！\n');