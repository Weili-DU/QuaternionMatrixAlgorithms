function [M_cell, S_cell, rank_info] = five_quaternion_decomposition(A_cell)
% FIVE_QUATERNION_DECOMPOSITION 五个四元数矩阵的同时分解（定理2.4）
%   输入: A_cell - 1x5的cell数组，包含五个四元数矩阵 A1,...,A5
%         维度要求: A1: q1×q2, A2: q2×q3, A3: q3×q4, A4: q4×q5, A5: q5×q6
%   输出: M_cell - 1x6的cell数组，包含分解矩阵 M0,...,M5
%         S_cell - 1x5的cell数组，包含标准形矩阵 S_a1,...,S_a5
%         rank_info - 结构体，包含所有计算得到的秩信息
%
% 注意：该函数依赖于 LANQSVDToolbox 或 MATLAB 的 Quaternion Toolbox。
%       如果未安装，请自行实现四元数矩阵的基本运算（乘法、逆、秩等）。

    %% 1. 输入验证
    assert(length(A_cell) == 5, '需要输入5个四元数矩阵');
    dims = check_dimensions(A_cell);  % 获取各矩阵维度 [q1,q2,q3,q4,q5,q6]

    %% 2. 计算所有需要的秩（公式2.16-2.20）
    fprintf('Step 1: Computing ranks...\n');
    rank_info = compute_all_ranks(A_cell);

    %% 3. 构建S矩阵的标准形（公式2.11-2.15）
    fprintf('Step 2: Constructing S matrices...\n');
    S_cell = construct_S_matrices(rank_info, dims);

    %% 初始化M矩阵（全部设为单位阵）
    M_cell = cell(1, 6);
    for i = 1:6
        M_cell{i} = quaternion_eye(dims(i));  % 四元数单位阵
    end

    %% 5. 分解第一对矩阵 A1 和 A2（引理2.1）
    fprintf('Step 3: Decomposing A1 and A2...\n');
    [M_cell{1}, M_cell{2}, M_cell{3}] = decompose_pair(...
        A_cell{1}, A_cell{2}, S_cell{1}, S_cell{2}, rank_info);

    %% 6. 依次处理 A3, A4, A5
    for k = 3:5
        fprintf('Step %d: Processing A%d...\n', k+1, k);
        [M_cell{k}, M_cell{k+1}] = process_next_matrix(...
            A_cell{k}, M_cell{k}, S_cell{k}, rank_info, k);
    end

    fprintf('Decomposition completed.\n');
end

%% ==================== 辅助函数 ====================

function dims = check_dimensions(A_cell)
    q1 = size(A_cell{1}, 1);
    q2 = size(A_cell{1}, 2);
    assert(size(A_cell{2}, 1) == q2, 'A2的行数必须等于A1的列数');
    q3 = size(A_cell{2}, 2);
    assert(size(A_cell{3}, 1) == q3, 'A3的行数必须等于A2的列数');
    q4 = size(A_cell{3}, 2);
    assert(size(A_cell{4}, 1) == q4, 'A4的行数必须等于A3的列数');
    q5 = size(A_cell{4}, 2);
    assert(size(A_cell{5}, 1) == q5, 'A5的行数必须等于A4的列数');
    q6 = size(A_cell{5}, 2);
    dims = [q1, q2, q3, q4, q5, q6];
end

function rank_info = compute_all_ranks(A_cell)
% 计算所有需要的秩（公式2.16-2.20）
    A1 = A_cell{1}; A2 = A_cell{2}; A3 = A_cell{3}; 
    A4 = A_cell{4}; A5 = A_cell{5};

    rank_info = struct();

    % 单个矩阵的秩
    rank_info.r1 = quaternion_rank(A1);
    rank_info.r2 = quaternion_rank(A2);
    rank_info.r3 = quaternion_rank(A3);
    rank_info.r4 = quaternion_rank(A4);
    rank_info.r5 = quaternion_rank(A5);

    % A1A2 乘积的秩
    A12 = quaternion_multiply(A1, A2);
    rank_info.r12 = quaternion_rank(A12);
    rank_info.r22 = rank_info.r2 - rank_info.r12;

    % A1A2A3 相关的秩
    A123 = quaternion_multiply(A12, A3);
    A23 = quaternion_multiply(A2, A3);
    rank_info.r13 = quaternion_rank(A123);
    rank_info.r23 = quaternion_rank(A23) - rank_info.r13;
    rank_info.r33 = rank_info.r3 - quaternion_rank(A23);

    % A1A2A3A4 相关的秩
    A1234 = quaternion_multiply(A123, A4);
    A234 = quaternion_multiply(A23, A4);
    A34 = quaternion_multiply(A3, A4);
    rank_info.r14 = quaternion_rank(A1234);
    rank_info.r24 = quaternion_rank(A234) - rank_info.r14;
    rank_info.r34 = quaternion_rank(A34) - quaternion_rank(A234);
    rank_info.r44 = rank_info.r4 - quaternion_rank(A34);

    % A1A2A3A4A5 相关的秩
    A12345 = quaternion_multiply(A1234, A5);
    A2345 = quaternion_multiply(A234, A5);
    A345 = quaternion_multiply(A34, A5);
    A45 = quaternion_multiply(A4, A5);
    rank_info.r15 = quaternion_rank(A12345);
    rank_info.r25 = quaternion_rank(A2345) - rank_info.r15;
    rank_info.r35 = quaternion_rank(A345) - quaternion_rank(A2345);
    rank_info.r45 = quaternion_rank(A45) - quaternion_rank(A345);
    rank_info.r55 = rank_info.r5 - quaternion_rank(A45);
