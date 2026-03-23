function [U0, U1, U2] = decompose_pair(H1, H2, r1, r2, r21, r22)
    % 输入: H1 (m×n), H2 (n×l), 秩信息 (可预先计算)
    % 输出: U0 (m×m), U1 (n×n), U2 (l×l) 满足 H1 = U0*S1*U1^{-1}, H2 = U1*S2*U2^{-1}

    % 1. 初始化
    m = size(H1, 1);
    n = size(H1, 2);
    l = size(H2, 2);
    
    % 检查输入是否为四元数矩阵
    if ~isa(H1, 'Quaternion') || ~isa(H2, 'Quaternion')
        error('输入必须是四元数矩阵');
    end
    
    % 初始化变换矩阵
    L1 = quaternion_eye(m);      % 记录对 H1 的行变换
    R1 = quaternion_eye(n);      % 记录对 H1 的列变换
    R2 = quaternion_eye(l);      % 记录对 H2 的列变换

    % 2. 将 H1 化为 S1 = [I_r1 0; 0 0] 的形式
    % 使用行/列交换和消元
    for i = 1:r1
        % 确保 H1(i,i) 非零，必要时交换行/列
        if abs(H1(i, i).a) < 1e-10 && abs(H1(i, i).b) < 1e-10 && ...
           abs(H1(i, i).c) < 1e-10 && abs(H1(i, i).d) < 1e-10
            % 寻找第 i 行非零元素
            row_found = false;
            for k = i+1:m
                if ~(abs(H1(k, i).a) < 1e-10 && abs(H1(k, i).b) < 1e-10 && ...
                     abs(H1(k, i).c) < 1e-10 && abs(H1(k, i).d) < 1e-10)
                    % 交换行
                    H1([i, k], :) = H1([k, i], :);
                    L1([i, k], :) = L1([k, i], :);
                    row_found = true;
                    break;
                end
            end
            
            if ~row_found
                % 寻找第 i 列非零元素
                for k = i+1:n
                    if ~(abs(H1(i, k).a) < 1e-10 && abs(H1(i, k).b) < 1e-10 && ...
                         abs(H1(i, k).c) < 1e-10 && abs(H1(i, k).d) < 1e-10)
                        % 交换列
                        H1(:, [i, k]) = H1(:, [k, i]);
                        R1(:, [i, k]) = R1(:, [k, i]);
                        break;
                    end
                end
            end
        end
        
        % 归一化第 i 行
        pivot = H1(i, i);
        if ~(abs(pivot.a) < 1e-10 && abs(pivot.b) < 1e-10 && ...
             abs(pivot.c) < 1e-10 && abs(pivot.d) < 1e-10)
            % 计算 pivot 的逆
            pivot_inv = Quaternion(pivot.a, -pivot.b, -pivot.c, -pivot.d) / (pivot.a^2 + pivot.b^2 + pivot.c^2 + pivot.d^2);
            
            % 左乘 pivot_inv 到第 i 行
            for j = 1:n
                H1(i, j) = pivot_inv * H1(i, j);
            end
            for j = 1:m
                L1(i, j) = pivot_inv * L1(i, j);
            end
        end
        
        % 消去第 i 列下方元素
        for j = i+1:m
            factor = H1(j, i);
            if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                 abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                % 左乘 -factor 加到第 j 行
                for k = 1:n
                    H1(j, k) = H1(j, k) - factor * H1(i, k);
                end
                for k = 1:m
                    L1(j, k) = L1(j, k) - factor * L1(i, k);
                end
            end
        end
        
        % 消去第 i 行右侧元素
        for j = i+1:n
            factor = H1(i, j);
            if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                 abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                % 右乘 -factor 加到第 j 列
                for k = 1:m
                    H1(k, j) = H1(k, j) - H1(k, i) * factor;
                end
                for k = 1:n
                    R1(k, j) = R1(k, j) - R1(k, i) * factor;
                end
            end
        end
    end
    % 此时 H1 左上角 r1×r1 为单位阵，其余为零

    % 3. 恢复左下块（当前为 R1）为单位阵
    % 构造 L2 = R1^{-1}
    L2 = quaternion_inverse(R1);
    % 左乘 L2 到 H2
    H2 = L2 * H2;

    % 4. 将右下块 H2 化为 S2 (已知结构)
    % S2 的结构: 前 r21 列为 I_{r21}，接着 r22 列为 I_{r22}，其余为零
    
    % 首先处理前 r21 列
    for j = 1:r21
        % 确保 H2(j,j) 非零
        if abs(H2(j, j).a) < 1e-10 && abs(H2(j, j).b) < 1e-10 && ...
           abs(H2(j, j).c) < 1e-10 && abs(H2(j, j).d) < 1e-10
            % 寻找第 j 列非零元素
            for k = j+1:n
                if ~(abs(H2(k, j).a) < 1e-10 && abs(H2(k, j).b) < 1e-10 && ...
                     abs(H2(k, j).c) < 1e-10 && abs(H2(k, j).d) < 1e-10)
                    % 交换行
                    H2([j, k], :) = H2([k, j], :);
                    break;
                end
            end
        end
        
        % 归一化第 j 行
        pivot = H2(j, j);
        if ~(abs(pivot.a) < 1e-10 && abs(pivot.b) < 1e-10 && ...
             abs(pivot.c) < 1e-10 && abs(pivot.d) < 1e-10)
            pivot_inv = Quaternion(pivot.a, -pivot.b, -pivot.c, -pivot.d) / (pivot.a^2 + pivot.b^2 + pivot.c^2 + pivot.d^2);
            
            for k = 1:l
                H2(j, k) = pivot_inv * H2(j, k);
            end
        end
        
        % 消去第 j 列下方元素
        for k = j+1:n
            factor = H2(k, j);
            if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                 abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                for p = 1:l
                    H2(k, p) = H2(k, p) - factor * H2(j, p);
                end
            end
        end
        
        % 消去第 j 行右侧元素
        for k = j+1:l
            factor = H2(j, k);
            if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                 abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                for p = 1:n
                    H2(p, k) = H2(p, k) - H2(p, j) * factor;
                end
                for p = 1:l
                    R2(p, k) = R2(p, k) - R2(p, j) * factor;
                end
            end
        end
    end
    
    % 处理接下来的 r22 列
    start_col = r21 + 1;
    for j = 1:r22
        col = start_col + j - 1;
        row = r21 + j;
        
        % 确保 H2(row, col) 非零
        if abs(H2(row, col).a) < 1e-10 && abs(H2(row, col).b) < 1e-10 && ...
           abs(H2(row, col).c) < 1e-10 && abs(H2(row, col).d) < 1e-10
            % 寻找合适的行交换
            for k = row+1:n
                if ~(abs(H2(k, col).a) < 1e-10 && abs(H2(k, col).b) < 1e-10 && ...
                     abs(H2(k, col).c) < 1e-10 && abs(H2(k, col).d) < 1e-10)
                    H2([row, k], :) = H2([k, row], :);
                    break;
                end
            end
        end
        
        % 归一化
        pivot = H2(row, col);
        if ~(abs(pivot.a) < 1e-10 && abs(pivot.b) < 1e-10 && ...
             abs(pivot.c) < 1e-10 && abs(pivot.d) < 1e-10)
            pivot_inv = Quaternion(pivot.a, -pivot.b, -pivot.c, -pivot.d) / (pivot.a^2 + pivot.b^2 + pivot.c^2 + pivot.d^2);
            
            for k = 1:l
                H2(row, k) = pivot_inv * H2(row, k);
            end
        end
        
        % 消去下方元素
        for k = row+1:n
            factor = H2(k, col);
            if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                 abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                for p = 1:l
                    H2(k, p) = H2(k, p) - factor * H2(row, p);
                end
            end
        end
        
        % 消去右侧元素
        for k = col+1:l
            factor = H2(row, k);
            if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                 abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                for p = 1:n
                    H2(p, k) = H2(p, k) - H2(p, col) * factor;
                end
                for p = 1:l
                    R2(p, k) = R2(p, k) - R2(p, col) * factor;
                end
            end
        end
    end

    % 5. 输出分解矩阵
    U0 = quaternion_inverse(L1);
    U1 = R1;
    U2 = R2;
