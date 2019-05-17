---
layout:     post
title:      "Ubuntu如何手动安装package"
subtitle:   "踩坑随记"
date:       2019-05-16 
author:     "Yean"
header-img: "img/post-bg-unix-linux.jpg"
catalog: true
tags:

    - 踩坑随记
---
# Ubuntu如何手动安装package

有时候在源出现问题的时候用apt-get install的方式不能安装想要的package，这种情况下还有另外一种手动配置的方法：

1.进入[Ubuntu package下载官网](https://packages.ubuntu.com/)

2.在自己的系统版本下，搜索想要的包。
![](https://upload-images.jianshu.io/upload_images/1083955-61a20d659a547ba2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
3.下载完成后会得到一个.deb文件
```
sudo dpkg -i 软件包名.deb
```
如果安装失败的话命令行中会提示缺少哪些依赖，按照同样的方式先手动安装好依赖的package就可以了（真的很麻烦……）
4.卸载.deb文件，可以使用Adept，或输入：
```
sudo apt-get remove 软件包名称
```