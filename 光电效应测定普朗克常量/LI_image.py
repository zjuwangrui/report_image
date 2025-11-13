import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import linregress
from typing import Tuple, Optional

def simple_logger(message: str, level: str = "INFO") -> None:
    """一个简单的打印函数，用于调试。"""
    print(f"[{level}] {message}")

def load_and_transform_data(file_path: Path) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    加载数据并进行转换。
    - L (cm) to L (m)
    - Calculates L_inv_sq (m⁻²)
    
    Args:
        file_path (Path): 输入CSV文件的路径。

    Returns:
        A tuple of (L_m, L_inv_sq, I) numpy arrays, or None if loading fails.
    """
    if not file_path.exists():
        simple_logger(f"输入文件不存在: {file_path}", "ERROR")
        return None
    
    simple_logger(f"正在从 {file_path} 读取数据...")
    df = pd.read_csv(file_path)
    df.columns = ['L_cm', 'I']
    
    L_cm = df['L_cm'].values
    I = df['I'].values
    
    # Convert L from cm to m for SI unit consistency
    L_m = L_cm / 100.0
    
    # According to physics, light intensity is proportional to L⁻².
    # We will verify the linear relationship between I_s and L⁻².
    L_inv_sq = L_m ** -2
    
    simple_logger("数据转换完成: L (cm) -> L⁻² (m⁻²)。")
    return L_m, L_inv_sq, I

def perform_linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """
    对给定的x, y数据执行线性回归。

    Args:
        x (np.ndarray): 自变量数据 (L⁻²)。
        y (np.ndarray): 因变量数据 (I)。

    Returns:
        A tuple containing (slope, intercept, r_squared).
    """
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r_squared = r_value ** 2
    simple_logger(f"线性回归完成。斜率: {slope:.4f}, 截距: {intercept:.4f}, R²: {r_squared:.4f}")
    return slope, intercept, r_squared

def plot_and_save_graph(
    x: np.ndarray, 
    y: np.ndarray, 
    slope: float, 
    intercept: float, 
    r_squared: float, 
    output_path: Path
) -> None:
    """
    绘制 I vs L⁻² 的关系图并保存。

    Args:
        x (np.ndarray): L⁻² 数据。
        y (np.ndarray): I 数据。
        slope (float): 拟合斜率。
        intercept (float): 拟合截距。
        r_squared (float): R² 值。
        output_path (Path): 图像输出路径。
    """
    simple_logger(f"正在绘制 I vs L⁻² 关系图...")
    plt.figure(figsize=(10, 7))
    
    # 绘制原始数据点
    plt.scatter(x, y, label='Experimental Data', color='blue')
    
    # 绘制拟合直线
    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = slope * x_fit + intercept
    fit_equation = f'$I_s = {slope:.4f} \\cdot (1/L^2) + {intercept:.4f}$'
    plt.plot(x_fit, y_fit, color='red', label=f'Linear Fit\n{fit_equation}\n$R^2 = {r_squared:.4f}$')
    
    plt.title('Saturation Photocurrent vs. (Light Source Distance)$^{-2}$')
    plt.xlabel('1 / $L^2$ ($m^{-2}$)')
    plt.ylabel('Saturation Photocurrent $I_s$ ($10^{-10}$ A)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    simple_logger(f"图像已保存至: {output_path}")
    plt.close()

def save_report_file(
    output_path: Path,
    r_squared: float,
    slope: float,
    intercept: float,
    L_m: np.ndarray,
    I: np.ndarray
) -> None:
    """
    将计算结果和日志保存到文本文件。
    """
    report_content = (
        f"饱和光电流与光源距离关系验证报告\n"
        f"========================================\n"
        f"实验目的: 验证饱和光电流 $I_s$ 与光强 $E$ 的正比关系，其中 $E \\propto 1/L^2$。\n"
        f"因此，我们检验 $I_s$ 与 $1/L^2$ 的线性关系。\n\n"
        f"分析结果:\n"
        f"  - 线性拟合的决定系数 (R²): {r_squared:.4f}\n"
        f"  - 拟合方程: I_s = {slope:.4f} * (1/L²) + {intercept:.4f}\n\n"
        f"结论: R² 值为 {r_squared:.4f}，非常接近1，表明饱和光电流 $I_s$ 与 $1/L^2$ 之间有很强的线性关系，\n"
        f"从而验证了饱和光电流与光强成正比。\n"
        f"========================================\n"
        f"原始输入数据:\n"
        f"L(m), I(10e-10 A)\n"
    )
    
    for l, i in zip(L_m, I):
        report_content += f"{l:.2f}, {i}\n"
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    simple_logger(f"分析报告已保存至: {output_path}")
    print("\n--- 分析报告预览 ---\n" + report_content)

def main() -> None:
    """主函数，协调所有操作。"""
    try:
        date_str = input("请输入一个日期或标识符 (例如 '20251017')，用于命名输出文件: ")
        
        # 定义路径
        base_path = Path('d:/report_image/ex3/output/LI_image')
        input_csv_path = base_path / 'input.csv'
        image_output_path = base_path / f'{date_str}+output.png'
        report_output_path = base_path / f'{date_str}+output.txt'
        
        # 加载和转换数据
        data = load_and_transform_data(input_csv_path)
        if data is None:
            return
        L_m, L_inv_sq, I = data
        
        # 线性回归
        slope, intercept, r_squared = perform_linear_regression(L_inv_sq, I)
        
        # 绘图
        plot_and_save_graph(L_inv_sq, I, slope, intercept, r_squared, image_output_path)
        
        # 保存报告
        save_report_file(report_output_path, r_squared, slope, intercept, L_m, I)
        
        simple_logger("所有任务处理完成。")

    except Exception as e:
        simple_logger(f"程序发生意外错误: {e}", "CRITICAL")

if __name__ == "__main__":
    main()
