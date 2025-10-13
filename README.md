# 创建虚拟环境
python -m venv myenv
然后右下角选择环境
# 已安装的库
numpy 
scipy
pandas
matplotlib
# 绘制图像
注意单位 $cm/s^2$
字体标签使用英文
保存格式为png svg ，保存名称加上时间。
# 提示词
写一个脚本实现：
计算公式，单位，保留位数和有效数字
输入是csv文件，文件地址为：和各列名称：
输出文件在eperi\output\data  experi\output\image
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试
输出文件名需要输入时间

# ex2
弗兰克赫兹实验

## auto.py
功能：拟合自动测量的数据得到图像求解k值。
写一个脚本实现：拟合自动测量的数据得到图像求解k值。
本脚本需要拟合峰值peakvalue和峰值序号n来得到线性关系式，其斜率k值是所需要计算的数据。本脚本背景是进行了弗兰克赫兹实验，通过自动测量测量峰值电压，拟合峰值电压和峰值序号得到斜率，斜率即为氩原子的第一激发电势。
斜率需要保留两位小数。
输入数据csv文件，各列名称为:exp_order,peakValue1,peakValue2,peakValue3,peakValue4,peakValue5,peakValue6,peakValue7,k
输出文件在ex2\output\data\auto ，文件名为{data}+output.csv，data通过input()函数输入
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试
## image.py
功能：实现绘制手动测量数据的图像，得到峰值，利用峰值逐差法计算氩原子第一激发电势，以及不确定度。
写一个脚本实现：拟合手动测量的数据得到$I_A-U_{G2K}$图像，使用平滑曲线连接输入数据给出的离散点。拟合图像后记录峰值，输出到ex2\output\image ,文件名record.txt 和终端。
本脚本背景是进行了弗兰克赫兹实验，通过手动测量数据拟合$I_A-U_{G2K}$图像，记录图像的峰值电压，利用峰值电压和逐差法计算氩原子的第一激发电势。
输入数据csv文件，各列名称为:U(V),I(nA)
输出文件在ex2\output\image ，文件名为{data}+output.csv，data通过input()函数输入
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试
## generate_raw_data.py
生成初始手动测量数据。
