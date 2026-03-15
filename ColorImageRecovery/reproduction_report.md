# Yang 2025 复现报告

## 1. 论文核心信息提取

论文：**Quaternion optimized model with sparseness for color image recovery**  
任务：彩色图像缺失像素恢复（image completion）

核心模型（论文思路）：

- 低秩项：Quaternion Truncated Nuclear Norm（QTNN）
- 稀疏项：在 QDCT 域施加 $l_1$ 正则
- 约束：观测位置保持不变，变换域辅助变量约束
- 优化：两阶段流程  
  1) 由当前解的 QSVD 构造截断项  
  2) 用 ADMM 求解含稀疏项的子问题

停止条件（论文）：

- 外层：$\|X^{k+1}-X^k\|_F \le \epsilon_0$
- 内层 ADMM：$\|X^{p+1}-X^p\|_F \le \epsilon$ 或达到最大迭代

复杂度（论文给出量级）：

- 核心代价与 SVD/矩阵运算相关，主项在 $\mathcal{O}(MN\min(M,N))$ 量级

实验设置（论文）：

- MATLAB R2019a
- 图像规模常用 $256\times256\times3$
- 关键参数扫描：$\beta_1,\lambda,r$
- 采样率：`SR={0.5,0.3,0.1}` 等

## 2. 可执行伪代码与模块化映射

伪代码：

```text
输入: 观测图 O, 掩码 Ω, 参数 (λ, r, β1, ρ, βmax, tol, max_iter)
X ← O
β ← β1
for t = 1..max_iter:
    X_lr ← 截断低秩更新(X, r)
    D ← QDCT(X_lr)
    D ← soft_threshold(D, λ)
    X_sp ← IQDCT(D)
    X_new ← 0.5*(X_lr + X_sp)
    X_new[Ω] ← O[Ω]
    X_new ← 轻度SVT稳定化(X_new, β)
    若 ||X_new - X|| / ||X|| < tol: break
    X ← X_new
    β ← min(ρβ, βmax)
输出: clip(X)
```

代码映射：

- 退化：`src/degradation.py`
- QDCT/逆变换：`src/qdct.py`
- 主求解器：`src/lrqr_sr.py`
- 指标与校验：`src/utils.py`
- 实验与扫描：`src/experiments.py`
- 一键入口：`scripts/run_reproduce.py`

## 3. 复现执行与产物

已执行：

```bash
python scripts/run_reproduce.py --config configs/default.json
python -m unittest discover -s tests -v
```

主要产物：

- 图像结果：`outputs/figures/recovery_triplet.png`
- 残差曲线：`outputs/figures/residual_curve.png`
- 参数趋势图：`outputs/figures/parameter_trends.png`
- 扫描总表：`outputs/tables/parameter_scan.csv`
- 最优参数汇总：`outputs/tables/best_params_by_sweep.csv`
- 论文趋势对比：`outputs/tables/paper_trend_comparison.csv`

## 4. 对齐结论（与论文趋势）

已对齐的一组核心趋势：

- **$\lambda$ 存在中间最优区间**，过大或过小时效果下降（与论文趋势一致）

未完全对齐趋势：

- 论文报告 `beta1=1e-4` 更优；当前实现在代理数据上更偏向较大 `beta1`
- 论文对 `rank` 的推荐（高 SR 取更高 r）与当前实现最优点存在偏差

单次恢复示例（`SR=0.2`）：

- 观测图：PSNR 6.22 / SSIM 0.148
- 恢复图：PSNR 20.56 / SSIM 0.558
- 提升：PSNR +14.34 / SSIM +0.409

## 5. 偏差分析

主要偏差来源：

- 使用 Python 近似实现，不是论文 MATLAB 原版 Quaternion 算子链
- QDCT/QSVD 采用可运行近似路径，未完全复刻论文中所有四元数细节
- 数据集不是论文同源图像子集和同一预处理流程
- 未引入论文所有对比基线的官方代码与固定参数
