# 深度学习实验五：LeNet卷积神经网络实现MNIST手写数字识别

用PyTorch复现LeNet-5结构，在MNIST手写数字数据集上完成训练、测试与结果分析。

## 环境

- Python 3.10
- PyTorch 2.6.0+cu124
- torchvision
- 显卡：NVIDIA GeForce RTX 3050 Laptop GPU

## 网络结构

```
输入 1×28×28
→ Conv2d(1,6,5,padding=2) → Sigmoid → AvgPool2d(2,2)
→ Conv2d(6,16,5) → Sigmoid → AvgPool2d(2,2)
→ Flatten(5×5×16) → Linear(400,120) → Sigmoid
→ Linear(120,84) → Sigmoid
→ Linear(84,10)
```

可训练参数共61706个。

## 超参数

| 项目 | 取值 |
| --- | --- |
| batch size | 512 |
| 优化器 | Adam |
| 学习率 | 0.01 |
| 训练轮数 | 30 |

## 结果

| 指标 | 数值 |
| --- | --- |
| 训练损失 | 0.0076 |
| 训练准确率 | 99.76% |
| 测试损失 | 0.0419 |
| 测试准确率 | 98.90% |
| 训练总耗时 | 434.5 s |

## 文件说明

- `深度学习实验五-LeNet-李铱璠.docx`：实验报告
- `深度学习实验五-LeNet-李铱璠.pdf`：报告PDF版
- `run_lenet.py`：完整实验代码，运行后生成全部图表和`results.json`
- `results.json`：逐轮损失、准确率、逐类别准确率与混淆矩阵
- `figs/`：实验报告中的四张图
- `build_report.py`：根据`results.json`生成docx报告

## 运行

```bash
python run_lenet.py
```

MNIST数据默认从`C:\Users\86136\data`读取，本地不存在时会自动下载。
