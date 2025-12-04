import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional

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

def calculate_power_factor(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates the power factor and fills the corresponding column."""
    simple_logger("Calculating power factor cos(phi)...")
    
    # Calculate cos(phi) = P / (U * I)
    # Use .get() for safer column access
    P = df.get('P\\W')
    U = df.get('U\\V')
    I = df.get('I\\A')
    
    if P is None or U is None or I is None:
        raise KeyError("One or more required columns ('P\\W', 'U\\V', 'I\\A') are missing.")
        
    # Avoid division by zero
    apparent_power = U * I
    df['\\cos \\phi'] = np.where(apparent_power > 0, P / apparent_power, 0)
    
    # Round to 4 decimal places
    df['\\cos \\phi'] = df['\\cos \\phi'].round(4)
    
    simple_logger("Power factor calculation complete.")
    return df

def plot_and_fit_graph(df: pd.DataFrame, output_path: Path) -> None:
    """Generates and saves the cos(phi) vs. C plot with a polynomial fit."""
    C = df['C(\\mu F)']
    cos_phi = df['\\cos \\phi']
    
    # Perform a 2nd degree polynomial fit: y = ax^2 + bx + c
    fit_params = np.polyfit(C, cos_phi, 2)
    poly_func = np.poly1d(fit_params)
    
    simple_logger(f"Polynomial fit (2nd degree) complete. Parameters: a={fit_params[0]}, b={fit_params[1]}, c={fit_params[2]}")
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot measured data points
    ax.scatter(C, cos_phi, label='Measured Data', color='blue', zorder=5)
    
    # Create data for the fitted line
    C_fit = np.linspace(C.min(), C.max(), 200)
    cos_phi_fit = poly_func(C_fit)
    
    # Create equation string with 4 significant figures for parameters
    eq_str = (f'Fit: $y = {fit_params[0]:.4g}x^2 + {fit_params[1]:.4g}x + {fit_params[2]:.4g}$')
    
    # Plot the fitted line
    ax.plot(C_fit, cos_phi_fit, 'r--', label=eq_str, linewidth=2)
    
    # --- Formatting ---
    ax.set_title('Power Factor vs. Capacitance')
    ax.set_xlabel('Capacitance C (μF)')
    ax.set_ylabel('Power Factor $\\cos(\\phi)$')
    ax.grid(True)
    ax.legend(fontsize=12)
    
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
        date_str = input("Please enter a date or identifier (e.g., '20251114'): ")
        
        # --- File Paths ---
        base_path = Path('./交流电功率因数实验/output')
        input_csv = base_path / 'data' / 'input.csv'
        output_csv = base_path / 'data' / f'{date_str}+output.csv'
        output_png = base_path / 'image' / f'{date_str}+output.png'
        
        # --- Load and Process Data ---
        df = load_or_create_data(input_csv)
        if df is None:
            raise ValueError("Failed to load or create data. Aborting.")
        
        df_processed = calculate_power_factor(df.copy())
        
        # --- Save Processed Data ---
        df_processed.to_csv(output_csv, index=False, float_format='%.4f')
        simple_logger(f"Processed data saved to {output_csv}")
        
        # --- Generate Plot ---
        plot_and_fit_graph(df_processed, output_png)

    except Exception as e:
        simple_logger(f"An error occurred: {e}", "CRITICAL")
    
    simple_logger("Script finished.")

if __name__ == "__main__":
    main()