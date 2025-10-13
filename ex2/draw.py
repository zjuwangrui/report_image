import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, List

def simple_logger(message: str, level: str = "INFO") -> None:
    """一个简单的打印函数，用于调试。"""
    print(f"[{level}] {message}")

def load_data(file_path: Path) -> pd.DataFrame | None:
    """从CSV文件加载数据并进行预处理。"""
    if not file_path.exists():
        simple_logger(f"输入文件不存在: {file_path}", "ERROR")
        return None
    
    simple_logger(f"正在从 {file_path} 读取数据...")
    df = pd.read_csv(file_path)
    
    # 标准化列名
    df.columns = ['U', 'I']
    simple_logger(f"数据加载成功，共 {len(df)} 行。")
    return df

def analyze_and_plot(df: pd.DataFrame, output_path_prefix: str) -> Tuple[List[float], float, float] | None:
    """
    分析数据、绘制图像、寻找峰值并计算激发电势。

    Args:
        df (pd.DataFrame): 包含 U 和 I 列的数据。
        output_path_prefix (str): 输出文件（图像和文本）的前缀。

    Returns:
        A tuple containing (peak_voltages, mean_potential, uncertainty) or None if fails.
    """
    U = df['U'].values
    I = df['I'].values

    # 1. 数据平滑：使用三次样条插值
    simple_logger("使用三次样条插值平滑数据...")
    cs = CubicSpline(U, I)
    U_smooth = np.linspace(U.min(), U.max(), 2000)
    I_smooth = cs(U_smooth)

    # 2. 寻找峰值
    # prominence: 峰值的突出程度, height: 峰值的最小高度
    simple_logger("正在寻找电流峰值...")
    peaks_indices, _ = find_peaks(I_smooth, prominence=50, height=560)
    peak_voltages = U_smooth[peaks_indices]
    peak_currents = I_smooth[peaks_indices]
    
    if len(peak_voltages) < 2:
        simple_logger("找到的峰值少于2个，无法进行计算。", "ERROR")
        return None
        
    simple_logger(f"找到 {len(peak_voltages)} 个峰值，电压分别为: {[f'{v:.2f}' for v in peak_voltages]}")

    # 3. 绘制图像并设置交互功能
    simple_logger("正在绘制可交互的 I-U 曲线图...")
    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(U_smooth, I_smooth, label='Smoothed I-U Curve', color='blue', zorder=1)
    ax.scatter(U, I, color='gray', s=15, label='Raw Data Points', zorder=2)
    ax.scatter(peak_voltages, peak_currents, color='red', s=50, zorder=3, label=f'Detected Peaks ({len(peak_voltages)})')

    # 在图上标记峰值电压
    for i, (v, c) in enumerate(zip(peak_voltages, peak_currents)):
        ax.text(v, c + 15, f'{v:.2f}V', ha='center', va='bottom', fontsize=9)

    ax.set_title('Franck-Hertz Experiment: $I_A - U_{G2K}$ Curve')
    ax.set_xlabel('$U_{G2K}$ (V)')
    ax.set_ylabel('$I_A$ (nA)')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    # --- 添加交互式坐标显示功能 ---
    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(event):
        if event.inaxes == ax:
            x, y = event.xdata, event.ydata
            annot.xy = (x, y)
            text = f"U={x:.2f}, I={y:.2f}"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.4)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", update_annot)
    # --------------------------------

    # 保存图像
    img_output_path = Path(f"{output_path_prefix}_plot.png")
    img_output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(img_output_path)
    simple_logger(f"图像已保存至: {img_output_path}")
    
    # 显示交互式窗口
    plt.show()
    plt.close()

    # 4. 计算第一激发电势 (逐差法)
    simple_logger("使用逐差法计算第一激发电势...")
    diffs = np.diff(peak_voltages)
    mean_potential = np.mean(diffs)
    
    # 计算A类不确定度 (标准差)
    if len(diffs) > 1:
        uncertainty = np.std(diffs, ddof=1) / np.sqrt(len(diffs))
    else:
        uncertainty = np.nan # 如果只有一个差值，无法计算标准差

    simple_logger(f"计算完成: 平均激发电势 = {mean_potential:.2f} V, 不确定度 = {uncertainty:.2f} V")
    
    return peak_voltages.tolist(), mean_potential, uncertainty

def save_results(output_path: Path, peak_voltages: List[float], mean_potential: float, uncertainty: float) -> None:
    """将结果保存到文本文件并打印到终端。"""
    
    output_content = (
        "弗兰克-赫兹实验数据分析报告\n"
        "=================================\n"
        f"找到的峰值数量: {len(peak_voltages)}\n"
        f"各峰值电压 (V): {[f'{v:.2f}' for v in peak_voltages]}\n"
        "---------------------------------\n"
        "逐差法计算结果:\n"
        f"  - 平均第一激发电势: {mean_potential:.2f} V\n"
        f"  - A类不确定度: {uncertainty:.2f} V\n"
        "=================================\n"
        f"最终结果: U = ({mean_potential:.2f} ± {uncertainty:.2f}) V\n"
    )
    
    # 打印到终端
    print("\n" + "="*40)
    print("分析结果")
    print("="*40)
    print(output_content)
    
    # 保存到文件
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    simple_logger(f"分析报告已保存至: {output_path}")


def main() -> None:
    """主函数，协调整个流程。"""
    file_basename = input("请输入要分析的CSV文件的基本名称（例如, 对于 'raw.csv'，请输入 'raw'）: ")
    
    input_path = Path(f'd:/report_image/ex2/output/data/non_auto/raw.csv')
    output_prefix = f'd:/report_image/ex2/output/image/{file_basename}'
    
    df = load_data(input_path)
    if df is None:
        return

    analysis_result = analyze_and_plot(df, output_prefix)
    
    if analysis_result:
        peak_voltages, mean_potential, uncertainty = analysis_result
        record_output_path = Path(f"{output_prefix}_record.txt")
        save_results(record_output_path, peak_voltages, mean_potential, uncertainty)

if __name__ == "__main__":
    main()
