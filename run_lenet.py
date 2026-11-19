# -*- coding: utf-8 -*-
import json
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from torchvision import datasets, transforms

WORK = r"C:\Users\86136\Desktop\深度学习实验五_LeNet"
FIG = os.path.join(WORK, "figs")
os.makedirs(FIG, exist_ok=True)

torch.manual_seed(0)
np.random.seed(0)

batch_size = 512
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device:", device, torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")

train_set = datasets.MNIST(r"C:\Users\86136\data", train=True, download=False,
                           transform=transforms.Compose([transforms.ToTensor()]))
test_set = datasets.MNIST(r"C:\Users\86136\data", train=False, download=False,
                          transform=transforms.Compose([transforms.ToTensor()]))
trainloader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=True)
testloader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True)
print("train", train_set.data.shape, "test", test_set.data.shape)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5, padding=2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(5 * 5 * 16, 120)
        self.fc2 = nn.Linear(120, 84)
        self.clf = nn.Linear(84, 10)

    def forward(self, x):
        x = F.sigmoid(self.conv1(x))
        x = F.avg_pool2d(x, kernel_size=2, stride=2)
        x = F.sigmoid(self.conv2(x))
        x = F.avg_pool2d(x, kernel_size=2, stride=2)
        x = x.view(x.size(0), -1)
        x = F.sigmoid(self.fc1(x))
        x = F.sigmoid(self.fc2(x))
        x = self.clf(x)
        return x


model = Net().to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-2)
print(model)
print("params:", sum(p.numel() for p in model.parameters()))

epochs = 30
hist = {"train_loss": [], "train_acc": [], "test_loss": [], "test_acc": [], "time": []}
t0 = time.time()
x_last = None
for epoch in range(epochs):
    model.train()
    run_loss, run_correct, run_n = 0.0, 0, 0
    for batch_idx, (x, y) in enumerate(trainloader):
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        out = model(x)
        loss = F.cross_entropy(out, y)
        loss.backward()
        optimizer.step()
        run_loss += loss.item() * y.size(0)
        run_correct += out.argmax(1).eq(y).sum().item()
        run_n += y.size(0)

    tr_loss = run_loss / run_n
    tr_acc = run_correct / run_n

    model.eval()
    correct, testloss = 0, 0.0
    with torch.no_grad():
        for batch_idx, (x, y) in enumerate(testloader):
            x, y = x.to(device), y.to(device)
            out = model(x)
            testloss += F.cross_entropy(out, y).item()
            pred = out.max(dim=1, keepdim=True)[1]
            correct += pred.eq(y.view_as(pred)).sum().item()
            x_last = x
    acc = correct / len(testloader.dataset)
    testloss = testloss / (batch_idx + 1)

    hist["train_loss"].append(tr_loss)
    hist["train_acc"].append(tr_acc)
    hist["test_loss"].append(testloss)
    hist["test_acc"].append(acc)
    hist["time"].append(time.time() - t0)
    print("epoch:{:2d}  train_loss:{:.4f}  train_acc:{:.4f}  loss:{:.4f}  acc:{:.4f}".format(
        epoch, tr_loss, tr_acc, testloss, acc))

# ---------- 最终确定性评估 ----------
eval_loader = torch.utils.data.DataLoader(test_set, batch_size=512, shuffle=False)
model.eval()
all_pred, all_true = [], []
with torch.no_grad():
    for x, y in eval_loader:
        x = x.to(device)
        out = model(x)
        all_pred.append(out.argmax(1).cpu())
        all_true.append(y)
pred = torch.cat(all_pred).numpy()
true = torch.cat(all_true).numpy()

cm = np.zeros((10, 10), dtype=int)
for t, p in zip(true, pred):
    cm[t, p] += 1
per_class = (cm.diagonal() / cm.sum(axis=1)).tolist()
final_acc = float((pred == true).mean())

print("final acc:", round(final_acc, 4))
print("per class:", [round(v, 4) for v in per_class])

