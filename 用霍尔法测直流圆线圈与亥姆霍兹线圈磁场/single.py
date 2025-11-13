import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pandas import DataFrame

from pathlib import Path
from typing import Dict, Any

# --- Constants and Parameters ---
# Permeability of free space (μ₀) in T·m/A
MU_0 = 4 * np.pi * 1e-7
# Experiment parameters
PARAMS: dict[str, float] = {
    "current_I": 0.4,  # Amperes
    "turns_N": 400,
    "radius_R_cm": 10.0, # Centimeters
    "coil_center_S_cm": 15.0 # Centimeters
}

def simple_logger(message: str, level: str = "INFO") -> str:
    """A simple logger that returns a formatted string and prints it."""
    log_message = f"[{level}] {message}"
    print(log_message)
    return log_message + "\n"

def calculate_derived_values(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates x, B_avg, B_ideal, and relative error.
    
    Args:
        df (pd.DataFrame): Input dataframe with S(cm), B_+(mT), B_-(mT).
        params (Dict[str, Any]): Dictionary of physical parameters.

    Returns:
        pd.DataFrame: Dataframe with calculated columns.
    """
    # --- Unit Conversions ---
    radius_R_m = params["radius_R_cm"] / 100.0
    coil_center_S_cm = params["coil_center_S_cm"]
    
    # --- Calculations ---
    # 1. Calculate x in cm and m, and round to integer
    df['x(cm)'] = (df['S(cm)'] - coil_center_S_cm).round(0).astype(int)
    x_m = df['x(cm)'] / 100.0
    
    # 2. Calculate average measured B in mT and round
    df['B_avg(mT)'] = ((df['B_+(mT)'].abs() + df['B_-(mT)'].abs()) / 2).round(3)
    
    # 3. Calculate theoretical B in Tesla, then convert to mT and round
    # B(x) = (μ₀ * N * I * R²) / (2 * (x² + R²)^(3/2))
    numerator = MU_0 * params["turns_N"] * params["current_I"] * (radius_R_m ** 2)
    denominator = 2 * ((x_m ** 2 + radius_R_m ** 2) ** 1.5)
    b_ideal_tesla = numerator / denominator
    df['B_ideal(mT)'] = (b_ideal_tesla * 1000).round(3) # Convert T to mT
    
    # 4. Calculate relative error and format as percentage string
    # Using abs() for error magnitude
    relative_error = ((df['B_avg(mT)'] - df['B_ideal(mT)']).abs() / df['B_ideal(mT)']) * 100
    df['相对误差'] = relative_error.apply(lambda x: f'{x:.1f}%')
    df['B_+(mT)'] = df['B_+(mT)'].round(3)
    df['B_-(mT)'] = df['B_-(mT)'].round(3)
    df['B_avg(mT)'] = df['B_avg(mT)'].round(3)
    df['B_ideal(mT)'] = df['B_ideal(mT)'].round(3)
    return df

# Update type hints for clarity

def plot_b_x_graph(df: DataFrame, params: Dict[str, Any], output_path: Path) -> None:
    """
    Plots both the fitted curve from measured data and the theoretical B-x graph.

    Args:
        df (DataFrame): The processed data.
        params (Dict[str, Any]): Physical parameters for the theoretical curve.
        output_path (Path): Path to save the image.
    """
    x_cm = df['x(cm)']
    b_avg_mT = df['B_avg(mT)']

    fig: Figure = plt.figure(figsize=(12, 8))
    ax: Axes = fig.add_subplot(1, 1, 1)

    # --- Fitted Curve from Measured Data ---
    # Fit a polynomial to the measured data to create a smooth curve
    poly_coeffs = np.polyfit(x_cm, b_avg_mT, 6)
    poly_func = np.poly1d(poly_coeffs)
    
    # Generate smooth x values for both curves
    x_smooth_cm = np.linspace(x_cm.min(), x_cm.max(), 300)
    b_fit_smooth_mT = poly_func(x_smooth_cm)

    # Plot the fitted curve (from measured data)
    ax.plot(x_smooth_cm, b_fit_smooth_mT, label='Fitted Curve (from Measured Data)', color='red')

    # --- Theoretical Curve ---
    x_smooth_m = x_smooth_cm / 100.0
    radius_R_m = params["radius_R_cm"] / 100.0
    
    numerator = MU_0 * params["turns_N"] * params["current_I"] * (radius_R_m ** 2)
    denominator = 2 * ((x_smooth_m ** 2 + radius_R_m ** 2) ** 1.5)
    b_ideal_smooth_mT = (numerator / denominator) * 1000
    
    # Plot the theoretical curve
    ax.plot(x_smooth_cm, b_ideal_smooth_mT, label='Theoretical Curve', color='green', linestyle='--')
    
    # Also plot the original measured data points for reference
    ax.scatter(x_cm, b_avg_mT, label='Measured Data Points', color='blue', zorder=5, alpha=0.6)

    # Formatting
    ax.set_title('Fitted vs. Theoretical Magnetic Field on the Axis of a Single Coil')
    ax.set_xlabel('Position x (cm)')
    ax.set_ylabel('Magnetic Field B (mT)')
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()

    # Save the figure
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)

def main():
    """Main function to run the analysis."""
    log_content = ""
    try:
        date_str = input("Please enter a date or identifier (e.g., '20251023') for output files: ")
        log_content += simple_logger(f"Starting analysis for identifier: {date_str}")

        # --- File Paths ---
        base_path = Path('d:/report_image/ex4/output/single')
        input_csv = base_path / 'data/input.csv'
        output_csv = base_path / f'data/{date_str}+output.csv'
        output_txt = base_path / f'data/{date_str}+output.txt'
        output_png = base_path / f'image/{date_str}+output.png'

        # --- Load Data ---
        log_content += simple_logger(f"Loading data from {input_csv}...")
        if not input_csv.exists():
            raise FileNotFoundError(f"Input file not found at {input_csv}")
        
        # Expecting columns: order, S(cm), B_+(mT), B_-(mT)
        df_input = pd.read_csv(input_csv)
        log_content += simple_logger("Data loaded successfully.")
        # --- Perform Calculations ---
        log_content += simple_logger("Calculating derived values (x, B_avg, B_ideal, error)...")
        df_processed = calculate_derived_values(df_input.copy(), PARAMS)
        log_content += simple_logger("Calculations complete.")

        # Debugging: Check if the output directory exists and is writable
        if not output_csv.parent.exists():
            print(f"Output directory does not exist: {output_csv.parent}")
        if not output_csv.parent.is_dir():
            print(f"Output path is not a directory: {output_csv.parent}")

        # --- Save Processed Data ---
        log_content += simple_logger(f"Saving processed data to {output_csv}...")
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df_processed.to_csv(output_csv, index=False, float_format='%.3f')
        log_content += simple_logger("Processed data saved.")

        # --- Generate and Save Plot ---
        log_content += simple_logger(f"Generating and saving B-x plot to {output_png}...")
        plot_b_x_graph(df_processed, PARAMS, output_png)
        log_content += simple_logger("Plot saved.")

        # --- Save Report ---
        log_content += simple_logger(f"Saving report to {output_txt}...")
        report_summary = (
            f"Analysis Report for: {date_str}\n"
            f"======================================\n"
            f"Parameters Used:\n"
            f"  - Current (I): {PARAMS['current_I']} A\n"
            f"  - Turns (N): {PARAMS['turns_N']}\n"
            f"  - Radius (R): {PARAMS['radius_R_cm']} cm\n"
            f"  - Coil Center (S): {PARAMS['coil_center_S_cm']} cm\n"
            f"======================================\n"
            f"Log Trace:\n"
            f"{log_content}"
        )
        output_txt.parent.mkdir(parents=True, exist_ok=True)
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(report_summary)
        log_content += simple_logger("Report saved.")
        
        print("\n--- Analysis Complete ---")

    except FileNotFoundError as e:
        simple_logger(str(e), "ERROR")
    except Exception as e:
        simple_logger(f"An unexpected error occurred: {e}", "CRITICAL")

if __name__ == "__main__":
    # Check if the input file exists before proceeding
    if not Path('d:/report_image/ex4/output/single/data/input.csv').exists():
        raise FileNotFoundError("Input file not found. Please ensure the file exists at the specified path.")
    
    main()
