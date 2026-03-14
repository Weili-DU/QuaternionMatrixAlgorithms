# reproduction_report

## 1. 复现目标与完成状态

- 目标：跑通 LRQD 核心算法（基础梯度法与改进法），并复现至少一组与论文趋势一致结果
- 状态：已完成
- 结论：在本仓库默认配置与参数扫描下，算法2在 PSNR 与 MSSI 指标上均显著优于算法1，趋势与论文一致

## 2. 论文关键信息提取

核心模型：
$$
\min_{A,H,W}\frac{1}{2}\|HW-A\|_F^2,\quad A_\Omega=D_\Omega
$$

关键梯度：
$$
\nabla_A f=A-HW,\quad \nabla_H f=(HW-A)W^*,\quad \nabla_W f=H^*(HW-A)
$$

停止条件（论文）：$\|X_{k+1}-X_k\|_F<\epsilon$。  
论文实验设置关键信息：$\rho=0.7,\ \alpha=0.0025,\ \epsilon=10^{-4}$，并比较算法1与算法2的恢复指标。

## 3. 可执行伪代码

算法1（基础）：
1. 初始化 $A_0,H_0,W_0$
2. $H_{k+1}\leftarrow H_k-\alpha(H_kW_k-A_k)W_k^*$
3. $W_{k+1}\leftarrow W_k-\alpha H_{k+1}^*(H_{k+1}W_k-A_k)$
4. $A_{k+1,\Omega}\leftarrow D_\Omega$，$A_{k+1,\Omega^c}\leftarrow(A_k-\alpha(A_k-H_{k+1}W_{k+1}))_{\Omega^c}$
5. 若 $\|X_{k+1}-X_k\|_F<\epsilon$ 停止

算法2（改进）：
1. 前三步同算法1
2. $A_{k+1,\Omega}\leftarrow D_\Omega$，$A_{k+1,\Omega^c}\leftarrow(H_{k+1}W_{k+1})_{\Omega^c}$
3. 若 $\|X_{k+1}-X_k\|_F<\epsilon$ 停止

## 4. 数值结果与论文趋势对齐

来自 `outputs/logs/run_summary.json` 的平均指标：

- Degraded：PSNR = 11.3730，MSSI = 0.2474
- Algorithm 1：PSNR = 21.7309，MSSI = 0.7353
- Algorithm 2：PSNR = 26.0855，MSSI = 0.8918

趋势判断：

- 算法2 > 算法1 > 退化输入（PSNR 与 MSSI 均成立）
- 与论文“改进算法整体更优”的趋势一致

参数扫描最优组合（按算法2相对算法1增益）：

- `alpha=0.005, eps=0.001, max_iter=80, rank=6`
- PSNR 增益：`+6.8486`
- MSSI 增益：`+0.3219`

## 5. 偏差分析

- 论文使用 MATLAB R2022a 与真实彩色图像；本仓库当前为 Python 实现与可控合成低秩数据
- 因数据分布、实现细节、数值库差异，绝对数值不与论文逐项完全一致
- 但关键趋势（算法2优于算法1）稳定复现

## 6. 缺失项清单（影响“逐数值对齐”）

以下文件缺失会影响与论文表1逐项精确对齐：

- 论文实验所用的 6 张原始测试图像  
  - 用途：复现论文表1各图像序号结果  
  - 建议获取方式：联系作者或按论文引用的数据源补齐
- 论文中退化图像的随机采样索引具体种子/索引文件  
  - 用途：逐样本精确重现实验输入  
  - 建议获取方式：请求作者提供随机种子或观测索引矩阵

在缺失项未补齐前，本仓库可完成“算法闭环复现与趋势一致性验证”，但不能保证“逐样本同值复现”。

