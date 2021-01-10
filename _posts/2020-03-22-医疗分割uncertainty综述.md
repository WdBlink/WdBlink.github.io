---
layout:     post
title:      "医疗分割uncertainty综述"
subtitle:   "科研碎片"
date:       2020-03-22
author:     "Echooo"
header-img: "img/post-bg-unix-linux.jpg"
catalog: true
tags:
    - 论文阅读
---



# 医疗分割uncertainty综述

## Abstract

近年来，深度学习推动了医学成像分割领域的最新发展。 但是，先前的工作倾向于将准确性最大化，而忽略了预测不确定性。 在像素级上对不确定性进行建模与精度一样重要，尤其是在医疗场景中，因为它可以使临床医生了解模型输出的可信度。本文对uncertainty的几种基本的方法进行说明，并对2019年将uncertainty方法应用到医疗分割的论文进行综述。



## 1.Introduction

目前深度学习在很多领域的表现都非常好，现在大多数深度学习算法几乎只能给出一个**高置信度**的预测结果，而不能给出模型自己对结果有多么确信。深度学习模型得到的这些高置信度预测通常由softmax产生，因为softmax概率是用快速增长的指数函数计算的，因此对softmax输入（即logit）进行少量添加就会导致输出分布发生实质性变化。

实际上在理想情况下，当你给我几张猫和狗的图片然后要求我对一张新的猫照片进行分类，那么我应该非常有信心地返回预测。 但是，如果你给我一张鸵鸟的照片，并强迫我确定它是猫还是狗，那么这种情况下，我应该以较低的预测信心返回我的结果。

模型具有这种能力在很多领域都是至关重要的，比如在无人驾驶领域，能够使机器在决策时采用更加合理的方式。在医疗领域，医生可以通过模型对于诊断的确信度来加以判断等等。

假设训练数据集表示为$D = {(x_i,y_i)}^N_{i=1}$，输入为$x_i$ ，分割标注为$y_i$，神经网络的参数为$\theta$。我们可以将神经网络想象成一个条件分布$p(y|x,\theta)$。当输入测试数据时，**预测后验分布**为$p(y_*,x_*,D) = \int p(y_*|x_*,\theta)p(\theta|D)d\theta$，这里$p(\theta|D)$是给定训练集得到的参数$\theta$的后验分布。预测的后验分布很难直接得到，因此需要通过某些比较易得的分布$q_\lambda(\theta)$进行近似，其中$\lambda$被称为variational parameters。通过最小化KL散度$KL[q_\lambda(\theta)||p(\theta|D)]$的相反数，便能得到$p(\theta|D)$的近似$q_\lambda(\theta)$。而最终想要得到的**预测不确定性**是预测后验分布的方差。

通常，不确定性主要有两种类型，**偶然不确定性**和**认知不确定性**。偶然不确定性是对数据中固有的，不可减少的噪声的度量，通常与数据采集过程相关。 

