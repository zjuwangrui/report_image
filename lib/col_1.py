from typing import List, Dict
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import os

# Font settings
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def add_output(line: str = "") -> None:
    output_lines.append(line)
    print(line)
output_dir: str = input('please input the file name, such as output/')
output_dir = 'output/' + output_dir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
# Experimental data (SI units)
data: Dict[str, List[float]] = {
    'exp_id': [1, 2, 3, 4, 5],
    'v1 (m/s)': [ 0.3338, 0.372, 0.4193, 0.5130, 0.6325],  # cm/s -> m/s
    'v2 (m/s)': [ 0.3306, 0.3706, 0.4156, 0.5119, 0.6320],  # cm/s -> m/s
    'a (m/s^2)': [ -0.0006, -0.0011, -0.0013, -0.0022, -0.0031]  # cm/s^2 -> m/s^2
}

# Create DataFrame
df: pd.DataFrame = pd.DataFrame(data)

# Calculate average velocity (m/s)
df['v_avg (m/s)'] = (df['v1 (m/s)'] + df['v2 (m/s)']) / 2

# Mass m = 310.2g = 0.3102 kg
m: float = 0.3102  # kg

# Calculate force f = m * a (unit: Newton)
df['f (N)'] = m * df['a (m/s^2)']

# Output collection
output_lines: List[str] = []

# Show full data table
add_output("Full data table (SI units):")
add_output(df.round(4).to_string(index=False))
add_output("")

# Prepare plot data
v_avg = df['v_avg (m/s)'].values
f_values = df['f (N)'].values
df['k'] = df['f (N)'] / df['v_avg (m/s)']
list_k = df['k'].values
k_mean = sum(list_k) / len(list_k)
s:float=0
for k in list_k:
    s += (k - k_mean)**2
u = np.sqrt(s / (len(list_k) * (len(list_k) - 1)))
add_output(f"Drag coefficient k values for each experiment: {list_k}")
add_output(f"Mean drag coefficient k = {k_mean:.4f} N·s/m")
add_output(f"Uncertainty u = {u:.4f} N·s/m")

print(list_k)
# Linear fit f = -kv
slope, intercept, r_value, p_value, std_err = stats.linregress(v_avg, f_values)
add_output("Linear fit result:")
add_output(f"Fit equation: f = {slope:.6f} * v + {intercept:.6f}")
add_output(f"Since we expect f = -kv:")
add_output(f"k = {-slope:.4f} (drag coefficient in N·s/m)")
add_output(f"Correlation coefficient r = {r_value:.6f}")
add_output(f"R squared r^2 = {r_value**2:.6f}")
add_output(f"Standard error = {std_err:.6f}")
add_output("")

# Create output directory if not exists


# Create plot
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# Plot data points
ax.scatter(v_avg, f_values, color='red', s=100, alpha=0.7, label='Data points', zorder=5)

# Plot fit line
v_fit = np.linspace(float(min(v_avg)), float(max(v_avg)), 100)
f_fit = slope * v_fit + intercept
ax.plot(v_fit, f_fit, 'b--', linewidth=2, label=fr'Fit: $f = 0.0011v + {intercept:.4f}$', alpha=0.8)

# Annotate each data point
for i, (v, f_val) in enumerate(zip(v_avg, f_values)):
    ax.annotate(f'Exp {i+1}', (v, f_val), xytext=(5, 5), textcoords='offset points', fontsize=10, alpha=0.8)

# Set plot properties
ax.set_xlabel(r'Average velocity $\bar{v}$ (m/s)', fontsize=14)
ax.set_ylabel('Drag force f (N)', fontsize=14)
ax.set_title('Drag force f vs. average velocity $\\bar{v}$' + '\n' + f'Fit: $f = -kv$, $k = 0.0011$', fontsize=16)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=12)

# Set axis limits for better appearance
ax.set_xlim(0.2, 0.7)
y_min = float(min(f_values)) * 1.2
y_max = float(max(f_values)) * 1.2
ax.set_ylim(y_min, y_max)

# Add textbox for fit parameters
textstr = f'Drag coefficient k = 0.0011 N·s/m\nR squared r^2 = {r_value**2:.6f}'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)

img_path_png = os.path.join(output_dir, 'f_vs_velocity_plot.png')
img_path_pdf = os.path.join(output_dir, 'f_vs_velocity_plot.pdf')
img_path_svg = os.path.join(output_dir, 'f_vs_velocity_plot.svg')
plt.tight_layout()
plt.savefig(img_path_png, dpi=300, bbox_inches='tight')
plt.savefig(img_path_pdf, bbox_inches='tight')
plt.savefig(img_path_svg, bbox_inches='tight')
plt.close(fig)

add_output(f"Images saved as: {img_path_png}, {img_path_pdf}, and {img_path_svg}")
add_output("")

# Theoretical validation
add_output("Theoretical analysis:")
add_output("According to the model f = -kv:")
add_output(f"Drag coefficient k = {-slope:.4f} N·s/m")
add_output(f"This means that for every 1 m/s increase in velocity, the drag increases by {-slope:.6f} N")
add_output("")
add_output("Fit quality check:")
if r_value**2 > 0.9:
    add_output("excellent: (r^2 > 0.9)")
elif r_value**2 > 0.8:
    add_output("good: (r^2 > 0.8)")
else:
    add_output("fair: (r^2 < 0.8)")

# Save all output to file
result_txt_path: str = os.path.join(output_dir, 'result.txt')
with open(result_txt_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))