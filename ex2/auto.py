# 计算恢复系数、动量、能量等
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

def simple_logger(message: str, level: str = "INFO") -> None:
    """
    一个简单的打印函数，用于调试。
    A simple logger for debugging purposes.
    """
    print(f"[{level}] {message}")

def calculate_slope_for_row(row: pd.Series) -> float:
    """
    为单行数据计算峰值电压与峰值序号的线性回归斜率。

    Args:
        row (pd.Series): 包含一次实验数据的单行 DataFrame。

    Returns:
        float: 计算得到的斜率 (k 值)。
    """
    # 提取所有 'peakValue' 列
    peak_values: np.ndarray = row.filter(like='peakValue').values.astype(float)
    
    # 创建对应的峰值序号 (n = 1, 2, 3, ...)
    peak_numbers: np.ndarray = np.arange(1, len(peak_values) + 1)

    # 过滤掉无效的峰值数据 (NaN)
    valid_mask: np.ndarray = ~np.isnan(peak_values)
    if not np.any(valid_mask):
        simple_logger(f"Skipping row {row.get('exp_order', 'N/A')} due to all NaN values.", "WARNING")
        return np.nan

    peak_values = peak_values[valid_mask]
    peak_numbers = peak_numbers[valid_mask]

    # 执行线性回归
    slope, intercept, r_value, p_value, std_err = stats.linregress(peak_numbers, peak_values)
    
    simple_logger(f"Processed exp_order {row.get('exp_order', 'N/A')}: slope(k) = {slope:.4f}, R^2 = {r_value**2:.4f}")
    
    return slope

def process_franck_hertz_data(input_path: Path, output_path: Path) -> None:
    """
    处理弗兰克-赫兹实验数据，计算并保存 k 值。

    Args:
        input_path (Path): 输入 CSV 文件的路径。
        output_path (Path): 输出 CSV 文件的路径。
    """
    if not input_path.exists():
        simple_logger(f"Input file not found at: {input_path}", "ERROR")
        return

    simple_logger(f"Reading data from: {input_path}")
    df: pd.DataFrame = pd.read_csv(input_path)

    # 对每一行应用斜率计算函数
    simple_logger("Calculating slope (k) for each experiment...")
    df['k'] = df.apply(calculate_slope_for_row, axis=1)

    # 将 k 值格式化为两位小数
    df['k'] = df['k'].round(2)
    
    simple_logger(f"Saving processed data to: {output_path}")
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存到新的 CSV 文件
    df.to_csv(output_path, index=False)
    simple_logger("Processing complete.")

def main() -> None:
    """
    主函数，用于获取用户输入并启动处理流程。
    """
    # 从用户处获取文件名
    data_filename = input("请输入输出CSV文件的基本名称（例如，对于'u.csv'，请输入'u'）：")
    
    # 定义文件路径
    base_dir: Path = Path('d:/report_image/ex2/output/data/auto')
    input_file: Path = base_dir / "u.csv"
    output_file: Path = base_dir / f"{data_filename}_output.csv"
    
    process_franck_hertz_data(input_file, output_file)

if __name__ == "__main__":
    main()