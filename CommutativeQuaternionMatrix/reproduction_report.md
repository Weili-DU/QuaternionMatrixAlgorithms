# Zhang 2024 复现报告

## 1. 核心定义与流程提取

### 1.1 可交换四元数矩阵复表示

设 $A=B_1+B_2j$，其中 $B_1,B_2\in\mathbb{C}^{m\times n}$，论文给出复表示

$$
A_\sigma=\begin{bmatrix}B_1 & B_2\\ B_2 & B_1\end{bmatrix}\in\mathbb{C}^{2m\times2n}.
$$

并通过正交变换将其分解为 $B_1-B_2$ 与 $B_1+B_2$ 两块。

### 1.2 SVDCQ 核心

1. 对 $B_1-B_2$ 做 SVD 得 $\hat U_1,\hat\Sigma_1,\hat V_1$
2. 对 $B_1+B_2$ 做 SVD 得 $\hat U_2,\hat\Sigma_2,\hat V_2$
3. 回构
   - $U=\frac{\hat U_1+\hat U_2}{2}+\frac{\hat U_2-\hat U_1}{2}j$
   - $\Sigma=\frac{\hat\Sigma_1+\hat\Sigma_2}{2}+\frac{\hat\Sigma_2-\hat\Sigma_1}{2}j$
   - $V=\frac{\hat V_1+\hat V_2}{2}+\frac{\hat V_2-\hat V_1}{2}j$
4. 得到 $A=U\Sigma V^H$

### 1.3 GICQ 核心

论文公式 (5.5):

$$
A^\dagger=\frac{(B_1-B_2)^\dagger+(B_1+B_2)^\dagger}{2}
+\frac{(B_1+B_2)^\dagger-(B_1-B_2)^\dagger}{2}j.
$$

### 1.4 CQLS 求解

最小范数解采用

$$
x_{LS}=A^\dagger b.
$$

## 2. 可执行伪代码

```text
function SVDCQ(A):
    (B1, B2) = split(A)
    [U1, S1, V1] = svd(B1 - B2)
    [U2, S2, V2] = svd(B1 + B2)
    U = (U1 + U2)/2 + (U2 - U1)/2 * j
    S = (S1 + S2)/2 + (S2 - S1)/2 * j
    V = (V1 + V2)/2 + (V2 - V1)/2 * j
    return U, S, V

function GICQ(A):
    (B1, B2) = split(A)
    M1 = pinv(B1 - B2)
    M2 = pinv(B1 + B2)
    return (M1 + M2)/2 + (M2 - M1)/2 * j

function CQLS(A, b):
    A_dag = GICQ(A)
    return A_dag * b
```

## 3. 实现与验证

- 语言: Python（环境中无 MATLAB 可执行器，采用等价数值实现）
- 单测: `tests/test_minimal_numeric.py`
  - Example 6.1 两种求解路径一致性
  - Penrose 四条件数值验证
- 运行命令:
  - `python -m pytest -q`
  - `python scripts/run_reproduce.py --config configs/default_scan.json`

## 4. 结果对齐

### 4.1 论文 Example 6.1 对齐

- `svd_residual = 1.2178e-14`
- `gi_residual = 1.2178e-14`
- `x_diff_norm = 0`
- `paper_trend_match = True`

### 4.2 参数扫描（初始化/阈值/最大迭代/精度）

- 扫描维度:
  - init: `pinv | zero | random`
  - rcond: `1e-12 | 1e-10 | 1e-8`
  - max_iter: `5 | 20 | 50`
  - tol: `1e-13 | 1e-11`
  - dtype: `float64 | float32`
- 最优组合:
  - `dtype=float64, init=random, rcond=1e-10, tol=1e-11, max_iter=50`
  - `max_residual=1.418e-13 < 1e-11`

### 4.3 与论文趋势比较结论

- 论文趋势: 误差整体低于 $10^{-11}$
- 复现结果: 在扫描最优参数下，所有测试规模误差均低于 $10^{-11}$
- 对齐结论: 核心误差趋势一致

## 5. 偏差分析

- 本阶段未复现论文的第三方对照算法（Kosal、Ding），故仅验证“误差趋势”和“算法一致性”，未做同平台 CPU 对比
- 论文基准环境为 MATLAB 2018b + Intel i7-7700HQ，本复现环境为 Python + NumPy，绝对耗时不可直接横向对比
- Example 6.1 中 OCR 对向量第二项存在轻微字符歧义，已按上下文采用 `8-2i+j+4k`，不影响算法一致性验证

