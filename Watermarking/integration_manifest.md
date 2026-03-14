# integration_manifest

## 1. 目标

本清单用于将当前单篇复现结果并入后续总仓，明确路径映射、依赖与执行入口。

## 2. 路径映射

- 论文原文：
  - `paper/Wang2025_watermark.pdf`
- 核心实现：
  - `src/watermarking.py`
  - `src/attacks.py`
  - `src/metrics.py`
  - `src/io_utils.py`
- 配置与执行：
  - `configs/default.json`
  - `scripts/run_reproduce.py`
  - `scripts/run_reproduce.ps1`
- 测试：
  - `tests/test_consistency.py`
- 输出产物：
  - `outputs/figures/*`
  - `outputs/tables/*`
  - `outputs/logs/run_summary.json`
- 说明文档：
  - `README.md`
  - `reproduction_report.md`
  - `integration_manifest.md`

## 3. 依赖说明

- Python 3.10+
- `numpy`
- `Pillow`
- `pypdf`（用于论文文本提取辅助）

统一依赖文件：
- `requirements.txt`

## 4. 整合时建议保留接口

- 嵌入接口：`embed_watermark(host_rgb, watermark_rgb, rho, arnold_iters, arnold_params)`
- 提取接口：`extract_watermark(watermarked_rgb, key)`
- 攻击入口：`build_attacks()`

## 5. 与总仓集成策略

- 作为单论文子模块接入时，建议保留 `configs/default.json` 作为默认配置模板。
- 若总仓已有统一数据目录，可通过修改 `host_path/watermark_path` 完成重定向。
- 若总仓已有统一评估框架，可直接消费 `outputs/tables/*.csv`。

## 6. 已知偏差与兼容性

- 当前实现是可运行复现版，核心流程与论文一致，但非论文 MATLAB 原始代码。
- 若后续要做严格逐表对齐，建议补充：
  - 论文原始数据集与水印集；
  - 完整 SVDSQ 细节实现；
  - 论文中全部攻击参数与组合攻击项。
