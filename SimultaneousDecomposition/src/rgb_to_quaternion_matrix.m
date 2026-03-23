function Q = rgb_to_quaternion_matrix(rgb_image)
% RGB_TO_QUATERNION_MATRIX 将彩色图像的RGB三个通道转换为四元数矩阵
%   输入: rgb_image - m×n×3 的彩色图像 (uint8或double类型)
%   输出: Q - m×n 的四元数矩阵，每个元素: R*i + G*j + B*k
%         实部为0，虚部i,j,k分别对应R,G,B通道

    % 检查输入
    assert(ndims(rgb_image) == 3, '输入必须是3维彩色图像');
    assert(size(rgb_image, 3) == 3, '输入必须有3个通道（RGB）');
    
    % 转换为double类型以便计算
    if isa(rgb_image, 'uint8')
        rgb_image = double(rgb_image);
    end
    
    % 归一化到[0,1]区间（如果需要）
    % rgb_image = rgb_image / 255;
    
    % 分离RGB通道
    R = rgb_image(:,:,1);
    G = rgb_image(:,:,2);
    B = rgb_image(:,:,3);
    
    % 使用Quaternion类的静态方法创建四元数矩阵
    Q = Quaternion.from_rgb_channel(R, G, B);
end