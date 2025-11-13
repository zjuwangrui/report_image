
import pandas as pd
import numpy as np
from pathlib import Path

def generate_raw_data_template() -> None:
    """
    生成一个用于手动记录实验数据的CSV模板文件。

    文件包含两列：'U' 和 'I'。
    'U' 列预先填充了从 0.0 到 100.0，步长为 0.5 的电压值。
    'I' 列为空，等待用户填充。
    """
    # 从用户处获取文件名
    file_prefix = input("请输入原始数据文件的名称前缀（例如，输入 'my_experiment' 将生成 'my_experiment_raw.csv'）：")

    # 定义输出目录和文件名
    output_dir = Path('d:/report_image/ex2/output/data/non_auto')
    output_file = output_dir / f"{file_prefix}_raw.csv"

    # 生成 'U' 列的数据
    u_values = np.arange(0.0, 100.5, 0.5)

    # 创建 DataFrame
    df = pd.DataFrame({
        'U': u_values,
        'I': np.nan  # 使用 NaN (Not a Number) 作为 'I' 列的占位符
    })

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存到 CSV 文件
    df.to_csv(output_file, index=False, float_format='%.1f')

    print(f"成功创建模板文件：{output_file}")
    print(f"文件中包含 {len(u_values)} 行数据。")

if __name__ == "__main__":
    generate_raw_data_template()