# ---------- 图1 训练曲线 ----------
ep = np.arange(1, epochs + 1)
fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.4))
ax[0].plot(ep, hist["train_loss"], color="#0072B2", lw=1.6, label="Train loss")
ax[0].plot(ep, hist["test_loss"], color="#D55E00", lw=1.6, ls="--", label="Test loss")
ax[0].set_xlabel("Epoch")
ax[0].set_ylabel("Cross-entropy loss")
ax[0].set_title("Loss Curves", fontsize=10)
ax[0].legend(frameon=False, fontsize=9)
ax[0].grid(alpha=0.25, ls=":")
ax[1].plot(ep, np.array(hist["train_acc"]) * 100, color="#0072B2", lw=1.6, label="Train acc")
ax[1].plot(ep, np.array(hist["test_acc"]) * 100, color="#D55E00", lw=1.6, ls="--", label="Test acc")
ax[1].set_xlabel("Epoch")
ax[1].set_ylabel("Accuracy (%)")
ax[1].set_title("Accuracy Curves", fontsize=10)
ax[1].legend(frameon=False, fontsize=9)
ax[1].grid(alpha=0.25, ls=":")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig1_curves.png"), bbox_inches="tight", dpi=200)
plt.close()

# ---------- 图2 卷积特征图 ----------
n = 5
img = x_last.detach().cpu().numpy()[:n]
feature1 = F.sigmoid(model.conv1(x_last))
feature1 = F.avg_pool2d(feature1, kernel_size=2, stride=2)
feature2 = F.sigmoid(model.conv2(feature1))
feature2 = F.avg_pool2d(feature2, kernel_size=2, stride=2)
feature_map1 = feature1.detach().cpu().numpy()[:n]
feature_map2 = feature2.detach().cpu().numpy()[:n]

fig, ax = plt.subplots(3, n, figsize=(10, 6.4))
for i in range(n):
    ax[0, i].imshow(img[i].sum(0), cmap="gray")
    ax[0, i].set_title("Input", fontsize=9)
    ax[0, i].axis("off")
    ax[1, i].imshow(feature_map1[i].sum(0), cmap="gray")
    ax[1, i].set_title("Conv1 + Pool", fontsize=9)
    ax[1, i].axis("off")
    ax[2, i].imshow(feature_map2[i].sum(0), cmap="gray")
    ax[2, i].set_title("Conv2 + Pool", fontsize=9)
    ax[2, i].axis("off")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig2_featuremaps.png"), bbox_inches="tight", dpi=200)
plt.close()

# ---------- 图3 混淆矩阵 ----------
fig, ax = plt.subplots(figsize=(4.8, 4.2))
ax.imshow(cm, cmap="Blues")
for i in range(10):
    for j in range(10):
        if cm[i, j]:
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=7,
                    color="white" if cm[i, j] > cm.max() * 0.5 else "#333333")
ax.set_xticks(range(10))
ax.set_yticks(range(10))
ax.set_xlabel("Predicted label")
ax.set_ylabel("True label")
ax.set_title("Confusion Matrix on Test Set", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig3_confusion.png"), bbox_inches="tight", dpi=200)
plt.close()

# ---------- 图4 预测示例 ----------
idx = np.random.RandomState(5).choice(len(true), 32, replace=False)
fig, axes = plt.subplots(4, 8, figsize=(9.0, 4.8))
for ax, k in zip(axes.ravel(), idx):
    ax.imshow(test_set.data[k].numpy(), cmap="gray")
    ok = pred[k] == true[k]
    ax.set_title("%d / %d" % (pred[k], true[k]), fontsize=9,
                 color="#009E73" if ok else "#D55E00")
    ax.axis("off")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig4_predictions.png"), bbox_inches="tight", dpi=200)
plt.close()

out = {
    "device": str(device),
    "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "",
    "torch": torch.__version__,
    "batch_size": batch_size,
    "lr": 0.01,
    "epochs": epochs,
    "params": int(sum(p.numel() for p in model.parameters())),
    "history": hist,
    "final": {"test_loss": float(hist["test_loss"][-1]), "test_acc": final_acc,
              "train_loss": float(hist["train_loss"][-1]), "train_acc": float(hist["train_acc"][-1])},
    "per_class_acc": [float(v) for v in per_class],
    "confusion": cm.tolist(),
}
with open(os.path.join(WORK, "results.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("saved results.json")
