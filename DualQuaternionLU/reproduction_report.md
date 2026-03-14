# reproduction_report

## 1. 论文信息

- 标题：Algebraic method for LU decomposition of dual quaternion matrix and its corresponding structure-preserving algorithm
- 来源：Numerical Algorithms (2024) 97:1367–1382
- DOI：10.1007/s11075-024-01753-8

## 2. 复现目标

- 实现双四元数矩阵 LU 分解流程
- 实现与结构保持相关的分解变体
- 在小规模与主实验规模上验证重构误差与结构相关指标

## 3. 核心代数与算法提取

### 3.1 双四元数代数

- 双四元数写作 $q=q_{st}+\epsilon q_I$
- 乘法规则：
  $$
  (p_{st}+\epsilon p_I)(q_{st}+\epsilon q_I)=p_{st}q_{st}+\epsilon(p_{st}q_I+p_Iq_{st})
  $$
- 逆元（$q_{st}$ 可逆时）：
  $$
  q^{-1}=q_{st}^{-1}-\epsilon q_{st}^{-1}q_Iq_{st}^{-1}
  $$

### 3.2 分解流程

- 将矩阵分解为 $A=A_{st}+\epsilon A_I$
- 第一步：对 $A_{st}$ 做四元数 LU（支持部分主元）
- 第二步：在已知 $A_I,L_{st},U_{st}$ 下，解
  $$
  A_I=L_{st}U_I+L_IU_{st}
  $$
- 采用逐列策略先解 $U_I$ 上三角部分，再解 $L_I$ 下三角部分

### 3.3 结构保持策略

- 标准方法：部分主元，数值更稳但会改变行结构
- 结构保持变体：禁用置换，使用极小对角微扰保障可分解
- 本仓库用“行置换比例 + 填充比”评估结构保持倾向

## 4. 实现模块映射

- 表示层：`src/dual_quaternion.py`
- 矩阵构造与运算层：`src/dq_matrix.py`
- 分解与重构层：`src/lu.py`
- 误差评估与实验编排：`scripts/run_reproduce.py`

## 5. 实验设置

- 小规模正确性：`n_small=3`
- 主实验规模：`n_main=8`
- 枢轴阈值：`pivot_tol=1e-12`
- 结构保持正则：`diagonal_shift=1e-10`
- 随机种子：`2024`

## 6. 结果

结果表见：`outputs/tables/comparison_table.md`

| method | matrix_size | relative_error | fill_ratio | permutation_change_ratio | small_scale_error |
|---|---:|---:|---:|---:|---:|
| standard_partial_pivot | 8 | 1.8950e-16 | 1.1818 | 0.7500 | 1.2050e-17 |
| structure_preserving_no_pivot | 8 | 1.0927e-10 | 1.0000 | 0.0000 | 1.2050e-17 |

图结果见：`outputs/figures/error_fill_ratio.png`

## 7. 与论文趋势对齐说明

- 论文强调：部分主元策略提升稳定性，结构保持实算法强调结构信息保留
- 本复现实验趋势一致：
  - 标准部分主元误差更低
  - 结构保持变体保持零置换，且填充比更低

## 8. 偏差与限制

- 本仓库实现的是可运行复现版，重点在核心代数流程可验证
- 论文中的“实结构保持算法”基于更完整的实表示框架；当前版本采用轻量结构保持代理指标进行对照
- 若需与论文表格逐项对齐，下一步应补全实表示映射矩阵与同尺度实验集
