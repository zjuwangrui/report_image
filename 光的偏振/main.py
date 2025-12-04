import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional
from scipy.stats import linregress

def simple_logger(message: str, level: str = "INFO") -> None:
    """A simple logger that prints a formatted message."""
    print(f"[{level}] {message}")

def load_or_create_data(file_path: Path) -> Optional[pd.DataFrame]:
    """Loads data from CSV or creates a dummy file if it doesn't exist."""
    try:
        df = pd.read_csv(file_path)
        simple_logger("Data loaded successfully.")
        return df
    except Exception as e:
        simple_logger(f"Failed to read data file: {e}", "ERROR")
        return None

def process_and_analyze_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, tuple, float]:
    """
    Calculates cos^2(phi) and performs linear regression against photocurrent.
    
    Returns:
        A tuple containing:
        - The processed DataFrame with the new 'cos_sq_phi' column.
        - A tuple of fit parameters (slope, intercept).
        - The R-squared value of the fit.
    """
    simple_logger("Processing data and performing linear regression...")
    
    # Convert angle from degrees to radians and calculate cos^2(phi)
    phi_degrees = df['\\phi']
    phi_radians = np.deg2rad(phi_degrees)
    df['cos_sq_phi'] = np.cos(phi_radians)**2
    
    # Perform linear regression: i = slope * cos_sq_phi + intercept
    photocurrent = df['i(\\mu A)']
    cos_sq_phi = df['cos_sq_phi']
    
    slope, intercept, r_value, _, _ = linregress(cos_sq_phi, photocurrent)
    r_squared = r_value**2
    
    simple_logger(f"Linear regression complete. R-squared = {r_squared:.4f}")
    simple_logger(f"  - Slope (i_max): {slope:.2f}")
    simple_logger(f"  - Intercept: {intercept:.2f}")
    
    return df, (slope, intercept), r_squared

def plot_graph(df: pd.DataFrame, fit_params: tuple, r_squared: float, output_path: Path) -> None:
    """Generates and saves the i vs. cos^2(phi) plot."""
    
    slope, intercept = fit_params
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot measured data points
    ax.scatter(df['cos_sq_phi'], df['i(\\mu A)'], label='Measured Data', color='blue', zorder=5)
    
    # Create data for the fitted line
    x_fit = np.array([0, 1])
    y_fit = slope * x_fit + intercept
    
    # Create equation string for the legend
    eq_str = f'Fit: $i = {slope:.2f} \\cdot \\cos^2(\\phi) + {intercept:.2f}$'
    
    # Plot the fitted line
    ax.plot(x_fit, y_fit, 'r--', label=eq_str, linewidth=2)
    
    # --- Formatting ---
    title_str = f'Photocurrent vs. $\\cos^2(\\phi)$  ($R^2 = {r_squared:.4f}$)'
    ax.set_title(title_str)
    ax.set_xlabel('$\\cos^2(\\phi)$')
    ax.set_ylabel('Photocurrent $i$ (μA)')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)
    
    # Set axis limits for clarity
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, df['i(\\mu A)'].max() * 1.1)
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300)
        simple_logger(f"Plot successfully saved to {output_path}")
    except Exception as e:
        simple_logger(f"Failed to save plot: {e}", "ERROR")
    finally:
        plt.close(fig)

def main():
    """Main function to run the analysis."""
    simple_logger("Script for Malus's Law verification started.")
    try:


        date_str = input("Please enter a date or identifier (e.g., '20251116'): ")
        
        # --- File Paths ---
        base_path = Path('./光的偏振/output')
        input_csv = base_path / 'data' / 'input.csv'
        output_png = base_path / 'image' / f'{date_str}+output.png'
        
        # --- Load and Process Data ---
        df = load_or_create_data(input_csv)
        if df is None:
            raise ValueError("Failed to load or create data. Aborting.")
        
        df_processed, fit_params, r_squared = process_and_analyze_data(df)
        
        # --- Generate Plot ---
        plot_graph(df_processed, fit_params, r_squared, output_png)

    except Exception as e:
        simple_logger(f"An error occurred: {e}", "CRITICAL")
    
    simple_logger("Script finished.")

if __name__ == "__main__":
    main()