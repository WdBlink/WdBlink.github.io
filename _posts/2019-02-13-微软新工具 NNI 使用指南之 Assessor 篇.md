---
layout:     post
title:      "微软新工具 NNI 使用指南之 Assessor 篇"
subtitle:   "微软NNI MiniTask第三篇"
date:       2019-02-13 
author:     "Yean"
header-img: "img/post-bg-unix-linux.jpg"
catalog: true
tags:
    - 机器学习
    - AI
---
# 微软新工具 NNI 使用指南之 Assessor 篇
![](https://upload-images.jianshu.io/upload_images/1083955-7c9ad7544cf87c62.PNG?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
## 什么是 Assessor
在说 NNI 中的 Assessor 算法前，首先需要了解下什么是 Assessor。
通常来说，“Assessor” 不是论文中的通常叫法，一般而言 Assessor 在论文中被叫做
 “Early Stop”。顾名思义，该模块的作用在于判断当前尝试的超参是否有“前途”，
如果当前设置被判断为即便多次迭代后仍无法获得更好的结果时便提前终止迭代，以节约
宝贵的计算资源。

**注：本文中出现的所有引用均可以在该[仓库](https://github.com/VDeamoV/autoML_papers) 内找到**
## NNI 已有 Assessor 算法介绍
### Median Stop
Median Stop 出现在 Goolge 的自动调参工具的论文 [1] 中，该方法在论文中的描述为，
在当前尝试的超参训练的过程中，如果出现最新 step 的结果比之前所有的 step 的结果的均值要低的情况，则终止该训练。
这种方法的优点为**不需要拟合曲线，运算简单**，但是缺点也很明显，即利用之前步骤的信息较少，判断可能不是很准确。

> 优点：算法简单，算法运算速度快<br>
> 缺点：对之前已有的信息利用不充分，判断结果相对较不准确，如曲线震荡幅度比较大但是最终结果很好的情况。

### Curvefitting
Curvefitting 是一篇在顶会 IJCAI 的工作 [2]，相比之前的 Median Stop 算法，
该算法同贝叶斯优化算法类似，使用之前的 n 个样本点来拟合学习曲线。
而与传统的使用高斯处理来拟合学习曲线不同的是，该算法引入了马尔可夫蒙特卡洛 (Markov Chain Monte Carlo)，
这使得算法能够更加充分利用之前的样本点中的信息，以更好的预测当前训练的最终结果。
该算法的停止标准为，**当预计当前算法的最优结果低于之前的最优结果**，则决定提前停止当前尝试。

> 优点：能够更好的学习到前几次的尝试样本，能更准确的判断是否该提前停止<br>
> 缺点：该算法需要冷启动，需要设置较多超参

论文中的实验将 Curvefitting 同 SMAC 结合，如图 2.1 所示，可以看出效果还是非常明显的。

![图 2.1 Curvefitting](https://ws4.sinaimg.cn/large/006tNc79ly1g02mxvl23pj31uo0oin1x.jpg)
## 结语
当前已有的 Assessor 主要出自 Google 的 Google Vizier[3]，经过对论文的调查有效的
Early Stop 算法均以实现。 当前 NNI 内的 Assessor 的定义有些类似 Early Stop，而这个单独作为一类的话似乎有点太奢侈。
在 Tuner 的调研中，发现有一些算法，如 Hyperband[4] 是可以和其他 Tuner 进行融合而具有更好的结果的。
如果将 Assessor 定义为可以和基础算法进行融合的算法的话，似乎可以让 Tuner 的配置更具灵活性。

但是不管怎么说，Assessor 的使用简单明确，对新手非常友好是一个很好的组件。NNI
也是一个简单易用的工具，希望未来 NNI 越来越完善，最终成为炼丹师们的好帮手。
## 参考论文
- [1] Golovin D, Solnik B, Moitra S, et al. Google vizier: A service for black-box optimization[C]//Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. ACM, 2017: 1487-1495.
- [2] Domhan T, Springenberg J T, Hutter F. Speeding Up Automatic Hyperparameter Optimization of Deep Neural Networks by Extrapolation of Learning Curves[C]//IJCAI. 2015, 15: 3460-8.
- [3] Golovin D, Solnik B, Moitra S, et al. Google vizier: A service for black-box optimization[C]//Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. ACM, 2017: 1487-1495.
- [4] Li L, Jamieson K, DeSalvo G, et al. Hyperband: A novel bandit-based approach to hyperparameter optimization[J]. arXiv preprint arXiv:1603.06560, 2018: 1-48.
