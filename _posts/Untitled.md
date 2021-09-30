论文：

FGSD: A DATASET FOR FINE-GRAINED SHIP DETECTION IN HIGH RESOLUTION SATELLITE IMAGES

A High Resolution Optical Satellite Image Dataset for Ship Recognition and Some New Baselines

### FGSD

FGSD数据集一共2612张图，5634个标记样本。分辨率0.12m ～ 1.93m，图片大小为930 × 930。分成4个大类：warship，carrier，submarine，civil ship。其中包括共43个小类。

![image-20210825162618408](https://tva1.sinaimg.cn/large/008i3skNly1gtt44figshj60pj0fvmz102.jpg)

![image-20210825161533053](https://tva1.sinaimg.cn/large/008i3skNly1gtt3t86367j60ki0fpgm802.jpg)

如上所述，某些船只略有不同，而其他船只差别很多。 这些类别略有差异可以被视为细粒度的子集。 因此，我们进一步标记了那些细粒度的类别，包括航空母舰，战舰，两栖突击船和供应船。 图5示出了集子集飞行器和战舰的一些示例。

![image-20210825161427882](https://tva1.sinaimg.cn/large/008i3skNly1gtt3s5ld2nj60lo0fk0uq02.jpg)

使用R2CNN和Faster-RCNN作为baseline，得到以下结果：

![image-20210825161930769](https://tva1.sinaimg.cn/large/008i3skNly1gtt3xcskcoj617w0f6wi802.jpg)

BLr平均mAP0.65，BLh平均0.7



### HRSC2016

数据集包含1061张图3786个样本。分辨率2-m and 0.4-m. 图像大小区间 300×300 ～1500×900 大部分大于1000×600.

HRSC2016数据集上分类4个大类的准确率：

![image-20210825163202852](https://tva1.sinaimg.cn/large/008i3skNly1gtt4ae5lotj60oy04yt9602.jpg)

43个子类准确率：

![image-20210825170139704](https://tva1.sinaimg.cn/large/008i3skNly1gtt557mdhbj61fq09e0vf02.jpg)