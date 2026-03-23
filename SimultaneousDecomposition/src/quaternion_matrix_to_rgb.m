function rgb_image = quaternion_matrix_to_rgb(Q, original_type)
% QUATERNION_MATRIX_TO_RGB 将四元数矩阵转回RGB图像
%   输入: Q - m×n的四元数矩阵，每个元素包含R,G,B信息在虚部
%         original_type - 原始图像类型（可选，'uint8'或'double'）
%   输出: rgb_image - m×n×3的彩色图像

    [m, n] = size(Q);
    
    % 初始化RGB三个通道
    R = zeros(m, n);
    G = zeros(m, n);
    B = zeros(m, n);
    
    % 从四元数的虚部提取RGB值
    for i = 1:m
        for j = 1:n
            q = Q(i, j);
            R(i, j) = q.b;  % i虚部对应R
            G(i, j) = q.c;  % j虚部对应G
            B(i, j) = q.d;  % k虚部对应B
        end
    end
    
    % 组合RGB通道
    rgb_image = cat(3, R, G, B);
    
    % 转换回原始类型
    if nargin > 1 && strcmp(original_type, 'uint8')
        rgb_image = uint8(round(rgb_image));
    elseif nargin > 1 && strcmp(original_type, 'double')
        % 保持double类型
    else
        % 默认转换为uint8
        rgb_image = uint8(round(rgb_image));
    end
end