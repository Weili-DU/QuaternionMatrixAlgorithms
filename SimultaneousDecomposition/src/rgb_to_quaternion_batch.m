function Q_batch = rgb_to_quaternion_batch(rgb_batch)
% RGB_TO_QUATERNION_BATCH 批量处理多个彩色图像
%   输入: rgb_batch - 5×1 cell数组，每个元素是 m×n×3 的彩色图像
%   输出: Q_batch - 5×1 cell数组，每个元素是 m×n 的四元数矩阵

    assert(length(rgb_batch) == 5, '需要5个彩色图像');
    
    Q_batch = cell(1, 5);
    parfor i = 1:5  % 如果安装了Parallel Computing Toolbox可以使用并行处理
        Q_batch{i} = rgb_to_quaternion_matrix(rgb_batch{i});
    end
end