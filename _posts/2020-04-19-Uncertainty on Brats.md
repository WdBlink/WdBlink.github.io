---
layout:     post
title:      "Uncertainty on Brats"
subtitle:   "科研碎片"
date:       2020-04-19
author:     "Echooo"
header-img: "img/post-bg-unix-linux.jpg"
catalog: true
tags:
    - 论文阅读
---



# Uncertainty On BraTS

uncertainty这项理论应用到临床医学的意义重大，但实际上关于各种uncertainty方法在医学数据上的效果以及挑战的相关研究仍然很少。而以目前的一些研究成果来看，当前的各种方法的表现实际上是非常接近的，值得注意的是，当前的方法虽然在数据集层面上表现不错，但**在具体样本层面上表现很不稳定**。**辅助网络（auxiliary networks）**可以替代常规的uncertainty方法因为它们可以适用于预训练模型。



医疗图像分割领域，不确定性主要关注点在以下三个层次：

1. 体素级别的uncertainty，这对于辅助医生的诊断至关重要
2. 实例分割层面的不确定性（将体素不确定性汇总），能够降低错误率
3. 样本层面的不确定性，这样能告诉我们当前得到的分割结果是否成功

softMax entropy（baseline）中 uncertainty 的度量：
$$
H = -\sum_{c\in C}\frac{p_clog(p_c)}{log(|C|)} \in[0,1]
$$


$p_c$是第$c$类预测的softMax输出，$C$是所有类的集合。

#### 几种benchmark：

a) Bayesian uncer- tainty estimation via test-time dropout [5],

test-time dropout 可以认为是BNN的近似。T个随机dropout网络生成概率预测，将这些概率的归一化熵用作不确定性的度量，$p_c=\frac{1}{T}\sum^T_{t=1}p_{t,c}$。目前有两种dropout方法，一种是在每个卷积层后都加一个p=0.05的dropout（称为baseline+MC），另一种是在中心位置使用p=0.5的dropout（称为center+MC），两个方法同样使用T=20。

b) aleatoric uncertainty estimation via a second network output [9]

MC dropout 衡量模型预测中存在的不确定性，偶然不确定性方法衡量观测中的固有噪声。这种方法学习一个函数$f(x)$，输入训练数据$x$得到两个输出 $[\hat x,\sigma^2]$，这两个输出是经过高斯噪声扰乱的logits的均质和方差。通过 **aleatoric loss** 来优化两个输出，同时将这两个输出作为uncertainty的度量。

c) uncertainty estimation via ensembling of networks [10].

使用k个训练好的网络取平均，$p_c=\frac{1}{K}\sum^K_{k=1}p_{k,c}$。每个独立的网络使用同样的模型算法，但使用不同的子集和不同的初始化参数训练。

d) Auxiliary network

辅助网络方法是用来预测样本级的分割表现的。有两个辅助网络：

* **auxiliary feat**，包括三个连续的1*1卷积网络与分割网络的最后一个特征层相连。
* **auxiliary segm**，是一个完全独立的U-net网络，网络的输入为原始图像和分割模型得到的分割mask。

#### 几种metric：

* **Calibration** ，当一个模型在 $P(y=1|f(x)=p)=p$ （二分类模型）时，对于自己的预测$f(x)$置信度为$p$，那么则称为完美的校准。举个例子，这意味着置信度为0.7的模型预测100次，那么刚好其中70个的预测是正确的。
* **Uncertainty-Error overlap** ，通常，分割任务不需要完美的校准，但是对于模型来说，确定哪里出错了并确定哪里正确就足够了。U-E其实表达的是分割错误区域和低置信度区域（阈值控制）之间的重合度。
* **Corrections** ，有几个简写需要注意，TPU (uncertainty in the true positives)，TNU (uncertainty in the true negatives)，FPU(uncertainty in the false positives)，FNU(uncertainty in the false negatives)。当满足假阳性的不确定性FPU > 真阴性的不确定性TPU时，可以通过修正假阳性来提升Dice系数。表中BnF（benefit condition for false positive removal）作为简写。

#### Result

![image-20200419223633325](https://tva1.sinaimg.cn/large/007S8ZIlly1gdzgbrmhetj30pn09had7.jpg)