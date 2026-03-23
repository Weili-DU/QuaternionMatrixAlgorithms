# Simultaneous Decomposition of Some Quaternion Matrices

## 项目概述

本项目实现了基于四元数矩阵同时分解的图像隐写算法。该算法通过将多个四元数矩阵同时分解，实现了在彩色图像中嵌入隐秘信息的功能。

## 算法特点

- **四元数矩阵表示**: 使用四元数表示彩色图像的RGB通道
- **同时分解**: 对多个四元数矩阵进行同时分解
- **图像隐写**: 在HH子带中嵌入隐秘信息
- **DWT变换**: 使用离散小波变换进行图像分解
- **PNG输出**: 直接生成PNG格式的嵌入结果图像

## 文件结构

```
SimultaneousDecomposition/
├── README.md                    # 项目说明文档
├── src/                         # 核心算法实现
│   ├── main_fixed_png_complete.m    # 完整集成版本（推荐使用）
│   ├── embed_quaternion_images.m    # 四元数图像嵌入函数
│   ├── watermark_embedding.m        # 水印嵌入脚本
│   ├── five_quaternion_decomposition.m  # 五个四元数矩阵分解
│   ├── quaternion_matrix_to_rgb.m   # 四元数矩阵转RGB
│   ├── rgb_to_quaternion_matrix.m   # RGB转四元数矩阵
│   ├── dwt2_color.m                # 彩色图像DWT变换
│   ├── inverse_filter_synthesis.m  # 逆滤波合成
│   ├── DWT.m                       # DWT变换函数
│   └── Quaternion.m                # 四元数类定义
├── data/                         # 测试数据
│   ├── apple.png                   # 测试图像
│   ├── balloon..png               # 测试图像
│   ├── cat.png                    # 测试图像
│   ├── fox.png                    # 测试图像
│   ├── girl.png                   # 测试图像
│   └── logo.png                   # 隐秘信息图像
├── scripts/                      # 运行脚本
│   └── run_reproduce.m            # 复现脚本
├── configs/                      # 配置文件
│   └── default.json               # 默认参数配置
├── tests/                        # 测试文件
│   └── test_minimal.m             # 最小测试
├── outputs/                      # 输出目录
│   ├── figures/                   # 图表输出
│   ├── logs/                      # 日志文件
│   └── tables/                    # 数据表格
└── paper/                        # 论文相关
    └── notes.md                   # 论文笔记
```

## 使用方法

### 快速开始

运行完整集成版本：
```matlab
cd src
main_fixed_png_complete
```

### 使用复现脚本

```matlab
cd scripts
run_reproduce
```

### 详细步骤

1. **加载图像**: 程序会自动加载5个载体图像和1个隐秘信息图像
2. **DWT分解**: 对每个载体图像进行离散小波变换
3. **四元数转换**: 将HH子带转换为四元数矩阵
4. **同时分解**: 对五个四元数矩阵进行同时分解
5. **嵌入隐秘信息**: 在分解后的矩阵中嵌入隐秘信息
6. **重构图像**: 使用逆DWT重构嵌入后的图像
7. **保存结果**: 生成PNG格式的嵌入结果图像

## 输出文件

程序运行后会在 `outputs` 目录中生成以下文件：

- `cover_1.png` - `cover_5.png`: 原始载体图像
- `embedded_1.png` - `embedded_5.png`: 嵌入隐秘信息后的图像
- `secret_1.png` - `secret_5.png`: 隐秘信息图像
- `key_1.txt` - `key_5.txt`: 嵌入密钥文件

## 技术细节

### 四元数矩阵表示

彩色图像的RGB通道使用四元数表示：
- 实部: 0
- i虚部: R通道
- j虚部: G通道
- k虚部: B通道

### 同时分解算法

算法基于以下分解公式：
```
A_i = M_{i-1} * S_i * M_i^{-1}
```

其中：
- A_i: 第i个四元数矩阵
- M_i: 分解矩阵
- S_i: 特征矩阵

### 隐秘信息嵌入

隐秘信息嵌入公式：
```
S_i' = S_i + α * W
```

其中：
- S_i': 嵌入后的特征矩阵
- S_i: 原始特征矩阵
- α: 嵌入强度系数
- W: 隐秘信息四元数矩阵

## 依赖要求

- MATLAB R2018b 或更高版本
- 图像处理工具箱（推荐）
- 小波工具箱（可选，程序包含简化实现）

## 参考文献

[1] 四元数矩阵分解在图像处理中的应用研究
[2] 基于四元数的彩色图像隐写算法
[3] Simultaneous decomposition of quaternion matrices for image watermarking

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进本项目。