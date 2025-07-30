MLProgress - Minimalist Progress Bar for Machine Learning

[图片] https://img.shields.io/badge/python-3.6%2B-blue

[图片] https://img.shields.io/badge/license-MIT-green

[图片] https://img.shields.io/pypi/v/mlprogress

MLProgress is a minimalist progress bar library specifically designed for machine learning tasks, providing only the most essential progress display functionality without complex dependencies.

功能特点

- ⚡ Ultra Lightweight - Core code less than 100 lines
- 🚀 No External Dependencies - Uses only Python standard library
- 🔍 ML-Optimized - Default descriptions tailored for ML scenarios
- 🛠️ Easy to Use - Intuitive API design
- 📦 Multiple Usage Modes - Supports regular updates, context managers and iterator wrapping

安装

pip install mlprogress

快速开始

Basic Usage

from mlprogress import MLProgress

total_epochs = 10
progress = MLProgress(total_epochs, "Training")

for epoch in range(total_epochs):
    # Your training code
    progress.update()

Using Context Manager

from mlprogress import MLProgress

with MLProgress(100, "Processing Data") as progress:
    for i in range(100):
        # Data processing code
        progress.update()

Wrapping Iterators

from mlprogress import MLProgress

data = load_large_dataset()  # Your large dataset
for batch in MLProgress.iter(data, "Loading Data"):
    # Process each batch
    process(batch)

高级配置

# Custom progress bar style
progress = MLProgress(
    total=100,
    description="Custom Progress",
    bar_length=50,       # Progress bar length
)

输出示例

Training Model: [####################-----] 75%
Processing Data: [############----------] 50%
Custom Progress: [##############--------] 60%

开发指南

Running Tests

python -m unittest discover tests

Building and Releasing

python setup.py sdist bdist_wheel
twine upload dist/*

贡献

Issues and Pull Requests are welcome! Please ensure:

1. Follow existing code style
2. Add appropriate test cases
3. Update documentation accordingly

许可证

This project is licensed under the "MIT License" (LICENSE).

免责声明

This software is provided "as is" without any warranties. Users assume all risks. Thorough testing is recommended before production use.

<p align="center">

✨ Happy Coding! ✨

</p>