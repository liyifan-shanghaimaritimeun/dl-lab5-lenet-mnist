# -*- coding: utf-8 -*-
import json
import os

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

WORK = r"C:\Users\86136\Desktop\深度学习实验五_LeNet"
FIG = os.path.join(WORK, "figs")
OUT = os.path.join(WORK, "深度学习实验五-LeNet-李铱璠.docx")

with open(os.path.join(WORK, "results.json"), encoding="utf-8") as f:
    R = json.load(f)

doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(3.17)
sec.right_margin = Cm(3.17)
sec.top_margin = Cm(2.54)
sec.bottom_margin = Cm(2.54)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def set_run_font(run, ascii_font="Times New Roman", east="宋体", size=12, bold=None):
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def para(text="", size=12, bold=False, align=None, indent=True,
         before=0, after=0, line=1.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if indent:
        pf.first_line_indent = Pt(size * 2)
    if align is not None:
        p.alignment = align
    if text:
        r = p.add_run(text)
        set_run_font(r, "Times New Roman", "宋体", size, bold)
    return p


def title(text):
    return para(text, size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                indent=False, before=0, after=12, line=1.3)


def heading(text, before=10, after=4):
    p = para(text, size=12, bold=True, indent=False,
             before=before, after=after, line=1.5)
    p.paragraph_format.keep_with_next = True
    return p


def body(text):
    return para(text, size=12, indent=True, before=0, after=0, line=1.5)


def code(lines):
    for i, ln in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.first_line_indent = Pt(0)
        pf.left_indent = Cm(0.6)
        pf.space_before = Pt(4 if i == 0 else 0)
        pf.space_after = Pt(4 if i == len(lines) - 1 else 0)
        pf.line_spacing = 1.0
        r = p.add_run(ln if ln else " ")
        set_run_font(r, "Consolas", "宋体", 9)


def figure(name, caption, width_cm=14.2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.0
    pf.keep_with_next = True
    p.add_run().add_picture(os.path.join(FIG, name), width=Cm(width_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Pt(0)
    cap.paragraph_format.space_before = Pt(0)
    cap.paragraph_format.space_after = Pt(10)
    cap.paragraph_format.line_spacing = 1.0
    r = cap.add_run(caption)
    set_run_font(r, "Times New Roman", "宋体", 10.5, False)


def _border(tag, sz):
    el = OxmlElement(tag)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "000000")
    return el


def _none(tag):
    el = OxmlElement(tag)
    el.set(qn("w:val"), "none")
    el.set(qn("w:sz"), "0")
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "auto")
    return el


def table(caption, header, rows, widths):
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Pt(0)
    cap.paragraph_format.space_before = Pt(8)
    cap.paragraph_format.space_after = Pt(3)
    cap.paragraph_format.line_spacing = 1.0
    cap.paragraph_format.keep_with_next = True
    r = cap.add_run(caption)
    set_run_font(r, "Times New Roman", "宋体", 10.5, False)

    t = doc.add_table(rows=len(rows) + 1, cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    borders.append(_border("w:top", 12))
    borders.append(_none("w:left"))
    borders.append(_border("w:bottom", 12))
    borders.append(_none("w:right"))
    borders.append(_none("w:insideH"))
    borders.append(_none("w:insideV"))
    tblPr.append(borders)

    all_rows = [header] + rows
    for i, row in enumerate(all_rows):
        tr = t.rows[i]
        for j, val in enumerate(row):
            cell = tr.cells[j]
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(val))
            set_run_font(r, "Times New Roman", "宋体", 10.5, i == 0)
        if i == 0:
            for cell in tr.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                tcB = OxmlElement("w:tcBorders")
                tcB.append(_border("w:bottom", 6))
                tcPr.append(tcB)
        if i < len(all_rows) - 1:
            for cell in tr.cells:
                for cp in cell.paragraphs:
                    cp.paragraph_format.keep_with_next = True

    tail = doc.add_paragraph()
    tail.paragraph_format.space_before = Pt(0)
    tail.paragraph_format.space_after = Pt(0)
    tail.paragraph_format.line_spacing = 1.0


# ---------------- 正文 ----------------
title("实验名称：LeNet卷积神经网络实现MNIST手写数字识别")
para("姓名：李铱璠　学号：202410315057　班级：人工智能242",
     size=12, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=14, line=1.3)

heading("一、实验目的", before=6)
body("1.理解卷积神经网络的基本组成，明确卷积层、池化层和全连接层各自的作用。")
body("2.按参考代码补全LeNet的网络结构，完成MNIST手写数字的训练和测试。")
body("3.通过可视化卷积层的输出特征图，观察卷积核提取到的局部特征。")
body("4.把LeNet和实验四的MLP放在同一数据集上对比，理解卷积结构在图像任务上的优势。")

heading("二、实验内容")
body("实验沿用参考代码的流程：加载MNIST数据集，搭建LeNet，用Adam优化器和交叉熵损失训练30轮，每轮结束后在测试集上评估，最后取一批测试图可视化两层卷积的特征图。运行环境为CUDA，显卡为NVIDIA GeForce RTX 3050 Laptop GPU，PyTorch版本为2.6.0+cu124。")

heading("2.1 数据加载与预处理", before=8, after=3)
body("MNIST训练集60000张、测试集10000张，都是28×28的灰度图。预处理只做ToTensor，把像素值缩放到0~1。与实验四不同的是，这里不再手动把图片拉平，卷积层直接接收1×28×28的张量，空间结构被保留下来。批大小按参考代码取512，训练集和测试集都打乱顺序。")
code([
    "batch_size = 512",
    "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')",
    "",
    "trainloader = torch.utils.data.DataLoader(",
    "    datasets.MNIST('data', train=True, download=True,",
    "                   transform=transforms.Compose([transforms.ToTensor()])),",
    "    batch_size=batch_size, shuffle=True)",
    "",
    "testloader = torch.utils.data.DataLoader(",
    "    datasets.MNIST('data', train=False, download=True,",
    "                   transform=transforms.Compose([transforms.ToTensor()])),",
    "    batch_size=batch_size, shuffle=True)",
])

heading("2.2 LeNet网络结构", before=8, after=3)
body("网络由两个卷积块和三个全连接层组成。第一个卷积层用6个5×5的卷积核，padding取2，输出保持28×28；经过2×2、步长2的平均池化后变成6×14×14。第二个卷积层用16个5×5的卷积核，不做padding，输出16×10×10；再池化一次得到16×5×5。展平后是400维，依次经过120、84个神经元的全连接层，最后输出10类得分。卷积层和全连接层之间都用sigmoid激活。")
code([
    "class Net(nn.Module):",
    "    def __init__(self):",
    "        super(Net, self).__init__()",
    "        self.conv1 = nn.Conv2d(1, 6, 5, padding=2)",
    "        self.conv2 = nn.Conv2d(6, 16, 5)",
    "        self.fc1 = nn.Linear(5 * 5 * 16, 120)",
    "        self.fc2 = nn.Linear(120, 84)",
    "        self.clf = nn.Linear(84, 10)",
    "",
    "    def forward(self, x):",
    "        x = F.sigmoid(self.conv1(x))",
    "        x = F.avg_pool2d(x, kernel_size=2, stride=2)",
    "        x = F.sigmoid(self.conv2(x))",
    "        x = F.avg_pool2d(x, kernel_size=2, stride=2)",
    "        x = x.view(x.size(0), -1)",
    "        x = F.sigmoid(self.fc1(x))",
    "        x = F.sigmoid(self.fc2(x))",
    "        x = self.clf(x)",
    "        return x",
])
body("逐层统计参数量：conv1为1×6×5×5+6=156，conv2为6×16×5×5+16=2416，fc1为400×120+120=48120，fc2为120×84+84=10164，clf为84×10+10=850，合计61706个可训练参数。这个数量比实验四的MLP还少，但因为卷积核在整张图上共享，提取特征的能力反而更强。")

heading("2.3 训练设置", before=8, after=3)
body("损失函数用交叉熵，优化器按参考代码选Adam，学习率1e-2，训练30轮。每个batch依次做梯度清零、前向传播、求损失、反向传播和参数更新，同时累计损失和正确数，用于统计本轮的训练指标。")
code([
    "model = Net().to(device)",
    "optimizer = optim.Adam(model.parameters(), lr=1e-2)",
    "",
    "for epoch in range(30):",
    "    for batch_idx, (x, y) in enumerate(trainloader):",
    "        x, y = x.to(device), y.to(device)",
    "        optimizer.zero_grad()",
    "        out = model(x)",
    "        loss = F.cross_entropy(out, y)",
    "        loss.backward()",
    "        optimizer.step()",
])
body("30轮训练总耗时约434.5秒，平均每轮14.5秒。比实验四慢一些，主要是因为批大小从2048降到512，每轮的迭代次数多了4倍。")

heading("2.4 测试与评估", before=8, after=3)
body("每轮训练结束后切到评估模式，在测试集上统计平均损失和准确率。评估部分用no_grad关闭计算图，取输出中最大值的下标作为预测类别。为了画混淆矩阵和逐类别准确率，训练结束后又用不打乱的DataLoader完整跑了一遍测试集，把全部预测结果保存下来。")
code([
    "correct = 0",
    "testloss = 0",
    "with torch.no_grad():",
    "    for batch_idx, (x, y) in enumerate(testloader):",
    "        x, y = x.to(device), y.to(device)",
    "        out = model(x)",
    "        testloss += F.cross_entropy(out, y).item()",
    "        pred = out.max(dim=1, keepdim=True)[1]",
    "        correct += pred.eq(y.view_as(pred)).sum().item()",
    "",
    "acc = correct / len(testloader.dataset)",
    "testloss = testloss / (batch_idx + 1)",
])

heading("2.5 卷积特征图可视化", before=8, after=3)
body("参考代码在训练结束后取最后一批测试图的前5张，分别前向经过conv1和conv2，再把每个位置上的6个或16个通道求和，压成一张灰度图显示。这样能直观看到卷积层保留了哪些形状信息，以及池化之后分辨率下降到什么程度。")
code([
    "feature1 = F.sigmoid(model.conv1(x))",
    "feature1 = F.avg_pool2d(feature1, kernel_size=2, stride=2)",
    "feature2 = F.sigmoid(model.conv2(feature1))",
    "feature2 = F.avg_pool2d(feature2, kernel_size=2, stride=2)",
    "",
    "feature_map1 = feature1.detach().cpu().numpy()[:n]",
    "feature_map2 = feature2.detach().cpu().numpy()[:n]",
])

heading("三、实验结果与分析")
heading("3.1 总体结果", before=8, after=3)
table("表1  模型在训练集和测试集上的最终结果",
      ["指标", "数值"],
      [["训练损失", "0.0076"],
       ["训练准确率", "99.76%"],
       ["测试损失", "0.0419"],
       ["测试准确率", "98.90%"],
       ["可训练参数量", "61706"],
       ["训练总耗时", "434.5 s"]],
      [7.0, 5.0])
body("表1汇总了30轮训练结束时的指标。测试准确率98.90%，10000张测试图里只错了110张。训练准确率99.76%，比测试高0.86个百分点，训练损失0.0076远低于测试损失0.0419，说明模型在后期对训练集拟合得比较充分，存在轻微过拟合，但测试准确率仍在缓慢上升，没有出现明显退化。")

heading("3.2 训练曲线分析", before=8, after=3)
body("从图1看，损失在前3轮下降非常快，训练损失从2.050降到0.245，测试损失从1.566降到0.165；第5轮之后两条曲线都进入缓慢下降阶段，最后训练损失0.0076、测试损失0.0419。准确率方面，第1轮测试准确率只有40.35%，第2轮就跳到89.80%，第3轮94.83%，第6轮97.89%，第10轮98.38%，之后一直在98%到99%之间小幅波动，第30轮达到98.90%。")
body("曲线中训练损失在第1轮明显高于测试损失，这不是模型有问题，而是训练损失统计的是整个epoch内所有batch的平均值，前期参数还很差的部分也被算了进去，而测试是在这一轮训练全部结束后才做的。随着训练推进，两者的统计口径差异逐渐变小。")

figure("fig1_curves.png", "图1  30轮训练与测试的损失、准确率曲线", 10.5)
body("图1左为损失曲线，右为准确率曲线，蓝色实线是训练集，橙色虚线是测试集。两条曲线整体贴合，前期测试指标甚至略好于训练指标，后期训练指标反超，符合正常的训练规律。数据来源为本地MNIST数据集，由run_lenet.py在同一次运行中生成。")

heading("3.3 特征图分析", before=8, after=3)
figure("fig2_featuremaps.png", "图2  卷积层特征图（上：原图；中：conv1+池化；下：conv2+池化）", 13.0)
body("图2第一行是输入的原图，第二行是conv1加池化后的特征图，第三行是conv2加池化后的特征图。每行只显示了5个样本，特征图是把该层所有通道逐元素求和后压成的一张图。")
body("conv1的特征图基本保留了数字的轮廓，笔画边缘比原图更亮，背景被压暗，说明第一层卷积核主要在响应边缘和笔画方向。由于池化后尺寸从28×28降到14×14，线条开始出现锯齿。conv2的特征图只剩5×5，单个像素对应原图约5×5的区域，已经看不出具体笔画，只剩下大致的明暗分布。这也解释了为什么后面的全连接层能够把不同写法归到同一类：高层特征更关注整体形状，而不是某一个像素。")

heading("3.4 混淆矩阵与逐类别准确率", before=8, after=3)
pc = R["per_class_acc"]
cm = R["confusion"]
rows = []
for i in range(10):
    err = sum(cm[i]) - cm[i][i]
    rows.append([str(i), "%.2f%%" % (pc[i] * 100), str(err)])
table("表2  测试集各类别的准确率与错误数",
      ["类别", "准确率", "错误数"],
      rows,
      [3.6, 4.4, 3.6])
body("表2中各类准确率都在98%以上，最低的是数字6的98.43%，最高的是1的99.38%。原来最差的5从68.16%提升到98.54%，错误数从284张降到13张。")

figure("fig3_confusion.png", "图3  测试集混淆矩阵（行为真实标签，列为预测标签）", 9.0)
body("图3的对角线非常集中，非对角线上的数值基本是个位数。相对明显的错误是5被判成3共9张，9被判成4共8张，6被判成4和5各4张。这些样本要么笔画残缺，要么写法和标准字体差异较大。除此之外，模型几乎没有系统性的混淆方向，说明卷积提取的特征对不同类别有较好的区分度。")

figure("fig4_predictions.png", "图4  测试集预测示例（标题为“预测/真实”，绿色正确、橙色错误）", 14.6)
body("图4随机抽取32张测试图，标题全部是绿色，这批样本全部分对。其中包括笔画很细的1、倾斜的7和连笔的8，说明模型对书写风格的变化已经比较鲁棒。")

heading("3.5 与MLP的对比", before=8, after=3)
table("表3  LeNet与实验四MLP的对比",
      ["项目", "MLP", "LeNet"],
      [["网络结构", "784-128-10", "2卷积+3全连接"],
       ["激活函数", "ReLU", "Sigmoid"],
       ["优化器/学习率", "SGD / 0.01", "Adam / 0.01"],
       ["参数量", "101770", "61706"],
       ["测试准确率", "86.15%", "98.90%"],
       ["训练耗时", "252.5 s", "434.5 s"]],
      [4.4, 4.6, 4.6])
body("表3把两个实验放在一起比较。LeNet的参数量比MLP少约4万个，测试准确率却高出12.75个百分点，错误数从1385张降到110张。差距主要来自两点：一是卷积核在整张图上共享，同一个边缘检测器可以在不同位置复用，参数量小但感受野覆盖完整；二是池化带来了平移不变性，数字稍微移动几个像素不影响识别。MLP把图像拉平成784维后，相邻像素的空间关系被彻底打散，这是它准确率上不去的根本原因。")
body("代价是训练时间变长。LeNet每轮要处理117个batch，而MLP每轮只有30个batch，加上卷积运算本身比全连接更耗时，总时间多了约七成。不过从准确率提升的幅度看，这个代价是值得的。")

heading("四、实验小结", before=8, after=3)
body("这次实验的重点是把参考代码里的空补全。写的时候有几个地方容易出错：conv1的padding必须设2，这样28×28经过5×5卷积后尺寸不变，池化后是14×14；conv2不设padding，14×14经过5×5卷积后是10×10，再池化才是5×5，所以展平维度是16×5×5=400，不能写成别的数；池化的kernel_size和stride都要设成2，只写kernel_size会默认stride等于kernel_size，这里恰好一致，但换成别的尺寸就容易出问题。")
body("运行过程中F.sigmoid会提示已弃用，建议改用torch.sigmoid，但参考代码用的是F.sigmoid，为了和参考保持一致就没有改，结果不受影响。另外测试集的DataLoader在参考代码里设了shuffle=True，评估时打乱顺序不影响准确率，只是最后画特征图时取到的是随机一批图。")
body("最终测试准确率98.90%，比实验四的MLP高12.75个百分点，而参数量还更少。特征图的可视化很直观：第一层卷积保留笔画轮廓，第二层池化后只剩粗略的明暗分布，卷积网络正是靠这种逐层抽象来完成分类的。后续如果想继续提升，可以把sigmoid换成ReLU、平均池化换成最大池化，或者加入BatchNorm和数据增强，这些都是LeNet之后常见的改进方向。")

doc.save(OUT)
print("saved:", OUT)
