import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple
from scipy.stats import linregress

# Physical constants
E_CHARGE = 1.602176634e-19  # elementary charge, C

def simple_logger(msg: str, level: str = "INFO") -> None:
    print(f"[{level}] {msg}")


def wavelength_nm_to_frequency_hz(wl_nm: np.ndarray) -> np.ndarray:
    """把波长（nm）转换为频率（Hz）。

    ν = c / λ，λ 需从 nm 转为 m。
    """
    c = 299792458.0  # speed of light, m/s
    wl_m = wl_nm * 1e-9
    return c / wl_m


def read_and_prepare(input_csv: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """读取 CSV 并返回波长(nm)、频率(Hz)和截止电压数组（nm, Hz, V）。"""
    if not input_csv.exists():
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df = pd.read_csv(input_csv)
    # expect columns: 滤光片波长（nm）,截止电压（V）,反向电流（10e-13 A）
    # Normalize column names to English keys for safety
    cols = df.columns.tolist()
    # allow both Chinese and English names
    if len(cols) < 2:
        raise ValueError("Input CSV must contain at least two columns: wavelength and cutoff voltage")

    wl_col = cols[0]
    U_col = cols[1]

    wl_nm = df[wl_col].astype(float).to_numpy()
    Ua = df[U_col].astype(float).to_numpy()

    freq = wavelength_nm_to_frequency_hz(wl_nm)
    return wl_nm, freq, Ua


def fit_line_and_compute_h(freq: np.ndarray, Ua: np.ndarray) -> Tuple[float, float, float, float, float]:
    """对 Ua-ν 做线性拟合，返回 slope k (h/e), intercept, r_value and std_err, and h in SI units。

    Returns:
        k (float): slope in V·s (i.e., h/e)
        intercept (float): intercept in V
        h (float): Planck constant in J·s
        r_value (float): correlation coefficient
        std_err (float): standard error of the slope
    """
    # linear regression: Ua = k * freq + b
    slope, intercept, r_value, p_value, std_err = linregress(freq, Ua)
    k = slope
    h = k * E_CHARGE  # since k = h/e -> h = k * e
    return k, intercept, h, r_value, std_err


def plot_and_save(freq: np.ndarray, Ua: np.ndarray, k: float, intercept: float, date_str: str, out_dir: Path) -> Path:
    """绘图并保存图像，返回保存的文件路径。
    图像文件名为 {date}+output.png
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date_str}+output.png"

    # plot (keep frequency in Hz per requirement)
    plt.figure(figsize=(8, 6))
    plt.scatter(freq, Ua, label="data", color="blue")

    # regression line
    x_fit = np.linspace(freq.min(), freq.max(), 200)
    y_fit = k * x_fit + intercept
    k_display = k
    plt.plot(x_fit, y_fit, color="red", label=f"fit: Ua = {k_display} * ν + {intercept}")

    plt.xlabel(r"$\nu$ (Hz)")
    plt.ylabel(r"$U_a$ (V)")
    plt.title(r"$U_a - \nu$ (photoelectric effect)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.savefig(out_path)
    plt.close()
    return out_path


def save_report(date_str: str, out_dir: Path, k: float, intercept: float, h: float, r_value: float, std_err: float, wl_nm: np.ndarray, freq: np.ndarray, Ua: np.ndarray) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{date_str}+output.txt"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("Franck Photoelectric measurement report\n")
        f.write("====================================\n")
        f.write(f"Number of points: {len(freq)}\n")
        f.write(f"Slope k = h/e = {k} V·s\n")
        f.write(f"Intercept (y) = {intercept} V\n")
        # compute x-intercept (frequency where Ua = 0): ν0 = -intercept / k
        try:
            nu0 = -intercept / k
        except Exception:
            nu0 = float('nan')

        # convert to wavelength (nm) if positive
        if np.isfinite(nu0) and nu0 > 0:
            wl_at_nu0_nm = 299792458.0 / nu0 * 1e9
        else:
            wl_at_nu0_nm = float('nan')

        f.write(f"X-intercept (ν where Ua=0): {nu0} Hz\n")
        f.write(f"Corresponding wavelength: {wl_at_nu0_nm} nm\n")
        f.write(f"Calculated Planck constant h = {h} J·s\n")
        f.write(f"Correlation r = {r_value}, slope std_err = {std_err}\n")
        f.write("====================================\n")
        f.write("Data (wavelength_nm, frequency_Hz, Ua_V):\n")
        for wl, f_hz, u in zip(wl_nm, freq, Ua):
            f.write(f"{wl}, {f_hz}, {u}\n")
    return out_file


def main() -> None:
    try:
        date_str = input("请输入数据标识（用于输出文件名，例如 20251016）: ")
        input_csv = Path('d:/report_image/ex3/output/line/data/line.csv')
        wl_nm, freq, Ua = read_and_prepare(input_csv)
        k, intercept, h, r_value, std_err = fit_line_and_compute_h(freq, Ua)

        # prepare outputs
        k_rounded = k

        img_out_dir = Path('d:/report_image/ex3/output/line/image')
        data_out_dir = Path('d:/report_image/ex3/output/line/data')

        img_path = plot_and_save(freq, Ua, k, intercept, date_str, img_out_dir)
        report_path = save_report(date_str, data_out_dir, k_rounded, intercept, h, r_value, std_err, wl_nm, freq, Ua)

        simple_logger(f"Image saved to: {img_path}")
        simple_logger(f"Report saved to: {report_path}")
    except Exception as e:
        simple_logger(str(e), level="ERROR")


if __name__ == '__main__':
    main()
