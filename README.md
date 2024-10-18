# 房租计算器
## 项目背景
该项目用于解决本人每月需要计算合租公寓中的各个房间的费用需求而诞生的，初代版本是前室友开发的java代码程序，后经再次迭代出借助excel简单布局的版本，到现在有UI的独立程序。

## 实现项目的用到的技术
- python3.10
- pyqt5
- pyinstaller
- 数据库:sqlite3

## 使用
### 使用方法
release版本中有打包的exe可执行程序压缩包，只需下载到本地目录并解压，双击custom_calculator.exe即运行。
### 源码重新打包
1.安装python3.10

2.安装requirements.txt中程序依赖的第三方库包

3.安装pyinstaller

4.打包源码生成程序
```shell
pyinstaller --onefile --windowed --icon=favicon.ico --distpath=./bin custom_calculator.py
```

### 客户端支持情况
- windows 

### 程序功能使用详情
程序中有两大块内容，分别是计算和历史2大块区域。其中计算块是根据每月抄表和费用收据单录入数据的区域并计算每人均摊的结果。历史块则是对过往的每月的计算结果进行的一个展示区域，里面含有每月人均公摊的费用折线图，寝室总费用折线图和每间房间每月的费用折线图。
按照实际情况依次输入对应文本框中的内容后检查一遍，确认输入无误后点击"计算按钮"会及时计算出结果。

注：除房间名对应的输入框可以输入非数字文本以外其他输入框请不要输入非数字相关的文本


### 程序界面预览
<image src="./img/计算页面.png" align="middle"><p align="middle">计算界面</p></image>

<image src="./img/历史数据页面.png"><p align="middle">历史数据页面</p></image>

