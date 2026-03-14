# Reproduction Report: Wang et al. (2024) Split Quaternion SVD

## 1. 核心定义与算法提取

### 1.1 split quaternion 实表示（论文式 (2.1), (2.4)）
设 $A=A_1+A_2 i+A_3 j+A_4 k \in \mathbb{H}_s^{m\times n}$，其实表示为
$$
A^\sigma=
\begin{bmatrix}
A_1+A_3 & -A_2+A_4 \\
A_2+A_4 & A_1-A_3
\end{bmatrix}\in\mathbb{R}^{2m\times 2n}.
$$
逆映射（由分块实矩阵恢复 split quaternion 矩阵）按论文式 (2.4) 实现。

### 1.2 SVDSQ 主流程（论文第 4 节）
1. 计算 $A^\sigma$  
2. 对 $A^\sigma$ 做实矩阵 SVD：$A^\sigma=\hat U\hat\Sigma\hat V^H$  
3. 由奇异值对 $(\tau_t,\tau_{r+t})$ 构造 split quaternion 奇异值
$$
\sigma_t=\frac{\tau_t+\tau_{r+t}}{2}+\frac{\tau_t-\tau_{r+t}}{2}j.
$$
4. 由论文式 (2.4) 将 $\hat U,\hat V$ 映射回 split quaternion 单位矩阵 $U,V$，得到
$$
A=U\Sigma V^H.
$$

### 1.3 SVDLS 与广义逆（论文第 5 节）
- 通过 $(A^\sigma)^\dagger$ 计算 $A^\dagger$
- 最小范数解：$X_{LS}=A^\dagger B$

## 2. 伪代码与模块分解

### 2.1 可执行伪代码
```text
Input: A, B, config
1) As = to_sigma(A)
2) [Uhat, s, Vhat] = svd(As)
3) build sigma_t from (s_t, s_{r+t})
4) U = from_sigma(Uhat), V = from_sigma(Vhat), Sigma = diag(sigma_t)
5) A_pinv = from_sigma(pinv(As, rcond))
6) X_ls = A_pinv * B
7) compute metrics and export tables/figure/log
Output: U, Sigma, V, X_ls, reports
```

### 2.2 代码模块
- `src/split_quaternion.py`：实表示双向映射、i-共轭转置、乘法、范数
- `src/svdsq.py`：SVDSQ、重构、伪逆、最小二乘
- `src/experiments.py`：Example 6.1 + 参数扫描 + 图表/表格导出
- `scripts/run_reproduce.py`：一键入口

## 3. 停止条件与复杂度

### 3.1 停止条件
- 论文算法主体是代数直达法（核心由一次实矩阵 SVD 完成），无显式外层迭代终止式  
- 本复现实验中，参数扫描的 baseline 求解加入迭代修正，终止条件为
  $$
  \frac{\|\Delta X\|_F}{\|X\|_F+10^{-15}} < \text{refinement\_tol}
  $$
  或达到 `max_iter`

### 3.2 复杂度（主导项）
- 构造 $A^\sigma$：$O(mn)$
- 对 $A^\sigma\in\mathbb{R}^{2m\times 2n}$ 做 SVD：主导复杂度约 $O(\min(m,n)\,mn)$ 量级（常数按 2 倍维度放大）
- 其余映射、重构与表格导出均低于 SVD 主项

## 4. 结果对齐

### 4.1 Example 6.1 奇异值对齐
- 复现文件：`outputs/tables/example61_sigma_compare.md`
- 结果：3 个奇异值与论文数值高度一致，整体相对偏差：
  - `example61_sigma_rel_gap = 3.0497726643552333e-06`

### 4.2 趋势复现（小范围扫描）
- 扫描配置：`configs/reproduce_config.json`
- 输出：
  - `outputs/tables/parameter_scan.csv`
  - `outputs/tables/trend_table.md`
  - `outputs/figures/error_trend.png`
- 观察到在当前对比设置下，SVDLS 的误差与时间趋势优于 normal-equation 基线（与论文“该类对比中 SVDLS 更优”的方向一致）

### 4.3 最优参数组合（当前扫描）
- `seed=2024`
- `rcond=1e-10`
- `rank_tol=1e-10`
- `epsilon_clip=1e-14`
- `max_iter=15`
- `refinement_tol=1e-10`
- `normal_eq_ridge=1e-12`

## 5. 偏差分析

- 论文对比对象是文献 [34] 的结构保持 LDU 算法；本仓库当前基线为 normal-equation 代理实现，不是原文 [34] 逐行重写
- 论文硬件、MATLAB 版本与本地 Python/BLAS 栈不同，绝对 CPU 时间不可直接数值对齐
- 论文图 1 原始点数据未公开，当前图为按论文规模规则重采样生成

## 6. 缺失项清单（对“完全同条件复现”有影响）

1. 文献 [34] 的可运行源代码或精确实现细节  
   - 用途：构造与论文完全一致的基线比较  
   - 建议获取：作者主页/补充材料/邮件索取

2. 论文图 1 的原始实验记录（逐 h 的时间与误差原始值）  
   - 用途：像素级重建论文图曲线  
   - 建议获取：补充材料或联系作者提供

3. 论文中随机实验的精确随机种子与线性代数后端设置  
   - 用途：消除运行间微差  
   - 建议获取：作者实验脚本或补充说明

当前状态下，核心算法已完整跑通并给出与论文趋势一致的至少一组结果。
