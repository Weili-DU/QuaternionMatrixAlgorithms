# Reproduction12: Yang et al. 2025 稀疏优化彩色图像恢复复现

## 1. 项目说明

本仓库复现论文 **Quaternion optimized model with sparseness for color image recovery** 的核心流程，完成了：

- 图像退化（随机采样缺失）与恢复主流程
- 低秩约束 + 稀疏正则的迭代求解
- 最小数值单测
- 参数扫描、结果图和对比表导出

实现语言选择为 **Python**（论文原实验为 MATLAB，本文用 Python 实现同类流程以便集成）。

## 2. 目录结构

- `paper/`：论文 PDF 与笔记
- `src/`：算法实现
- `scripts/`：一键运行脚本
- `configs/`：参数配置
- `tests/`：最小数值测试
- `outputs/figures`：结果图
- `outputs/tables`：参数扫描与论文趋势对比表
- `outputs/logs`：单次运行日志
- `reproduction_report.md`：复现报告
- `integration_manifest.md`：总仓库整合清单

## 3. 环境与安装

建议 Python 3.10+。

依赖：

- numpy
- scipy
- matplotlib
- pandas
- scikit-image
- pypdf

安装示例：

```bash
pip install numpy scipy matplotlib pandas scikit-image pypdf
```

## 4. 一键复现

```bash
python scripts/run_reproduce.py --config configs/default.json
```

运行完成后将生成：

- `outputs/figures/recovery_triplet.png`
- `outputs/figures/residual_curve.png`
- `outputs/figures/parameter_trends.png`
- `outputs/tables/parameter_scan.csv`
- `outputs/tables/best_params_by_sweep.csv`
- `outputs/tables/paper_trend_comparison.csv`
- `outputs/logs/single_run_metrics.json`

## 5. 最小测试

```bash
python -m unittest discover -s tests -v
```

当前包含：

- `tests/test_minimal_numeric.py`：验证恢复后 PSNR 相对观测图提升

## 6. 结果说明（当前实现）

- 单次恢复日志显示：在 `SR=0.2` 下，PSNR/SSIM 相对观测图显著提升
- 参数扫描显示：`lambda` 存在中间区间优于两端的趋势，与论文“过大或过小都不好”的结论一致
- `beta1` 和 `rank` 的最优点与论文数值不完全一致，详见 `reproduction_report.md`

## 7. 缺失项与补充建议

若要更严格对齐论文表格（尤其是 Table 2、50 图像统计）仍缺以下资源：

- SIPI / McMaster / BSD 论文同源图像子集及预处理细节
- 论文中各对比基线（TNNR、TNN-SR、LRQA、QTNN 等）官方实现与固定参数
- 论文中完整 Quaternion-QDCT/QSVD 细节实现（MATLAB 版本）

建议先补齐上述文件后，再执行同参数同数据对齐实验。

