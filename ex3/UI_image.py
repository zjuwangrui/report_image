import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional

def simple_logger(message: str, level: str = "INFO") -> None:
    """一个简单的打印函数，用于调试。"""
    print(f"[{level}] {message}")

def load_ui_data(file_path: Path) -> Optional[pd.DataFrame]:
    """
    从指定的CSV文件加载电压和电流数据。

    Args:
        file_path (Path): 输入的CSV文件路径。

    Returns:
        Optional[pd.DataFrame]: 包含'U'和'I'列的DataFrame，如果文件不存在则返回None。
    """
    if not file_path.exists():
        simple_logger(f"输入文件不存在: {file_path}", "ERROR")
        return None
    
    simple_logger(f"正在从 {file_path} 读取数据...")
    df = pd.read_csv(file_path)
    
    # 标准化列名以确保兼容性
    df.columns = ['U', 'I']
    simple_logger(f"数据加载成功，共 {len(df)} 行。")
    return df

def find_stopping_potential(df: pd.DataFrame) -> float:
    """
    通过找到电流最接近零的电压值来估算截止电压。
    这里我们假设电流穿过零点，找到电流从正到负或最接近0的点。
    """
    # 寻找电流值最接近0的点的索引
    zero_current_index = (np.abs(df['I'])).idxmin()
    stopping_potential = df['U'][zero_current_index]
    return float(stopping_potential)

def plot_and_save_curves(
    data_long: pd.DataFrame, 
    data_short: pd.DataFrame, 
    output_path: Path
) -> None:
    """
    在同一张图上绘制两个波长的U-I曲线并保存。

    Args:
        data_long (pd.DataFrame): 长波长 (577nm) 的数据。
        data_short (pd.DataFrame): 短波长 (546nm) 的数据。
        output_path (Path): 图像输出路径。
    """
    simple_logger(f"正在绘制U-I曲线图...")
    plt.figure(figsize=(10, 7))

    # 绘制长波长曲线
    plt.plot(data_long['U'], data_long['I'], marker='o', linestyle='-', markersize=4, label='λ = 577nm (long wavelength)')
    
    # 绘制短波长曲线
    plt.plot(data_short['U'], data_short['I'], marker='x', linestyle='--', markersize=4, label='λ = 546nm (short wavelength)')

    plt.title('Photoelectric Effect V-A Characteristic Curve ($U_{AK}-i$)')
    plt.xlabel('Phototube Voltage $U_{AK}$ (V)')
    plt.ylabel('Photocurrent $I$ (x10⁻¹⁰ A)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.axhline(0, color='black', linewidth=0.5) # 添加y=0的参考线
    plt.axvline(0, color='black', linewidth=0.5) # 添加x=0的参考线

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存图像
    plt.savefig(output_path)
    simple_logger(f"图像已保存至: {output_path}")
    plt.close()

def save_report(
    output_path: Path,
    stop_potential_long: float,
    stop_potential_short: float
) -> None:
    """
    将分析结果和日志保存到文本文件。

    Args:
        output_path (Path): 报告文件的输出路径。
        stop_potential_long (float): 长波长对应的截止电压。
        stop_potential_short (float): 短波长对应的截止电压。
    """
    report_content = (
        "伏安特性曲线数据分析报告\n"
        "=================================\n"
        "本报告分析了两个不同波长下的光电效应伏安特性曲线。\n\n"
        "处理文件:\n"
        "  - 长波长 (577nm): long_lambda.csv\n"
        "  - 短波长 (546nm): short_lambda.csv\n\n"
        "分析结果:\n"
        f"  - 估算的长波长 (577nm) 截止电压: {stop_potential_long:.3f} V\n"
        f"  - 估算的短波长 (546nm) 截止电压: {stop_potential_short:.3f} V\n\n"
        "备注: 截止电压是通过寻找数据中光电流最接近零的点来估算的。\n"
        "=================================\n"
    )
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    simple_logger(f"分析报告已保存至: {output_path}")
    # 同时在终端打印报告
    print("\n--- 分析报告预览 ---\n" + report_content)

def main() -> None:
    """主函数，协调整个数据处理和绘图流程。"""
    try:
        date_str = input("请输入一个日期或标识符 (例如 '20251017')，用于命名输出文件: ")
        
        # 定义文件路径
        base_data_path = Path('d:/report_image/ex3/output/UI_image/data')
        long_lambda_path = base_data_path / 'long_lambda.csv'
        short_lambda_path = base_data_path / 'short_lambda.csv'
        
        # 加载数据
        df_long = load_ui_data(long_lambda_path)
        df_short = load_ui_data(short_lambda_path)
        
        if df_long is None or df_short is None:
            simple_logger("一个或多个数据文件加载失败，程序终止。", "ERROR")
            return
            
        # 分析数据：寻找截止电压
        stop_long = find_stopping_potential(df_long)
        stop_short = find_stopping_potential(df_short)
        
        # 定义输出路径
        image_output_path = Path(f'd:/report_image/ex3/output/UI_image/image/{date_str}+output.png')
        report_output_path = Path(f'd:/report_image/ex3/output/UI_image/data/{date_str}+output.txt')
        
        # 绘图并保存
        plot_and_save_curves(df_long, df_short, image_output_path)
        
        # 保存报告
        save_report(report_output_path, stop_long, stop_short)
        
        simple_logger("所有任务处理完成。")

    except Exception as e:
        simple_logger(f"程序发生意外错误: {e}", "CRITICAL")

if __name__ == "__main__":
    main()
