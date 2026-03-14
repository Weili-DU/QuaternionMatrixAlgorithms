# Zhang2024 速记

- 复表示: $A=B_1+B_2j \Rightarrow A_\sigma=\begin{bmatrix}B_1&B_2\\B_2&B_1\end{bmatrix}$
- SVDCQ: 分别对 $B_1-B_2$ 和 $B_1+B_2$ 做 SVD 后回构 $U,\Sigma,V$
- GICQ: $A^\dagger$ 由 $(B_1-B_2)^\dagger$ 与 $(B_1+B_2)^\dagger$ 线性组合得到
- CQLS: 最小范数解 $x_{LS}=A^\dagger b$
- 论文趋势: CQLS 误差整体小于 $10^{-11}$
