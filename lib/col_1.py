import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  
plt.rcParams['axes.unicode_minus'] = False

# 实验数据
data: dict[str, list[float]] = {
    '实验编号': [1, 2, 3, 4, 5, 6],
    'v1 (cm/s)': [27.00, 33.38, 37.2, 41.93, 51.30, 63.25],
    'v2 (cm/s)': [26.31, 33.06, 37.06, 41.56, 51.19, 63.20],
    'a (cm/s²)': [-0.37, -0.22, -0.13, -0.31, -0.11, -0.06]
}

# 创建DataFrame
df = pd.DataFrame(data)

# 计算平均速度 v̄ = (v1 + v2) / 2
df['v̄ (cm/s)'] = (df['v1 (cm/s)'] + df['v2 (cm/s)']) / 2

# 物体质量 m = 310.2g
m = 310.2  # g

# 计算 f = m * a (单位: g·cm/s² = dyne)
df['f (dyne)'] = m * df['a (cm/s²)']

# 显示完整数据表
print("完整数据表:")
print(df.round(3))
print("\n")

# 准备绘图数据
v_avg = df['v̄ (cm/s)'].values
f_values = df['f (dyne)'].values

# 线性拟合 f = -kv (即 f = -k * v_avg)
# 使用最小二乘法拟合
slope, intercept, r_value, p_value, std_err = stats.linregress(v_avg, f_values)

print(f"线性拟合结果:")
print(f"拟合方程: f = {slope:.6f} * v + {intercept:.6f}")
print(f"由于我们期望 f = -kv 的形式，所以:")
print(f"k = {-slope:.6f} (阻力系数)")
print(f"相关系数 r = {r_value:.6f}")
print(f"相关系数平方 r² = {r_value**2:.6f}")
print(f"标准误差 = {std_err:.6f}")
print("\n")

# 创建图像
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# 绘制数据点
ax.scatter(v_avg, f_values, color='red', s=100, alpha=0.7, 
           label='实验数据点', zorder=5)

# 绘制拟合直线
v_fit = np.linspace(min(v_avg), max(v_avg), 100)
f_fit = slope * v_fit + intercept
ax.plot(v_fit, f_fit, 'b--', linewidth=2, 
        label=f'拟合直线: f = {slope:.4f}v + {intercept:.2f}', alpha=0.8)

# 为每个数据点添加标签
for i, (v, f_val) in enumerate(zip(v_avg, f_values)):
    ax.annotate(f'实验{i+1}', (v, f_val), 
                xytext=(5, 5), textcoords='offset points',
                fontsize=10, alpha=0.8)

# 设置图像属性
ax.set_xlabel('平均速度 v̄ (cm/s)', fontsize=14)
ax.set_ylabel('阻力 f (dyne)', fontsize=14)
ax.set_title('阻力 f 与平均速度 v̄ 的线性关系\n' + 
             f'拟合方程: f = -kv, k = {-slope:.6f}', fontsize=16)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=12)

# 设置坐标轴范围，使图像更美观
ax.set_xlim(20, 70)
y_min = min(f_values) * 1.2
y_max = max(f_values) * 1.2
ax.set_ylim(y_min, y_max)

# 添加文本框显示拟合参数
textstr = f'阻力系数 k = {-slope:.6f}\n相关系数 r² = {r_value**2:.6f}'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)

# 保存图像
plt.tight_layout()
plt.savefig('../output/f_vs_velocity_plot.png', dpi=300, bbox_inches='tight')
plt.savefig('../output/f_vs_velocity_plot.pdf', bbox_inches='tight')

plt.show()

# 计算理论验证
print("理论分析:")
print("根据 f = -kv 模型:")
print(f"阻力系数 k = {-slope:.6f} dyne·s/cm")
print(f"这意味着速度每增加 1 cm/s，阻力增加 {-slope:.6f} dyne")
print("\n验证拟合质量:")
if r_value**2 > 0.9:
    print("拟合质量: 优秀 (r² > 0.9)")
elif r_value**2 > 0.8:
    print("拟合质量: 良好 (r² > 0.8)")
else:
    print("拟合质量: 一般 (r² < 0.8)")