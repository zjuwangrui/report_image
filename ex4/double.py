import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Tuple
from matplotlib import ticker

# Use a non-interactive backend to prevent issues in certain environments
import matplotlib
matplotlib.use('Agg')

# --- Constants and Parameters ---
# Permeability of free space (μ₀) in T·m/A
MU_0 = 4 * np.pi * 1e-7
# Experiment parameters for the Helmholtz coil
PARAMS: Dict[str, float] = {
    "current_I": 0.4,          # Amperes
    "turns_N": 400,            # Turns per coil
    "radius_R_cm": 10.0,       # Centimeters
    "center_S_cm": 15.0,       # Center of the two-coil system
}

def simple_logger(message: str, level: str = "INFO") -> str:
    """A simple logger that returns a formatted string and prints it."""
    log_message = f"[{level}] {message}"
    print(log_message)
    return log_message + "\n"

def calculate_derived_values(df: pd.DataFrame, params: Dict[str, float]) -> pd.DataFrame:
    """
    Calculates x and B_avg from the raw data.
    
    Args:
        df (pd.DataFrame): Input dataframe with S(cm), B_+(mT), B_-(mT).
        params (Dict[str, float]): Dictionary of physical parameters.

    Returns:
        pd.DataFrame: Dataframe with calculated 'x(cm)' and 'B_avg(mT)'.
    """
    df['x(cm)'] = df['S(cm)'] - params["center_S_cm"]
    df['x(cm)'] = df['x(cm)'].round(0).astype(int)
    df['B_avg(mT)'] = (df['B_+(mT)'].abs() + df['B_-(mT)'].abs()) / 2
    return df

def calculate_center_field_and_error(df: pd.DataFrame, params: Dict[str, float]) -> Tuple[float, float, float]:
    """
    Calculates the theoretical B at x=0 and the relative error.

    Args:
        df (pd.DataFrame): Processed dataframe with B_avg(mT) and x(cm).
        params (Dict[str, float]): Dictionary of physical parameters.

    Returns:
        A tuple containing (measured_B_at_center, theoretical_B_at_center, relative_error).
    """
    radius_R_m = params["radius_R_cm"] / 100.0
    
    # Theoretical B at the center (x=0) for a Helmholtz coil
    # B(0) = (4/5)^(3/2) * (μ₀ * N * I / R)
    constant_factor = (4/5)**1.5
    b_ideal_tesla = constant_factor * (MU_0 * params["turns_N"] * params["current_I"] / radius_R_m)
    b_ideal_mT = b_ideal_tesla * 1000

    # Find measured B at x=0
    b_measured_at_center_series = df[df['x(cm)'] == 0]['B_avg(mT)']
    if b_measured_at_center_series.empty:
        raise ValueError("No measurement found at the center (x=0) to calculate relative error.")
    
    b_measured_mT = b_measured_at_center_series.iloc[0]
    
    # Calculate relative error
    relative_error = abs(b_measured_mT - b_ideal_mT) / b_ideal_mT
    
    return b_measured_mT, b_ideal_mT, relative_error

def plot_b_x_graph(df: pd.DataFrame, output_path: Path) -> None:
    """
    Plots the measured B-x graph with a fitted curve.

    Args:
        df (pd.DataFrame): The processed data.
        output_path (Path): Path to save the image.
    """
    x_cm = df['x(cm)']
    b_avg_mT = df['B_avg(mT)']

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot original measured data points
    ax.scatter(x_cm, b_avg_mT, label='Measured Data Points', color='blue', zorder=5)

    # Fit a polynomial to the measured data for a smooth curve
    # A higher-degree polynomial (e.g., 8) is suitable for the flat top of a Helmholtz coil field
    poly_coeffs = np.polyfit(x_cm, b_avg_mT, 8)
    poly_func = np.poly1d(poly_coeffs)

    # Generate smooth x values for the fitted curve
    x_smooth_cm = np.linspace(x_cm.min(), x_cm.max(), 300)
    b_fit_smooth_mT = poly_func(x_smooth_cm)

    # Plot the fitted curve
    ax.plot(x_smooth_cm, b_fit_smooth_mT, label='Fitted Curve of Measured Data', color='red', linestyle='--')

    # Formatting
    ax.set_title('Magnetic Field B along the Axis of a Helmholtz Coil')
    ax.set_xlabel('Position x (cm)')
    ax.set_ylabel('Magnetic Field B (mT)')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1)) # Set x-axis ticks to 1cm intervals
    ax.legend()

    # Save the figure
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    simple_logger(f"Plot successfully saved to {output_path}")

