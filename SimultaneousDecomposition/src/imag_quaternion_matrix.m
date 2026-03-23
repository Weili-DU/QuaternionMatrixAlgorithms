function Q_imag = imag_quaternion_matrix(Q)
% 提取四元数矩阵的虚部，返回实部为0、虚部与 Q 相同的四元数矩阵
    [m, n] = size(Q);
    Q_imag = quaternion.zeros(m, n);
    for i = 1:m
        for j = 1:n
            q = Q(i, j);
            [~, b, c, d] = parts(q);
            Q_imag(i, j) = quaternion(0, b, c, d);
        end
    end
end

function real_part = real_quaternion_matrix(Q)
% 提取四元数矩阵的实部，返回 m×n 实数矩阵
    [m, n] = size(Q);
    real_part = zeros(m, n);
    for i = 1:m
        for j = 1:n
            q = Q(i, j);
            [a, ~, ~, ~] = parts(q);
            real_part(i, j) = a;
        end
    end
end