![图1](https://tva1.sinaimg.cn/large/00831rSTly1gcshyg2awoj30fr06lt9b.jpg)

认知不确定性是我们对模型参数真实值的不确定性，这是由训练集的有限大小引起的。 随着训练集规模的增加，认知不确定性渐近趋于零。 

![截屏2020-03-13下午6.55.02](https://tva1.sinaimg.cn/large/00831rSTly1gcsi0mfmjnj30h002a3yt.jpg)

通常情况下认知不确定性很难测量，原因是我们需要数据集提供的ground truth进行训练，而很难获取数据集和真实情况的ground truth的差距。假设训练集有N个图片$\{x_i\}^N_{i=1}$，如果第$i$个图像有D个分割标注者$\{y^1_i,...,y^D_i\}$，定义这些像素点的分割标记的偶然不确定性为$V_{p(D)}[y_i]=\frac{1}{D}\sum ^D_{j=1}(y^j_i-\bar{y}_i)^2$，其中$\bar{y}_i=\frac{1}{D}\sum ^D_{j=1}y^j_i$。



## 2.Classical methods

### 2.1 Bayesian NNs

uncertainty中一个**传统并且基本的思想**来自于贝叶斯网络的应用，思想的关键很简单：在贝叶斯世界观中，所有事物都附有概率分布，包括模型参数（NN中的权重和偏差）。例如在编程语言中，我们拥有可以采用特定值的变量，并且每次访问该变量时，都会获得相同的值。与此相反，在贝叶斯世界中，我们有类似的实体，它们被称为随机变量，每次访问它时都会赋予不同的值。 因此，如果X是代表正态分布的随机变量，则每次访问X时，它的值都会不同。

**从随机变量获取新值的过程称为采样**。 产生什么值取决于随机变量的相关概率分布。 与随机变量关联的概率分布越广，其值的不确定性就越大，因为根据（宽）概率分布，它可以取任何值。如果随机变量是两次掷骰子的位数之和，则每次掷骰都会获得一个值，该值的概率取决于下图2所示分布。 这意味着最可能获得的点数总和是7，最不可能获得的是2和12。

![图2](https://tva1.sinaimg.cn/large/00831rSTly1gcvsx511y8j30x20n0afu.jpg)

在传统的神经网络中具有固定的权重和偏差，这些权重和偏差决定了如何将输入转换为输出。 在贝叶斯神经网络中，所有权重和偏差都具有附加的概率分布。 为了对图像进行分类，需要对网络进行多次运行，每次都使用一组新的采样权重和偏差，而不是一组输出值，得到的是多个集合。每个运行一次。 输出值集表示输出值的概率分布，因此可以找出每个输出的置信度和不确定性。 如果输入图像是网络从未见过的东西，那么对于所有输出类别，不确定性都将很高，网络应该解释说：“我真的不知道该图像是关于什么的”。

推理是整个过程中最关键的步骤。它基于著名的贝叶斯定理。
$$
P(A|B)=\frac{P(B|A)P(A)}{P(B)}
$$
假设A是权重和偏差的初始概率分布（称为**先验priors**，通常是一些标准分布，如正态或均匀随机），而B是训练数据（图像/标签）。贝叶斯定理的关键思想是，我们想使用数据来找出权重和偏差$P(A|B)$的更新分布（**posterior后验**）。 就像使用网络的初始随机分配的权重和偏差一样，参数（先验）的初始分布将给我们带来错误的结果。只有使用数据获取参数的更新分布（近似于后验）后，我们才能使用网络对图像进行分类。

权重和偏差的概率分布通过贝叶斯定理进行更新。变分贝叶斯方法的要点在于，由于我们无法精确地计算后验，因此我们可以找到与其最接近的“行为良好（well-behaved）”的概率分布。 “行为良好”是指可以由一小部分参数（如均值或方差）表示的分布（如正态分布或指数分布）。因此，在“行为良好”的分布中随机初始化这些参数之后可以通过相应的损失函数逐渐梯度下降，更新分布的参数（例如均值或方差），以使得结果分布尽可能更接近要计算的后验，接近度的度量称为[Evidence Lower Bound（ELBO)](http://legacydirs.umiacs.umd.edu/~xyang35/files/understanding-variational-lower.pdf)。  

### 2.2 Monte Carlo Dropout

论文链接：

[1]Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning：https://arxiv.org/pdf/1506.02142.pdf

[2]Bayesian SegNet: Model Uncertainty in Deep Convolutional Encoder-Decoder Architectures for Scene Understanding:https://arxiv.org/pdf/1511.02680.pdf

![图3](https://tva1.sinaimg.cn/large/00831rSTly1gcvsf9dmm6j30oz06j41u.jpg)

这篇paper的模型使用dropout作为上面讲到的[BNN](https://towardsdatascience.com/making-your-neural-network-say-i-dont-know-bayesian-nns-using-pyro-and-pytorch-b1c24e6ab8cd)中的近似推断方法，因此也使用dropout作为从模型的后验分布中获取样本的方法。 论文[1]将这项技术与贝叶斯卷积神经网络中具有权重分布的伯努利分布的变异推理联系起来。 我们利用这种方法对我们的细分模型执行概率推断，从而产生了Bayesian SegNet。

通常，精确的后验分布是很难得到的，因此我们需要近似估计这些权重的分布。训练模型的时候使用dropout，并在测试时间使用dropout**采样权重的后验分布**，以获得softmax类概率的后验分布。 **将这些样本的均值用于细分预测，并使用方差输出每个类别的模型不确定性**。图4显示了分段预测和模型不确定性估计过程的示意图

![图4](https://tva1.sinaimg.cn/large/00831rSTly1gcvsfa1punj30zh06vgqk.jpg)

### 2.3 Deep Ensemble

[3]Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles:https://arxiv.org/pdf/1612.01474.pdf

与BNN相比（变分推理或MCMC方法），简化了方法的实现，只需要对标准神经网络稍加修改，并且适合于分布式计算，适合部署在大规模深度学习应用中。

方法相当于将ensemble（把多个模型的预测结果取平均值来获得“model uncertainty”）和对抗训练（提高局部平滑度）结合。只需要很少的超参数调整，并且可以很容易地用于各种架构，例如MLP，CNN等，包括那些不使用Dropout的架构。



## 3.医疗影像分割中的应用

### 3.1 Probabilistic U-Net 

https://arxiv.org/abs/1806.05034

这篇文章是发表在NIPS2017的工作。定义N为标准正态分布，φ, θ是由神经网络参数化的函数。我们可以用prior net和posterior net来建模，两个网络使用相同的结构但不共享权重。下图为**prob-U-Net的架构**，训练阶段使用图b的网络结构，将图像和ground truth叠加在一起输入到posterior net中，相当于一个encoder将输入编码到正态分布的**隐空间**，将训练样本输入到prior net中编码到另一个正态分布的隐空间，计算两个分布的KL散度作为损失函数的一部分。由于posterior net的输入有标签信息，所以称其编码后的分布为**后验分布**，prior net仅有原始图像输入，因此得到的分布为先验分布。通过KL散度训练网络将先验分布和后验分布尽可能相近想要达到的效果是，在使用如下图a网络结构测试和验证时，仅输入图像也能让网络得到近似于“后验”的分布，这个分布的作用是为了进行连续采样，每个采样值再经过上采样插值到作为解码器的U-NET的最后一层特征层中，从而得到不同的预测结果。

![图5](https://tva1.sinaimg.cn/large/00831rSTly1gctbp31g1zj30o209uabg.jpg)

这篇文章中使用的数据集为LIDC-IDRI，每个输入数据有4个标注者。

### 3.2 PHiSeg 

https://arxiv.org/abs/1906.04045

这是一篇发表在MICCAI2019的工作，它解决了prob U-Net在只有一个标注者的时候，生成的多个预测之间差异度不够的问题（如图6第四行）。

![图6](https://tva1.sinaimg.cn/large/00831rSTly1gcthrqnhm0j30kx0hh76t.jpg)

作者提出了一种新颖的分层概率模型，该模型可以产生与多个与注释结果的分布紧密匹配的分割样本。 受拉普拉斯金字塔启发，该模型以低分辨率生成输出，然后以越来越高的分辨率不断细化segmentations的分布，来生成image-conditional的分割样本。与先前的工作相比，每个分辨率级别的变化都由单独的隐变量（latent code）控制，从而避免了prob-UNET的问题。

如图7所示，作者假设给定输入图像x的分割s是根据Fig. 1所示的图形模型从L个尺度的隐变量 ![[公式]](https://www.zhihu.com/equation?tex=z_l) 生成的

![图7](https://tva1.sinaimg.cn/large/00831rSTly1gctobqelfjj30ku044myg.jpg)

PHiSeg的模型结构如图8所示，和prob U-Net网络结构上的主要区别在于posterior network和prior network的结构换成了U型结构，从而能够生成多尺度的特征层的隐变量，在likelihood network中将这些多尺度信息结合。

![图8](https://tva1.sinaimg.cn/large/00831rSTly1gctokks07rj30nl0kr77f.jpg)

### 3.3 Addressing Failure Prediction by Learning Model Confidence

https://arxiv.org/pdf/1910.04851.pdf

这篇文章是从度量的角度，为深度神经网络模型的预测提供更可靠的置信度度量，配备了这种置信度度量，系统可以决定遵守该预测，或者相反，例如将其移交给人或备用系统或其他传感器，或只是触发警报。

在分类的背景下，使用神经网络进行置信度估计的一种广泛使用的baseline是采用预测类别的概率值，即softmax层输出给出的最大类别概率（Maximum Class Probability MCP）。但使用MCP作为度量仍然有几个理论缺陷，比如softmax概率是未经校准的，对对抗攻击敏感，并且很难检测离群样本点。

这项工作中专门解决的另一个重要问题与MCP有关的置信度分数的排名问题： 如图9a所示，对于在CIFAR-10数据集上训练的小型卷积网络，错误预测和正确预测的MCP置信度值重叠。这个问题来自以下原因：由于使用了最大softmax输出，因此MCP在设计上会导致较高的置信度值，即使对于错误的置信度也是如此。 另一方面，如图9b所示，模型相对于真实类别的概率得到了一个较合理的模型置信度。 错误类的置信度分布转移到较小的值，而正确的预测仍与高值相关联，从而使这两种类型的预测之间具有更好的可分离性。

![图9](https://tva1.sinaimg.cn/large/00831rSTly1gcvkyflg8kj30lz08qmy2.jpg)

基于此观察，作者提出了一种使用深度神经网络进行故障预测的新方法。 首先基于使用TCP的思想引入了新的置信度标准，为故障预测的背景提供了理论保证。 由于真实类在测试时显然是未知的，因此我们引入了一种从数据中学习给定目标置信度标准的方法如图10所示：假设需要学习的TCP置信度值为$c^*(x,y*)=P(Y=y^*|w,x)$，提出了一个置信度神经网络ConfidNet，网络参数为$\theta$，网络输出为$\hat{c}(x,\theta)$。训练时需要找到一个接近于$c^*(x,y^*)$的$\hat{c}(x,\theta)$。

![图10](https://tva1.sinaimg.cn/large/00831rSTly1gcvr7w9orkj30mb0be41j.jpg)

作者在分类和分割数据集上都测试了提出的方法，实验表明，从MCP到贝叶斯不确定性，以及专为故障预测而专门设计的最新方法，作者的方法始终优于前者。并提供了开源代码（https://github.com/google/TrustScore）

### 3.4 Supervised Uncertainty Quantification for Segmentation with Multiple Annotations

https://arxiv.org/pdf/1907.01949.pdf

这篇工作发表在MICCAI2019上，主要是对prob U-Net进行了两点改进：首先是prob U-Net中不包含衡量认知不确定性的机制，这可以通过在U-Net的最后一个卷积层之后添加变分dropout来实现。其次，假设训练集有N个图片$\{x_i\}^N_{i=1}$，如果第$i$个图像有D个分割标注者$\{y^1_i,...,y^D_i\}$，定义这些像素点的分割标记的偶然不确定性为$V_{p(D)}[y_i]=\frac{1}{D}\sum ^D_{j=1}(y^j_i-\bar{y}_i)^2$，其中$\bar{y}_i=\frac{1}{D}\sum ^D_{j=1}y^j_i$，标注之间的交叉熵$V_{p(D)}$可以作为校准偶然不确定性的目标。

 ![图11](https://tva1.sinaimg.cn/large/00831rSTly1gcvyn4sdjej30ju0c7dk3.jpg)

在LIDC-IDRI肺结节CT数据集和MICCAI2012前列腺MRI数据集上训练并测试模型，证明模型可以改善预测不确定性估计。 还发现，我们可以提高样本准确性和样本多样性。作者提供了开源代码（https://github.com/stefanknegt/Probabilistic-Unet-Pytorch）

### 3.5 Assessing Reliability and Challenges of Uncertainty Estimations for Medical Image Segmentation

 https://arxiv.org/pdf/1907.03338.pdf

这篇工作发表在MICCAI2019上。作者将几种uncertainty主流方法（Baseline uncertainty: Softmax entropy；MC dropout；Aleatoric uncertainty；Ensembles；Auxiliary network.）应用到BraTS2018数据集上评估了它们的Dice和uncertainty的质量。

![](https://tva1.sinaimg.cn/large/00831rSTly1gcw0pribraj30lq080dic.jpg)

Aleatoric方法和large dropout的方法性能最差。 aleatoric方法无法在分割错误的位置（即较低的U-E）产生不确定性，因此无法通过校正来改善分割结果，而MC dropout主要对分割性能和ECE产生负面影响。结果进一步表明，与非MC版本（baseline和中心）相比，MC dropout通常可以提高ECE，UE和Dice系数，但dropout概率设置较大会导致较差的性能，基于MC dropout的方法在很大程度上取决于dropout对分割性能的影响。

ensemble方法会按顺序生成最可靠的结果，并且通常是一个不错的选择（如果资源允许的话）。

作者还观察到辅助网络的良好性能，这些网络通常经过了良好的校准，并受益于其细分网络（即baseline模型）的良好细分性能。

关于指标，作者注意到低ECE值源于对ECE产生积极影响的大量低置信度背景区域。这也解释了BraTS数据集的较低ECE值，由于附加的图像尺寸，该数据集包含比ISIC数据集更多的背景。

![图12](https://tva1.sinaimg.cn/large/00831rSTly1gcw0qa6cwjj30lu09c771.jpg)

上图结果表明，尽管当前在体素方面的不确定性度量在数据集级别（即D列数据集中的所有体素）都得到了很好的校准，但它们在样本级别（S1，S2，S3列）上往往会失败。 原因是样本级别的校准误差（校准不足或过度校准）可以在数据集级别平均。基于所提出的基于校准的度量，在本文所研究的方法中没有找到最佳方法。 作者认为，通过评估总体素不确定性表现以提供样本水平估计的方法不够可靠，无法用作检测失败分割的机制。 因此，在医学图像分割中开发样本级别的不确定性估计很重要，可以解决High-Dimension-Low-Sample-Size（HDLSS）问题，以确保其在实践中的可靠性。



### 3.6 Exploiting Epistemic Uncertainty of Anatomy Segmentation for Anomaly Detection in Retinal OCT

https://arxiv.org/pdf/1905.12806.pdf

该工作发表在TMI上。这篇论文虽然没有针对不确定性方法作出优化，但其对不确定性方法的应用思路值得参考。论文提出的方案基于以下假设：认知不确定性与未知的解剖变异性（异常）存在相关性。因此在这项任务中应用认知不确定性估计来检测和分割视网膜OCT图像中的异常是合理的。如图12所示，异常面积和不确定性之间的高度相关性（ρ= 0.91）支持了这种说法。

![图13](https://tva1.sinaimg.cn/large/00831rSTly1gcw594by1pj30k20a2jt4.jpg)

方法上这篇论文使用的是MC dropout，以检索像素级认知不确定性估计。 最后，作者引入了一个简单的后处理步骤，即多数射线投射majority-ray-casting，将不确定度图转换为紧凑的异常分段。 该技术基于OCT中的异常紧凑且未分层的假设，从而弥合了层和异常形状之间的间隙。

![图14](https://tva1.sinaimg.cn/large/00831rSTly1gcw59o28lpj30ae0650t5.jpg)

