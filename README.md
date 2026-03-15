# QuaternionMatrixAlgorithms

[简体中文](./README.zh-CN.md)

A reproduction and experimentation repository for quaternion matrix algorithms, including independent subprojects with runnable scripts, tests, and generated outputs.

## Repository Structure

- `ColorImageRecovery/`: Color image recovery with low-rank quaternion representation
- `CommutativeQuaternionMatrix/`: Decomposition and generalized inverse experiments for commutative quaternion matrices
- `DualQuaternionLU/`: Reproduction of LU decomposition for dual quaternion matrices
- `Low-RankQuaternionMatrix/`: Reproduction of low-rank quaternion matrix decomposition models
- `QuaternionCUR/`: Reproduction of quaternion CUR decomposition
- `SplitQuaternionSVD/`: Reproduction of split quaternion matrix SVD
- `Watermarking/`: Color image watermarking experiments based on quaternion decomposition

Typical subproject layout:

- `paper/`: Paper notes and metadata
- `src/`: Core algorithm implementations
- `scripts/`: Reproduction entry scripts
- `configs/`: Parameter configurations
- `tests/`: Minimal runnable tests
- `outputs/`: Figures, tables, and logs

## Copyright and Paper Notes

This repository does not provide original paper PDF files. Paper titles and source information are documented in each subproject `README.md`.

## Usage

Enter any subproject and read its `README.md` first, then install dependencies and run reproduction scripts as instructed.