def main():
    """Main function to run the analysis."""
    log_content = ""
    try:
        date_str = input("Please enter a date or identifier (e.g., '20251024') for output files: ")
        log_content += simple_logger(f"Starting analysis for identifier: {date_str}")

        # --- File Paths ---
        base_path = Path('d:/report_image/ex4/output/double')
        input_csv = base_path / 'data/input.csv'
        output_csv = base_path / f'data/{date_str}+output.csv'
        output_txt = base_path / f'data/{date_str}+output.txt'
        output_png = base_path / f'image/{date_str}+output.png'

        # --- Load or Create Data ---
        log_content += simple_logger(f"Looking for data at {input_csv}...")
        if not input_csv.exists():
            log_content += simple_logger(f"Input file not found. Creating a dummy file at {input_csv}", "WARNING")
            dummy_data = {
                'order': range(1, 22),
                'S(cm)': np.arange(5, 26, 1),
                'B_+(mT)': [0.75, 0.88, 1.03, 1.18, 1.32, 1.42, 1.48, 1.51, 1.52, 1.51, 1.50, 1.51, 1.52, 1.51, 1.48, 1.42, 1.32, 1.18, 1.03, 0.88, 0.75],
                'B_-(mT)': [-0.75, -0.88, -1.03, -1.18, -1.32, -1.42, -1.48, -1.51, -1.52, -1.51, -1.50, -1.51, -1.52, -1.51, -1.48, -1.42, -1.32, -1.18, -1.03, -0.88, -0.75]
            }
            df_input = pd.DataFrame(dummy_data)
            input_csv.parent.mkdir(parents=True, exist_ok=True)
            df_input.to_csv(input_csv, index=False)
            log_content += simple_logger("Dummy input file created.")
        else:
            df_input = pd.read_csv(input_csv)
            log_content += simple_logger("Data loaded successfully.")

        # --- Perform Calculations ---
        log_content += simple_logger("Calculating B_avg and x positions...")
        df_processed = calculate_derived_values(df_input.copy(), PARAMS)
        log_content += simple_logger("B_avg and x calculations complete.")

        log_content += simple_logger("Calculating theoretical center field and relative error...")
        b_measured, b_ideal, rel_error = calculate_center_field_and_error(df_processed, PARAMS)
        log_content += simple_logger(f"Measured B at center: {b_measured:.4f} mT")
        log_content += simple_logger(f"Theoretical B at center (B₀): {b_ideal:.4f} mT")
        log_content += simple_logger(f"Relative Error at center: {rel_error:.2%}")
        
        # --- Save Processed Data ---
        log_content += simple_logger(f"Saving processed data to {output_csv}...")
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df_processed.to_csv(output_csv, index=False, float_format='%.3f')
        log_content += simple_logger("Processed data saved.")

        # --- Generate and Save Plot ---
        log_content += simple_logger(f"Generating and saving B-x plot...")
        plot_b_x_graph(df_processed, output_png)

        # --- Save Report ---
        log_content += simple_logger(f"Saving report to {output_txt}...")
        report_summary = (
            f"Analysis Report for Helmholtz Coil: {date_str}\n"
            f"==================================================\n"
            f"Parameters Used:\n"
            f"  - Current (I): {PARAMS['current_I']} A\n"
            f"  - Turns per coil (N): {PARAMS['turns_N']}\n"
            f"  - Radius (R): {PARAMS['radius_R_cm']} cm\n"
            f"==================================================\n"
            f"Center Point (x=0) Analysis:\n"
            f"  - Measured Magnetic Field at Center: {b_measured:.4f} mT\n"
            f"  - Theoretical Magnetic Field (B₀): {b_ideal:.4f} mT\n"
            f"  - Relative Error: {rel_error:.2%}\n"
            f"==================================================\n"
            f"Log Trace:\n"
            f"{log_content}"
        )
        output_txt.parent.mkdir(parents=True, exist_ok=True)
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(report_summary)
        
        print("\n--- Analysis Complete ---")
        print(f"Find your generated files in: {base_path.resolve()}")

    except (FileNotFoundError, ValueError) as e:
        simple_logger(str(e), "ERROR")
    except Exception as e:
        simple_logger(f"An unexpected error occurred: {e}", "CRITICAL")

if __name__ == "__main__":
    main()