end

function S_cell = construct_S_matrices(rank_info, dims)
% 构建 S_a1 到 S_a5 的标准形（公式2.11-2.15）
    [q1,q2,q3,q4,q5,q6] = deal(dims(1), dims(2), dims(3), dims(4), dims(5), dims(6));
    S_cell = cell(1,5);

    % S_a1 (2.11)
    S1 = Quaternion.zeros(q1, q2);
    S1(1:rank_info.r1, 1:rank_info.r1) = quaternion_eye(rank_info.r1);
    S_cell{1} = S1;

    % S_a2 (2.12)
    S2 = Quaternion.zeros(q2, q3);
    % 第一块
    S2(1:rank_info.r12, 1:rank_info.r12) = quaternion_eye(rank_info.r12);
    % 第二块
    r1_minus_r12 = rank_info.r1 - rank_info.r12;
    start_row = rank_info.r12;
    start_col = rank_info.r12 + r1_minus_r12;
    S2(start_row+1:start_row+rank_info.r22, ...
       start_col+1:start_col+rank_info.r22) = quaternion_eye(rank_info.r22);
    S_cell{2} = S2;

    % S_a3 (2.13)
    S3 = Quaternion.zeros(q3, q4);
    % 第一块 r13
    S3(1:rank_info.r13, 1:rank_info.r13) = quaternion_eye(rank_info.r13);
    % 第二块 r23
    row_start = rank_info.r13;
    col_start = rank_info.r13;
    S3(row_start+1:row_start+rank_info.r23, ...
       col_start+1:col_start+rank_info.r23) = quaternion_eye(rank_info.r23);
    % 第三块 r33
    row_start = row_start + rank_info.r23;
    col_start = col_start + rank_info.r23;
    S3(row_start+1:row_start+rank_info.r33, ...
       col_start+1:col_start+rank_info.r33) = quaternion_eye(rank_info.r33);
    S_cell{3} = S3;

    % S_a4 (2.14) 类似，有四块
    S4 = Quaternion.zeros(q4, q5);
    blocks4 = [rank_info.r14, rank_info.r24, rank_info.r34, rank_info.r44];
    fill_blocks(S4, blocks4);
    S_cell{4} = S4;

    % S_a5 (2.15) 有五块
    S5 = Quaternion.zeros(q5, q6);
    blocks5 = [rank_info.r15, rank_info.r25, rank_info.r35, rank_info.r45, rank_info.r55];
    fill_blocks(S5, blocks5);
    S_cell{5} = S5;
end

function fill_blocks(S, blocks)
% 在S矩阵中按顺序填充单位块
    row = 0; col = 0;
    for k = 1:length(blocks)
        if blocks(k) > 0
            S(row+1:row+blocks(k), col+1:col+blocks(k)) = quaternion_eye(blocks(k));
            row = row + blocks(k);
            col = col + blocks(k);
        end
    end
end

