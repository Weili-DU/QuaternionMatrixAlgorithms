# QuaternionCUR: Ling & Hu 2025 Quaternion CUR 复现

本仓库复现论文 **Efficient quaternion CUR decomposition based on discrete empirical interpolation method** 的核心流程：  
- mDEIM 采样  
- QCUR 主流程  
- 阈值参数扫描  
- 趋势对齐验证（与论文 Table 4 的趋势对齐）

## 目录结构

- `paper/`：论文笔记与来源信息（原论文 PDF 因版权原因未随仓库提供）
- `src/`：算法实现（DEIM、QCUR、实验）
- `scripts/`：一键运行脚本
- `configs/`：实验参数
- `tests/`：最小数值测试
- `outputs/figures`：结果图
- `outputs/tables`：结果表
- `outputs/logs`：日志与摘要
- `reproduction_report.md`：复现结论与偏差分析
- `integration_manifest.md`：总仓库整合清单

## 环境

- Python 3.10+
- 依赖：`numpy`, `pandas`, `matplotlib`, `pyyaml`, `pytest`

安装依赖：

```bash
pip install -r requirements.txt
```

## 一键复现

```bash
python scripts/run_reproduce.py
```

运行后将生成：
- `outputs/tables/table4_like_comparison.csv`
- `outputs/figures/trend_k_psnr_vs_c.png`
- `outputs/logs/run_summary.txt`
- `outputs/logs/summary.json`

## 运行测试

```bash
python -m pytest -q
```

## 结果说明

- 复现使用论文相同的 `c` 扫描点：`[8e-3, 5e-3, 2e-3, 9e-4, 6e-4, 3e-4]`
- 观察目标：`c` 下降时，估计秩 `k` 与 PSNR 整体上升
- 本仓库输出表已包含趋势布尔列：`k_trend_match`, `psnr_trend_match`

## 语言说明

论文代码环境为 MATLAB。本仓库使用Python作为复现语言
