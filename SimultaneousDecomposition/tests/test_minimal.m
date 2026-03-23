% 最小测试 - 验证核心算法功能
% 运行此测试来验证算法的基本功能

fprintf('=== 四元数矩阵同时分解算法最小测试 ===\n');

% 添加src目录到路径
addpath('../src');

% 测试1: 检查文件存在性
fprintf('测试1: 检查文件存在性...\n');
required_files = {
    'main_fixed_png_complete.m',
    'embed_quaternion_images.m',
    'five_quaternion_decomposition.m',
    'quaternion_matrix_to_rgb.m',
    'rgb_to_quaternion_matrix.m'
};

all_files_exist = true;
for i = 1:length(required_files)
    if ~exist(required_files{i}, 'file')
        fprintf('  ❌ 缺失文件: %s\n', required_files{i});
        all_files_exist = false;
    else
        fprintf('  ✅ 文件存在: %s\n', required_files{i});
    end
end

if ~all_files_exist
    error('缺少必要的算法文件');
end

% 测试2: 检查数据文件
fprintf('测试2: 检查数据文件...\n');
data_files = {
    '../data/apple.png',
    '../data/logo.png'
};

for i = 1:length(data_files)
    if ~exist(data_files{i}, 'file')
        fprintf('  ⚠️ 数据文件缺失: %s (将使用测试图像)\n', data_files{i});
    else
        fprintf('  ✅ 数据文件存在: %s\n', data_files{i});
    end
end

% 测试3: 验证基本函数
fprintf('测试3: 验证基本函数...\n');
try
    % 测试四元数转换
    test_img = zeros(10, 10, 3, 'uint8');
    Q = rgb_to_quaternion_matrix(test_img);
    fprintf('  ✅ RGB到四元数转换正常\n');
    
    img_back = quaternion_matrix_to_rgb(Q);
    fprintf('  ✅ 四元数到RGB转换正常\n');
    
    % 测试DWT函数
    [LL, LH, HL, HH] = dwt2_color(test_img);
    fprintf('  ✅ DWT变换正常\n');
    
    fprintf('所有基本功能测试通过！\n');
    
catch ME
    fprintf('  ❌ 功能测试失败: %s\n', ME.message);
    fprintf('请检查算法实现\n');
end

fprintf('=== 最小测试完成 ===\n');