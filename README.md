# QuaternionMatrixAlgorithms

四元数矩阵相关算法复现与实验仓库，包含多个子课题的独立实现、实验脚本、测试与结果输出。

## 仓库结构

- `ColorImageRecovery/`：彩色图像恢复（低秩四元数表示）
- `CommutativeQuaternionMatrix/`：交换四元数矩阵相关分解与广义逆实验
- `DualQuaternionLU/`：双四元数矩阵 LU 分解复现
- `Low-RankQuaternionMatrix/`：低秩四元数矩阵分解模型复现
- `QuaternionCUR/`：四元数 CUR 分解复现
- `SplitQuaternionSVD/`：分裂四元数矩阵 SVD 复现
- `Watermarking/`：基于四元数分解的彩色图像水印实验

各子目录通常包含如下结构：

- `paper/`：论文与笔记
- `src/`：核心算法实现
- `scripts/`：复现实验入口
- `configs/`：参数配置
- `tests/`：最小可运行测试
- `outputs/`：图表、表格与日志输出

## 版权与论文说明

本仓库不提供原论文 PDF 文件。各子项目涉及的论文题目与来源信息，已在对应子文件夹的 `README.md` 中标明。

## 使用方式

进入任一子项目后，优先阅读该子项目下的 `README.md`，再按其说明安装依赖并运行复现脚本。
