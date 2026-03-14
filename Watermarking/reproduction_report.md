# Wang2025 split quaternion SVD 彩色水印复现报告

## 1. 复现实验目标

- 复现论文的彩色图像水印嵌入/提取主流程。
- 在无攻击与攻击场景输出可视化与指标（PSNR、SSIM、NC）。
- 对嵌入强度与 Arnold 参数做小范围扫描，寻找更接近论文趋势的配置。

## 2. 论文关键信息提取

### 2.1 表示与流程

- 彩色宿主图构造为纯虚 split quaternion 矩阵：`A = R*i + G*j + B*k`。
- 分块后提取每块最大奇异值，形成矩阵 `C`。
- 水印经 Arnold 置乱后参与奇异值域嵌入，嵌入强度参数为 `rho`。
- 提取时依赖先验信息，属于非盲提取路线。

### 2.2 实验设置参考

- 论文主实验无攻击下给出高保真结果（PSNR 明显高于 35，SSIM/NC 接近 1）。
- 攻击类型覆盖噪声、滤波、几何变换、压缩与组合攻击。

## 3. 本仓库实现说明

### 3.1 已实现模块

- 图像预处理与 split quaternion 实同构映射。
- 分块奇异值嵌入与提取。
- Arnold 置乱与逆置乱。
- 攻击仿真（A0-A11）。
- 指标计算（PSNR/SSIM/NC）与参数扫描。

### 3.2 与论文的偏差

- 论文实现平台为 MATLAB 2023b，本文复现实现为 Python。
- 论文为完整双层 SVDSQ 推导；本复现保留核心结构并采用可运行近似重建策略，目标是趋势对齐与工程闭环复现。

## 4. 实验结果

## 4.1 无攻击场景（A0）

- PSNR：`52.2862`
- SSIM：`0.999961`
- NC：`0.994503`

结论：无攻击下满足论文趋势（高 PSNR、SSIM/NC 接近 1）。

## 4.2 攻击场景概览（A1-A11）

- 对均值滤波（A8）与轻度几何旋转（A10）保留较好的提取相关性。
- 对强噪声、亮度重映射与强压缩攻击，NC 明显下降。
- 指标完整记录在 `outputs/tables/metrics_attack.csv`。

## 4.3 参数扫描结果

扫描维度：
- `rho ∈ {0.1, 0.2, 0.3, 0.4}`
- `arnold_iters ∈ {1, 3, 5, 8}`

最佳配置（按 NC→SSIM→PSNR 排序）：
- `rho = 0.4`
- `arnold_iters = 3`
- `PSNR = 49.0060`
- `SSIM = 0.999918`
- `NC = 0.997648`

## 5. 产物清单

- 可视化：`outputs/figures/panel_host_wm_extract.png`
- 指标表：`outputs/tables/metrics_attack.csv`、`outputs/tables/metrics_scan.csv`
- 日志：`outputs/logs/run_summary.json`
- 一键脚本：`scripts/run_reproduce.py`、`scripts/run_reproduce.ps1`

## 6. 结论

- 该仓库已形成“嵌入-提取-攻击-评估-扫描-报告”单仓闭环。
- 无攻击场景结果与论文主趋势一致。
- 鲁棒性数值与论文原表存在偏差，主要由实现平台、SVDSQ 完整推导近似化与测试图像差异导致。
