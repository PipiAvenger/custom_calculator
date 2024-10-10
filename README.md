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


