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
# 提示词
写一个脚本实现：
计算公式，单位，保留位数和有效数字
输入是csv文件，各列名称：
输出文件在eperi\output\data  experi\output\image
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试
输出文件名需要输入时间

# ex2
弗兰克赫兹实验

## auto.py
写一个脚本实现：拟合自动测量的数据得到图像求解k值。
本脚本需要拟合峰值peakvalue和峰值序号n来得到线性关系式，其斜率k值是所需要计算的数据。本脚本背景是进行了弗兰克赫兹实验，通过自动测量测量峰值电压，拟合峰值电压和峰值序号得到斜率，斜率即为氩原子的第一激发电势。
斜率需要保留两位小数。
输入数据csv文件，各列名称为:exp_order,peakValue1,peakValue2,peakValue3,peakValue4,peakValue5,peakValue6,peakValue7,k
输出文件在ex2\output\data\auto ，文件名为{data}+output.csv，data通过终端输入
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试