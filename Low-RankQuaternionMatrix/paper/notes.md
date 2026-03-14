# 低秩四元数矩阵分解论文要点笔记

## 核心模型

目标模型：
$$
\min_{A,H,W}\ \frac{1}{2}\|HW-A\|_F^2,\ \text{s.t.}\ A_{\Omega}=D_{\Omega}
$$

- $A\in \mathbb{Q}^{m\times n}$，$H\in \mathbb{Q}^{m\times r}$，$W\in \mathbb{Q}^{r\times n}$，$r<\min(m,n)$
- $\Omega$ 是观测索引集，$\Omega^c$ 为其补集

## 梯度与最优性

目标函数：
$$
f(X)=\frac{1}{2}\|HW-A\|_F^2,\ X=(A,H,W)
$$

偏导：
$$
\nabla_A f = A-HW,\quad
\nabla_H f = (HW-A)W^*,\quad
\nabla_W f = H^*(HW-A)
$$

论文给出一阶最优性与稳定点条件，并证明偏导满足 Lipschitz 连续性。

## 算法1：四元数梯度下降法

迭代步骤：
1. $H_{k+1}=H_k-\alpha(H_kW_k-A_k)W_k^*$
2. $W_{k+1}=W_k-\alpha H_{k+1}^*(H_{k+1}W_k-A_k)$
3. $A_{k+1,\Omega}=D_\Omega$
4. $A_{k+1,\Omega^c}=(A_k-\alpha(A_k-H_{k+1}W_{k+1}))_{\Omega^c}$
5. 若 $\|X_{k+1}-X_k\|_F<\epsilon$ 停止

## 算法2：改进四元数梯度下降法

与算法1前两步相同，差异在 $A$ 更新：
$$
A_{k+1,\Omega}=D_\Omega,\quad
A_{k+1,\Omega^c}=(H_{k+1}W_{k+1})_{\Omega^c}
$$

## 收敛结论

- 论文给出：当 $\alpha\in(0,2/\eta)$ 时，算法1与算法2均满足下降型不等式并收敛
- 迭代差分趋于 0：$\|A_{k+1}-A_k\|_F,\|H_{k+1}-H_k\|_F,\|W_{k+1}-W_k\|_F\to 0$

## 实验设置（论文）

- 语言/环境：MATLAB R2022a
- 采样率：$\rho=0.7$
- 步长：$\alpha=0.0025$
- 停止阈值：$\epsilon=10^{-4}$
- 图像尺度：$256\times256\times3$ 或 $135\times198\times3$
- 指标：RPSN（文中写法）与 MSSI（结构相似）

## 论文趋势结论

- 算法2整体优于算法1（RPSN 与 MSSI 更高）
- 过大步长会破坏颜色结构，影响恢复质量

## 复杂度实现说明

论文未给出统一显式复杂度公式；按实现可估计单次迭代主耗时来自四元数矩阵乘，量级约为 $O(mnr)$（常数由四元数分量运算放大）。