end

% 辅助函数：创建四元数单位矩阵
function I = quaternion_eye(n)
    I = Quaternion.zeros(n, n);
    for i = 1:n
        I(i, i) = Quaternion(1, 0, 0, 0);
    end
end

% 辅助函数：四元数矩阵求逆
function A_inv = quaternion_inverse(A)
    [m, n] = size(A);
    if m ~= n
        error('只支持方阵求逆');
    end
    
    % 构造增广矩阵 [A | I]
    aug = [A, quaternion_eye(m)];
    
    % 高斯消元
    for i = 1:m
        % 找到主元
        [~, pivot_row] = max(abs([aug(i:m, i).a]));
        pivot_row = pivot_row + i - 1;
        
        % 交换行
        if pivot_row ~= i
            aug([i, pivot_row], :) = aug([pivot_row, i], :);
        end
        
        % 归一化主行
        pivot = aug(i, i);
        pivot_inv = Quaternion(pivot.a, -pivot.b, -pivot.c, -pivot.d) / (pivot.a^2 + pivot.b^2 + pivot.c^2 + pivot.d^2);
        
        for j = 1:2*m
            aug(i, j) = pivot_inv * aug(i, j);
        end
        
        % 消去其他行
        for j = 1:m
            if j ~= i
                factor = aug(j, i);
                for k = 1:2*m
                    aug(j, k) = aug(j, k) - factor * aug(i, k);
                end
            end
        end
    end
    
    % 提取逆矩阵
    A_inv = aug(:, m+1:2*m);
end