import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional
from scipy.stats import linregress
# --- Constants and Parameters ---
R0 = 50.0  # Reference resistance R₀ in Ohms

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

def analyze_data(df: pd.DataFrame) -> Tuple[float, np.ndarray, float]:
    """
    Performs linear regression on the resistance-temperature data using linregress.
    
    Args:
        df (pd.DataFrame): DataFrame with 't(°C)' and 'R_t(Ω)' columns.

    Returns:
        A tuple containing:
        - alpha (float): The calculated temperature coefficient.
        - fit_params (np.ndarray): The polynomial fit parameters [slope, intercept].
        - r_squared (float): The R-squared value of the fit.
    """
    t = df['t(°C)']
    rt = df['R_t(Ω)']
    
    # Perform linear regression using scipy.stats.linregress
    slope, intercept, r_value,_, _ = linregress(t, rt)
    
    # The slope k corresponds to R0 * alpha
    slope_k = slope
    
    # Calculate alpha
    alpha = slope_k / R0
    
    r_squared = r_value**2
    
    simple_logger("Linear regression with linregress complete.")
    simple_logger(f"  - Slope (k): {slope_k:.4f}")
    simple_logger(f"  - Intercept: {intercept:.4f}")
    simple_logger(f"  - R-squared: {r_squared:.6f}")
    simple_logger(f"Calculated temperature coefficient (alpha) = {alpha:.5f}")
    
    # Return parameters in a format compatible with np.polyval
    fit_params = np.array([slope, intercept])
    
    return alpha, fit_params, r_squared

def plot_graph(df: pd.DataFrame, alpha: float, fit_params: np.ndarray, r_squared: float, output_path: Path) -> None:
    """
    Generates and saves the R-t plot.
    
    Args:
        df (pd.DataFrame): The data.
        alpha (float): The calculated temperature coefficient.
        fit_params (np.ndarray): The parameters from the linear fit.
        r_squared (float): The R-squared value of the fit.
        output_path (Path): The path to save the image file.
    """
    t = df['t(°C)']
    rt = df['R_t(Ω)']
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot measured data points
    ax.scatter(t, rt, label='Measured Data', color='blue', zorder=5)
    
    # Create data for the fitted line
    t_fit = np.linspace(t.min(), t.max(), 100)
    rt_fit = np.polyval(fit_params, t_fit)
    
    # Create equation string for the legend
    eq_str = f'Fit: $R_t = {R0:.2f}(1 + {alpha:.5f}t)$'
    
    # Plot the fitted line
    ax.plot(t_fit, rt_fit, 'r--', label=eq_str, linewidth=2)
    
    # --- Formatting ---
    title_str = f'Resistance vs. Temperature ($R^2 = {r_squared:.4f}$)'
    ax.set_title(title_str)
    ax.set_xlabel('Temperature t (°C)')
    ax.set_ylabel('Resistance $R_t$ (Ω)')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)
    
    # Set major ticks
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
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
    simple_logger("Script started.")
    try:
        # Check if scipy is installed
        

        date_str = input("Please enter a date or identifier (e.g., '20251114'): ")
        
        # --- File Paths ---
        base_path = Path('非平衡电桥/output')
        input_csv = base_path / 'data.csv'
        output_png = base_path / f'{date_str}+output.png'
        
        # --- Load Data ---
        df = load_or_create_data(input_csv)
        if df is None:
            raise ValueError("Failed to load or create data. Aborting.")
            
        # --- Analyze Data ---
        alpha, fit_params, r_squared = analyze_data(df)
        
        # --- Generate Plot ---
        plot_graph(df, alpha, fit_params, r_squared, output_png)

    except Exception as e:
        simple_logger(f"An error occurred: {e}", "CRITICAL")
    
    simple_logger("Script finished.")

if __name__ == "__main__":
    main()