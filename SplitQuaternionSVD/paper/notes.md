# Wang 2024 论文笔记（复现用）

## 核心对象
- split quaternion 矩阵的奇异值分解（SVDSQ）
- 基于 SVDSQ 的 MP 广义逆与最小二乘问题（SVDLS）

## 关键公式
- 实表示：式 (2.1)
- 逆映射：式 (2.4)
- SVDSQ：式 (4.8a)-(4.8d)
- 最小二乘最小范数解：$X_{LS}=A^\dagger B$

## 实验关键信息
- 论文运行环境：MATLAB R2018b（Intel i7 / 16GB）
- Example 6.1 给出显式矩阵 A, B 与奇异值数值
- Example 6.2 比较 SVDLS 与另一算法在误差/时间上的趋势
