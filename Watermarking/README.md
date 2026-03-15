# Watermarking

复现论文：**Wang et al., 2025, Color image watermarking scheme based on singular value decomposition of split quaternion matrices**。

本仓库实现了彩色图像水印的嵌入、提取与攻击鲁棒性评估闭环，并输出可视化图与指标表。

## 1. 目录结构

- `paper/`：论文笔记与来源信息（原论文 PDF 因版权原因未随仓库提供）
- `src/`：核心算法模块（split quaternion 映射、嵌入提取、攻击、指标）
- `scripts/`：一键运行脚本
- `configs/`：复现实验配置
- `data/host`、`data/watermark`：输入宿主图与水印图
- `tests/`：一致性测试
- `outputs/figures`：可视化输出
- `outputs/tables`：指标表输出
- `outputs/logs`：运行日志
- `reproduction_report.md`：复现实验报告

## 2. 环境准备

```bash
python -m pip install -r requirements.txt
```

## 3. 数据准备

- 默认读取：
  - `data/host/host.png`
  - `data/watermark/watermark.png`
- 若文件不存在，脚本会自动生成一组演示图像，确保可直接跑通。

## 4. 一键运行

```bash
python scripts/run_reproduce.py --config configs/default.json
```

或在 PowerShell 下：

```powershell
./scripts/run_reproduce.ps1 -Config configs/default.json
```

## 5. 输出说明

- 可视化：
  - `outputs/figures/panel_host_wm_extract.png`（原图/含水印图/提取水印）
- 指标表：
  - `outputs/tables/metrics_attack.csv`（无攻击与多种攻击下 PSNR/SSIM/NC）
  - `outputs/tables/metrics_scan.csv`（嵌入强度与 Arnold 次数小范围扫描）
- 日志：
  - `outputs/logs/run_summary.json`

## 6. 指标解释

- **PSNR**：原图与含水印图的峰值信噪比，越高越好，常见要求不低于 35 dB。
- **SSIM**：结构相似度，越接近 1 越好。
- **NC**：原始水印与提取水印的归一化相关系数，越接近 1 越好。

## 7. 测试

```bash
python -m unittest discover -s tests -p "test_*.py"
```

当前至少包含一个嵌入-提取一致性测试（无攻击场景）。

## 8. 复现实现说明

- 采用 split quaternion 的实同构矩阵表示：
  - 对纯虚四元数矩阵 `A = R*i + G*j + B*k`，构造实矩阵 `phi(A)` 做 SVD。
- 嵌入流程：
  - 分块提取每块最大奇异值构成矩阵 `C`；
  - 对水印做 Arnold 置乱后映射到 `C` 维度；
  - 通过强度系数 `rho` 将水印注入最大奇异值矩阵并重建块。
- 提取流程：
  - 从含水印图再次提取块最大奇异值；
  - 使用非盲先验信息恢复置乱水印，再逆 Arnold 得到提取结果。

## 9. 论文对齐范围

- 已对齐：split quaternion 表示、分块+最大奇异值嵌入、Arnold 置乱、无攻击与攻击评估、参数扫描与趋势比较。
- 偏差：论文使用 MATLAB 与完整 SVDSQ 推导；本仓库为 Python 可运行复现版，保持流程一致并以指标趋势对齐为目标。
