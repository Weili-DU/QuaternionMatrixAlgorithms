function HH_quat = process_HH_subband(HH_cell)
% PROCESS_HH_SUBBAND 处理HH子带，转换为四元数矩阵
%   输入: HH_cell - cell数组，包含5个HH子带
%         每个HH子带是 m×n×3 的彩色图像
%   输出: HH_quat - cell数组，包含5个四元数矩阵

    num_images = length(HH_cell);
    HH_quat = cell(1, num_images);
    
    for idx = 1:num_images
        HH = HH_cell{idx};
        
        % 确保输入是RGB图像
        assert(size(HH, 3) == 3, 'HH子带必须是RGB图像');
        
        % 转换为四元数矩阵
        HH_quat{idx} = rgb_to_quaternion_matrix(HH);
        
        fprintf('第%d个HH子带已转换为四元数矩阵，尺寸: %d×%d\n', ...
                idx, size(HH_quat{idx}, 1), size(HH_quat{idx}, 2));
    end
end