% 复现脚本 - 四元数矩阵同时分解算法
% 运行此脚本来复现整个算法流程

fprintf('=== 四元数矩阵同时分解算法复现脚本 ===\n');

% 添加src目录到路径
addpath('../src');

% 检查依赖
fprintf('检查依赖...\n');
if ~exist('imread', 'file')
    error('需要图像处理工具箱');
end

% 运行主程序
fprintf('运行主程序...\n');
try
    % 切换到src目录
    cd('../src');
    
    % 运行完整版本
    main_fixed_png_complete;
    
    fprintf('复现完成！\n');
    fprintf('结果保存在 outputs 目录中\n');
    
catch ME
    fprintf('复现过程中出错: %s\n', ME.message);
    fprintf('尝试运行简化版本...\n');
    
    % 尝试运行其他版本
    try
        main;
    catch ME2
        fprintf('简化版本也失败: %s\n', ME2.message);
        fprintf('请检查文件完整性\n');
    end
end

% 返回脚本目录
cd('../scripts');