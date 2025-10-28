物理实验很多计算画图，用这些代码干的，基本全是ai+微调。记录了提示词。


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
实验背景和目的
计算公式描述和绘制图像描述
输入文件的文件地址为：和各列名称：
输出的计算结果的单位，保留位数和有效数字，写入文件 ex\output\data 文件名：{date}+output.txt
输出图片的路径 ex\output\image 文件名{date}+output.png  date变量通过input函数输入
图片图例标题使用英文，显示拟合方程，参数保留几位小数和有效数字
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试
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

# 光电效应测定普朗克常量
王瑞+3240101517+光电效应测定普朗克常量+周三三四五节

## line.py
绘制$U_a-\nu$图像。得出斜率k= $\frac{h}{e}$ ，求出普朗克常数h=ke。
背景：我在利用光电效应测量普朗克常数。根据U和频率图像斜率计算普朗克常数。
写一个脚本实现：绘制$U_a-\nu$图像。得出斜率k= $\frac{h}{e}$ ，求出普朗克常数h=ke。
本脚本需要拟合截止电压和频率$\nu$来得到线性关系式，其斜率k值是所需要计算的数据。
斜率需要保留两位小数。
输入数据csv文件，文件地址：各列名称为:滤光片波长（nm）,截止电压（V）,反向电流（10e-13 A）
输出拟合图像在ex3\output\line\image ，文件名为{date}+output.png，date通过input()函数输入
数据计算结果和关键脚本进行过程、日志输出在ex3\output\line\data 文件名{date}+output.txt，date通过input()函数输入
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试

## UI_image.py
绘制$U_{AK}-i$图像。
背景：我在利用光电效应测量伏安特性曲线
写一个脚本实现：绘制绘制$U_{AK}-i$图像。
输入数据csv文件，文件地址：ex3\output\UI_image\data\long_lambda.csv  ex3\output\UI_image\data\short_lambda.csv
各列名称为:光电管电压U(V),光电流I(10e-10 A)
输出拟合图像在ex3\output\UI_image\image ，文件名为{date}+output.png，date通过input()函数
把两个波长对应的图像放在一个图里面，使用不同颜色标注，加上英文图例标题。短波长设置为546nm，长波长设置为577nm，数据分别对应ex3\output\UI_image\data\short_lambda.csv      ex3\output\UI_image\data\long_lambda.csv 
输入数据计算结果和关键脚本进行过程、日志输出在ex3\output\UI_image\data 文件名{date}+output.txt，date通过input()函数输入
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试

## LI_image.py

写一个脚本实现：根据数据绘制饱和光电流$I_s$和光源距离L的负二分之一次方的关系，来验证饱和光电流和光强的正比关系。
输入数据csv文件，文件地址：ex3\output\LI_image\input.csv
各列名称为:L(cm),I(e-10 A)
输出拟合图像在ex3\output\LI_image\ ，文件名为{date}+output.png，date通过input()函数
图片图例使用英文，显示拟合方程和R^2
要求计算拟合图像的拟合效果R^2 (保留两位小数)
输入数据的计算结果R^2和关键脚本进行过程、日志输出在ex3\output\LI_image 文件名{date}+output.txt，date通过input()函数输入
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试

## phiI_iamge.py
写一个脚本实现：根据数据绘制饱和光电流$I_s$和光阑孔径$\phi$的二分之一次方的关系，来验证饱和光电流和光强的正比关系。
输入数据csv文件，文件地址：ex3\output\phiI_image\input.csv
各列名称为:phi(mm),I(e-10 A)
输出拟合图像在ex3\output\phiI_image\ ，文件名为{date}+output.png，date通过input()函数
图片图例使用英文，显示拟合方程和R^2
要求计算拟合图像的拟合效果R^2 (保留两位小数)
输入数据的计算结果R^2和关键脚本进行过程、日志输出在ex3\output\phiI_image 文件名{date}+output.txt，date通过input()函数输入
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试

# ex4 
王瑞+3240101517+用霍尔法测直流圆线圈与亥姆霍兹线圈磁场+周三3，4，5节

## single.py
脚本需要实现绘制单个载流原线圈的轴线上B-x图像。
实验过程中将单个载流圆线圈放置在测量位置，调节电流并记录不同位置的磁感应强度。
电流值为0.4A，匝数400，线圈半径10cm。实验原始数据(输入的input.csv)中S表示测量位置的读数，线圈位于s=15cm处。
x表示绘制磁场分布的图像的x坐标值，也就是该点的s-15。B的计算公式是B正和B负绝对值的平均值。
理论值应采用单个圆线圈轴线上磁感应强度的标准表达式（多匝乘以 N）：
B(x) = $\displaystyle \frac{\mu_0 N I R^2}{2\,(x^2+R^2)^{3/2}}$。
相对误差是 B的测量值(B_avg)和理论值之差 与B的理论值(B_ideal) 的比。
输入文件的文件地址为：ex4\output\single\data\input.csv 和各列名称：order,S(cm),x(cm),B_+(mT),B_-(mT),B_avg(mT),B_ideal(mT),相对误差
输出的计算结果，写入文件 ex4\output\single\data\output.csv 文件名：{date}+output.csv，将输入文件中没有计算的各列计算并写入文件。
简单输出脚本运行报告，记录关键进程。文件地址:ex4\output\single\data\output.txt
输出图片的路径 ex4\output\single\image 文件名{date}+output.png  date变量通过input函数输入
图片图例标题使用英文，同时显示理论图像和测量的B-x图像。
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试
## double.py
脚本需要实现绘制亥姆霍兹线圈的轴线上B-x图像。
实验过程中将亥姆霍兹线圈放置在测量位置，调节电流并记录不同位置的磁感应强度。
电流值为0.4A，匝数400，线圈半径10cm。实验原始数据(输入的input.csv)中S表示测量位置的读数，两个线圈的中心位于s=15cm处，线圈1位于s=10cm，线圈二位于s=20cm处。
x表示绘制磁场分布的图像的x坐标值，也就是该点的s-15。B_avg的计算公式是B正和B负绝对值的平均值。
输入文件的文件地址为：ex4\output\double\data\input.csv 和各列名称：order,S(cm),x(cm),B_+(mT),B_-(mT),B_avg(mT)
输出的计算结果，写入文件 ex4\output\double\data\output.csv 文件名：{date}+output.csv，将输入文件中没有计算的列B_avg(mT)计算并写入文件。
同时计算亥姆霍兹线圈在原点x=0处的理论磁感应强度值，计算相对误差。
简单输出脚本运行报告，记录关键进程和B_0计算值、相对误差。文件地址:ex4\output\single\data\output.txt
拟合B-x图像，并输出，图像的路径 ex4\output\double\image 文件名{date}+output.png  date变量通过input函数输入
图片图例标题使用英文
注意代码风格函数化，方便修改计算参数；增加严格的类型批注；增加简单的打印系统方便调试
# ex5
王瑞+3240101517+密里根油滴实验+周三三四五节 10.29