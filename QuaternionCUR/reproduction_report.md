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

