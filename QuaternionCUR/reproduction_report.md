# 复现实验报告：Ling & Hu (2025) Quaternion CUR

## 1. 复现目标与范围

- 目标：跑通论文核心算法链路（DEIM/mDEIM + QCUR），并复现至少一组与论文一致的趋势性结果
- 范围：本阶段交付可执行代码、最小测试、结果图表与整合文档；不做 Git 提交

## 2. 论文核心定义与流程提取

### 2.1 核心分解

- QCUR 形式：$A \approx C U R$
- 采样：对左右子空间向量分别做 DEIM/mDEIM，得到行列索引
- 因子构造：
  - 方法 1：$U = C^\dagger A R^\dagger$
  - 方法 2（文中加速）：$U = A(s,t)^\dagger$

### 2.2 停止准则与参数

- 自适应 QB/QSVD 中误差阈值：`threshold = c * ||A||_F^2`
- 论文实验中固定参数：`b = 10`, `p = 1`
- 论文 Table 4 扫描：`c = [8e-3, 5e-3, 2e-3, 9e-4, 6e-4, 3e-4]`

### 2.3 复杂度信息

- 文中给出 mDEIM 相比 DEIM 的核心优势：避免每轮直接重算增维逆矩阵
- 文中量级：DEIM 约 $\frac{1}{2}k^4+\frac{5}{3}k^3$，mDEIM 约 $\frac{7}{3}k^3$

## 3. 可执行伪代码

```text
Input: quaternion matrix A, threshold c, rank cap max_rank
1) Estimate k by residual-energy rule under c
2) Compute row/col low-dimensional bases W, V
3) Run mDEIM(W) -> row indices s
4) Run mDEIM(V) -> col indices t
5) C = A[:, t], R = A[s, :]
6) U = C^† A R^†   or   U = A[s, t]^†
7) A_hat = C U R
8) Report relative error and PSNR
```

## 4. 模块拆分与实现

- `src/deim.py`：DEIM 与 mDEIM 索引选择
- `src/qcur.py`：秩估计、QCUR 分解主流程
- `src/quaternion_utils.py`：四元数矩阵合法性检查、复块映射、乘法、伪逆、误差与 PSNR
- `src/experiments.py`：参数扫描、对比表与图生成
- `scripts/run_reproduce.py`：一键入口

## 5. 验证结果

### 5.1 最小测试

- 测试命令：`python -m pytest -q`
- 结果：`2 passed`

### 5.2 论文趋势对齐（Table 4 风格）

- 输出文件：`outputs/tables/table4_like_comparison.csv`
- 结果结论：
  - `k_trend_match = True`（随 `c` 减小，估计秩非降）
  - `psnr_trend_match = True`（随 `c` 减小，PSNR 非降）

本次复现结果（摘录）：

| c | 复现 k | 复现 PSNR |
|---:|---:|---:|
| 8e-3 | 4 | 30.63 |
| 5e-3 | 4 | 30.63 |
| 2e-3 | 4 | 30.63 |
| 9e-4 | 5 | 35.13 |
| 6e-4 | 5 | 35.13 |
| 3e-4 | 6 | 35.90 |

### 5.3 图表

- `outputs/figures/trend_k_psnr_vs_c.png`：论文与复现的 `k/PSNR-c` 趋势对比图

## 6. 偏差分析

- 本复现完成了趋势一致性，但未做像素级同值复现
- 偏差来源：
  - 本地无论文原始图像 `yunlong`、`bridge`
  - 本地无论文官方 MATLAB 代码与同版本四元数工具链
  - 本实现采用 Python 环境下的可运行等价流程，目标是“趋势复现 + 工程闭环”

## 7. 缺失项清单（用于进一步逼近论文数值）

| 缺失项 | 用途 | 建议获取方式 |
|---|---|---|
| 原始图像 `yunlong`、`bridge` | 复现论文第 4.3 节 PSNR 绝对数值 | 从论文作者代码仓库或通讯作者补充 |
| 作者公开 MATLAB 主脚本与参数 | 对齐实现细节与默认参数 | 使用论文内给出的 GitHub 链接拉取 |
| 四元数工具箱版本信息 | 避免线代细节差异 | 复现实验环境说明或作者补充 |
| SuiteSparse 指定矩阵构造脚本 | 对齐第 4.1 节矩阵来源 | 按论文表 2 的 ID 拉取并记录预处理 |

在以上文件补齐后，可继续推进“绝对数值对齐”复现实验。