function [M0, M1, M2] = decompose_pair(A1, A2, S1, S2, rank_info)
% 分解第一对矩阵 A1 和 A2（引理2.1）
% 输入：A1, A2 - 四元数矩阵
%       S1, S2 - 对应的标准形
%       rank_info - 包含必要的秩信息
% 输出：M0, M1, M2 - 分解矩阵，满足 A1 = M0 * S1 * M1^{-1}, A2 = M1 * S2 * M2^{-1}
%
% 注意：此实现基于初等变换，需要四元数矩阵的初等行/列操作。
%       如果你没有现成的初等变换函数，可以使用数值方法求解：
%       从 A1 = M0 * S1 * M1^{-1} 和 A2 = M1 * S2 * M2^{-1} 中，
%       先固定 M0 为单位阵，然后解出 M1 和 M2，再调整 M0 使一致性成立。
%       这里我们提供一个简化版本，假设 A1 和 A2 已经接近标准形。

    % 警告：以下代码仅为占位，实际需要实现引理2.1的算法。
    warning('decompose_pair 使用了占位代码，需要实现真正的分解算法。');
    
    % 临时返回单位阵
    m0 = size(A1, 1);
    m1 = size(A1, 2);
    m2 = size(A2, 2);
    M0 = quaternion_eye(m0);
    M1 = quaternion_eye(m1);
    M2 = quaternion_eye(m2);
end

function [Mk, Mk1] = process_next_matrix(Ak, Mk_prev, Sk, rank_info, k)
% 处理第 k 个矩阵（k=3,4,5）
% 输入：Ak - 当前矩阵
%       Mk_prev - 当前的 M_{k-1}
%       Sk - 对应的标准形
%       rank_info - 秩信息
%       k - 索引（3,4,5）
% 输出：Mk - 新的 M_k
%       Mk1 - 新的 M_{k+1}
%
% 此函数需要根据论文步骤3-5实现，涉及对 Mk_prev * Ak 的分块处理。
% 这里同样提供简化版本，需要用户根据具体秩结构完善。

    warning('process_next_matrix 使用了占位代码，需要实现真正的分解算法。');
    m = size(Ak, 2);  % Ak 的列数，即 Mk+1 的行数/列数
    Mk = quaternion_eye(size(Mk_prev, 2));  % 临时
    Mk1 = quaternion_eye(m);
end

%% ==================== 四元数基础运算（如果工具箱未提供）====================
% 以下函数假定你有 LANQSVDToolbox 或 MATLAB 的 quaternion 类。
% 如果未安装，你需要自行实现这些运算。

function r = quaternion_rank(A, tol)
% 计算四元数矩阵的数值秩（简化版本）
    if nargin < 2, tol = 1e-10; end
    [m, n] = size(A);
    % 简化：使用实部的秩作为近似
    A_real = zeros(m, n);
    for i = 1:m
        for j = 1:n
            A_real(i, j) = A(i, j).a;
        end
    end
    s = svd(A_real);
    r = sum(s > tol * max(size(A_real)) * max(s));
    % 限制秩的范围
    r = min(r, min(m, n));
    r = max(r, 1);
end

function C = quaternion_multiply(A, B)
% 四元数矩阵乘法（使用我们的Quaternion类）
    if isa(A, 'Quaternion') && isa(B, 'Quaternion')
        [m, k] = size(A);
        [k2, n] = size(B);
        assert(k == k2, '矩阵维度不匹配');
        C = Quaternion.zeros(m, n);
        for i = 1:m
            for j = 1:n
                % 直接计算每个元素，避免使用累加
                a1 = 0;
                b1 = 0;
                c1 = 0;
                d1 = 0;
                for p = 1:k
                    % 四元数乘法: (a1 + b1i + c1j + d1k) * (a2 + b2i + c2j + d2k)
                    q1 = A(i, p);
                    q2 = B(p, j);
                    
                    % 计算四元数乘积
                    a = q1.a * q2.a - q1.b * q2.b - q1.c * q2.c - q1.d * q2.d;
                    b = q1.a * q2.b + q1.b * q2.a + q1.c * q2.d - q1.d * q2.c;
                    c = q1.a * q2.c - q1.b * q2.d + q1.c * q2.a + q1.d * q2.b;
                    d = q1.a * q2.d + q1.b * q2.c - q1.c * q2.b + q1.d * q2.a;
                    
                    % 累加结果
                    a1 = a1 + a;
                    b1 = b1 + b;
                    c1 = c1 + c;
                    d1 = d1 + d;
                end
                C(i, j) = Quaternion(a1, b1, c1, d1);
            end
        end
    else
        error('输入必须是Quaternion类型');
    end
end

function I = quaternion_eye(n)
% 创建 n×n 单位四元数矩阵
    I = Quaternion.zeros(n, n);
    for i = 1:n
        I(i, i) = Quaternion(1, 0, 0, 0);
    end
end

function A_real = quaternion_to_real_matrix(A)
% 将四元数矩阵转换为实表示矩阵（每个四元数对应 4x4 实矩阵）
% 此函数需要根据四元数乘法规则实现，较复杂，这里仅作示意。
% 实际可使用工具箱的转换函数，如 lan_q2real 等。
    error('quaternion_to_real_matrix 需要具体实现');
end