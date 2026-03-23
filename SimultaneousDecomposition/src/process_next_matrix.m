function [Mk, Mk1] = process_next_matrix(Ak, Mk_prev, Sk, rank_info, k)
    % 输入: Ak (p×q), Mk_prev (p×p) 可逆, Sk (p×q) 标准形, rank_info 包含当前所需秩, k 是当前处理的矩阵索引
    % 输出: Mk (p×p) 和 Mk1 (q×q) 满足 Mk_prev * Ak = Mk * Sk * Mk1^{-1}

    % 1. 计算 T = Mk_prev * Ak
    T = Mk_prev * Ak;
    [p, q] = size(T);
    
    % 检查输入是否为四元数矩阵
    if ~isa(T, 'Quaternion') || ~isa(Sk, 'Quaternion')
        error('输入必须是四元数矩阵');
    end
    
    % 2. 初始化变换矩阵
    L = quaternion_eye(p);   % 记录对 T 的左乘行变换
    R = quaternion_eye(q);   % 记录对 T 的右乘列变换

    % 3. 根据 k 的值获取相应的秩信息
    % 提取当前矩阵的分块信息
    switch k
        case 3
            % 对于 A3，需要 r1_3, r2_3, r3_3
            block_sizes = [rank_info.r15, rank_info.r25, rank_info.r35, rank_info.r45, rank_info.r55];
        case 4
            % 对于 A4，需要 r1_4, r2_4, r3_4, r4_4
            block_sizes = [rank_info.r15, rank_info.r25, rank_info.r35, rank_info.r45, rank_info.r55];
        case 5
            % 对于 A5，需要 r1_5, r2_5, r3_5, r4_5, r5_5
            block_sizes = [rank_info.r15, rank_info.r25, rank_info.r35, rank_info.r45, rank_info.r55];
        otherwise
            error('k 值必须是 3, 4 或 5');
    end
    
    % 过滤掉大小为0的块
    block_sizes = block_sizes(block_sizes > 0);
    num_blocks = length(block_sizes);
    
    % 计算块的起始行和列
    row_start = cumsum([1, block_sizes(1:end-1)]);
    col_start = cumsum([1, block_sizes(1:end-1)]);

    % 4. 对每个块进行处理
    for idx = 1:num_blocks
        b = block_sizes(idx);
        rows = row_start(idx):row_start(idx)+b-1;
        cols = col_start(idx):col_start(idx)+b-1;
        
        % 4.1 处理当前块，将 T(rows, cols) 化为单位阵
        for i = 1:b
            current_row = rows(i);
            current_col = cols(i);
            
            % 确保 T(current_row, current_col) 非零
            if abs(T(current_row, current_col).a) < 1e-10 && abs(T(current_row, current_col).b) < 1e-10 && ...
               abs(T(current_row, current_col).c) < 1e-10 && abs(T(current_row, current_col).d) < 1e-10
                % 寻找当前块内的非零元素
                found = false;
                for k_row = rows(i):rows(end)
                    for k_col = cols(i):cols(end)
                        if ~(abs(T(k_row, k_col).a) < 1e-10 && abs(T(k_row, k_col).b) < 1e-10 && ...
                             abs(T(k_row, k_col).c) < 1e-10 && abs(T(k_row, k_col).d) < 1e-10)
                            % 交换行
                            T([current_row, k_row], :) = T([k_row, current_row], :);
                            L([current_row, k_row], :) = L([k_row, current_row], :);
                            % 交换列
                            T(:, [current_col, k_col]) = T(:, [k_col, current_col]);
                            R(:, [current_col, k_col]) = R(:, [k_col, current_col]);
                            found = true;
                            break;
                        end
                    end
                    if found
                        break;
                    end
                end
            end
            
            % 归一化当前行
            pivot = T(current_row, current_col);
            if ~(abs(pivot.a) < 1e-10 && abs(pivot.b) < 1e-10 && ...
                 abs(pivot.c) < 1e-10 && abs(pivot.d) < 1e-10)
                % 计算 pivot 的逆
                pivot_inv = Quaternion(pivot.a, -pivot.b, -pivot.c, -pivot.d) / (pivot.a^2 + pivot.b^2 + pivot.c^2 + pivot.d^2);
                
                % 左乘 pivot_inv 到当前行
                for j = 1:q
                    T(current_row, j) = pivot_inv * T(current_row, j);
                end
                for j = 1:p
                    L(current_row, j) = pivot_inv * L(current_row, j);
                end
            end
            
            % 消去当前列下方元素
            for j = rows(i+1):rows(end)
                factor = T(j, current_col);
                if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                     abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                    % 左乘 -factor 加到第 j 行
                    for k_col = 1:q
                        T(j, k_col) = T(j, k_col) - factor * T(current_row, k_col);
                    end
                    for k_col = 1:p
                        L(j, k_col) = L(j, k_col) - factor * L(current_row, k_col);
                    end
                end
            end
            
            % 消去当前行右侧元素
            for j = cols(i+1):cols(end)
                factor = T(current_row, j);
                if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                     abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                    % 右乘 -factor 加到第 j 列
                    for k_row = 1:p
                        T(k_row, j) = T(k_row, j) - T(k_row, current_col) * factor;
                    end
                    for k_row = 1:q
                        R(k_row, j) = R(k_row, j) - R(k_row, current_col) * factor;
                    end
                end
            end
        end
        
        % 4.2 消去当前块与其他块之间的元素
        % 消去当前块行与其他块列的交叉部分
        for i = rows(1):rows(end)
            for j = 1:cols(1)-1
                factor = T(i, j);
                if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                     abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                    % 右乘 -factor 加到第 j 列
                    for k = 1:p
                        T(k, j) = T(k, j) - T(k, cols(1)) * factor;
                    end
                    for k = 1:q
                        R(k, j) = R(k, j) - R(k, cols(1)) * factor;
                    end
                end
            end
            
            for j = cols(end)+1:q
                factor = T(i, j);
                if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                     abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                    % 右乘 -factor 加到第 j 列
                    for k = 1:p
                        T(k, j) = T(k, j) - T(k, cols(1)) * factor;
                    end
                    for k = 1:q
                        R(k, j) = R(k, j) - R(k, cols(1)) * factor;
                    end
                end
            end
        end
        
        % 消去其他块行与当前块列的交叉部分
        for i = 1:rows(1)-1
            for j = cols(1):cols(end)
                factor = T(i, j);
                if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                     abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                    % 左乘 -factor 加到第 i 行
                    for k = 1:q
                        T(i, k) = T(i, k) - factor * T(rows(1), k);
                    end
                    for k = 1:p
                        L(i, k) = L(i, k) - factor * L(rows(1), k);
                    end
                end
            end
        end
        
        for i = rows(end)+1:p
            for j = cols(1):cols(end)
                factor = T(i, j);
                if ~(abs(factor.a) < 1e-10 && abs(factor.b) < 1e-10 && ...
                     abs(factor.c) < 1e-10 && abs(factor.d) < 1e-10)
                    % 左乘 -factor 加到第 i 行
                    for k = 1:q
                        T(i, k) = T(i, k) - factor * T(rows(1), k);
                    end
                    for k = 1:p
                        L(i, k) = L(i, k) - factor * L(rows(1), k);
                    end
                end
            end
        end
    end

    % 5. 计算最终的变换矩阵
    Mk = quaternion_inverse(L);
    Mk1 = R;
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