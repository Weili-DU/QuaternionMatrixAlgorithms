# Wang 2024 Dual Quaternion LU 复现

## 项目目标

- 论文：Algebraic method for LU decomposition of dual quaternion matrix and its corresponding structure-preserving algorithm
- 目标：复现双四元数矩阵 LU 分解与结构保持变体，并验证分解正确性
- 本阶段：不做 Git 提交，仅完成单仓库可运行交付

## 目录结构

- `paper/` 论文 PDF
- `src/` 核心实现（表示层、分解层、重构层、误差评估层）
- `scripts/` 一键运行脚本
- `configs/` 实验配置
- `tests/` 正确性测试
- `outputs/figures` 图结果
- `outputs/tables` 表结果
- `outputs/logs` 运行日志

## 环境依赖

- Python 3.13.12
- numpy 2.3.5
- matplotlib 3.10.8
- pypdf 6.8.0

可选安装命令：

```bash
python -m pip install numpy matplotlib pypdf
```

## 一键复现

```bash
python scripts/run_reproduce.py
```

运行后自动生成：

- `outputs/figures/error_fill_ratio.png`
- `outputs/tables/comparison_table.csv`
- `outputs/tables/comparison_table.md`
- `outputs/logs/run_summary.json`

## 测试

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## 当前实验结论摘要

- 标准部分主元 LU：重构相对误差约 `1.8950e-16`
- 结构保持变体（无置换 + 对角微扰）：重构相对误差约 `1.0927e-10`
- 结构相关指标：标准部分主元行置换比例 `0.7500`，结构保持变体为 `0.0000`

## 关键实现说明

- 双四元数按 $q=q_{st}+\epsilon q_I$ 建模，满足 $\epsilon^2=0$
- 先对标准部分做四元数 LU（支持部分主元）
- 再按
  $$
  A_I = L_{st}U_I + L_IU_{st}
  $$
  逐列求解无穷小部分
- 结构保持变体通过禁用行交换并加入极小对角正则项来避免破坏原有行结构
