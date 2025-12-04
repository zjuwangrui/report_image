import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional, Dict
from scipy.signal import find_peaks
from matplotlib import ticker

def simple_logger(message: str, level: str = "INFO") -> str:
    """A simple logger that returns a formatted string and prints it."""
    log_message = f"[{level}] {message}"
    print(log_message)
    return log_message + "\n"

def load_or_create_data(file_path: Path) -> Optional[pd.DataFrame]:
    """Loads data from CSV or creates a dummy file if it doesn't exist."""
    
    try:
        df = pd.read_csv(file_path)
        simple_logger("Data loaded successfully.")
        return df
    except Exception as e:
        simple_logger(f"Failed to read data file: {e}", "ERROR")
        return None

def process_and_normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes the x-coordinate so that the minimum value becomes 0."""
    simple_logger("Normalizing x-coordinates...")
    x_min = df['x(mm)'].min()
    df['x_normalized(mm)'] = df['x(mm)'] - x_min
    simple_logger(f"Normalization complete. Original min x ({x_min:.2f} mm) is now 0.")
    return df

def find_diffraction_peaks(df: pd.DataFrame) -> Dict[str, float]:
    """Finds the central and first-order maximum photocurrents."""
    simple_logger("Finding diffraction maxima...")
    
    current_col = 'I(10^-8 A)'
    
    # Use scipy's find_peaks to identify all local maxima
    # A prominence is set to filter out minor noise peaks
    peaks_indices, _ = find_peaks(df[current_col], prominence=1)
    
    if len(peaks_indices) < 3:
        simple_logger("Could not find enough peaks (at least 3 required for central + 2 first-order).", "ERROR")
        simple_logger("Using global max as central and NaN for first-order.", "WARNING")
        central_max_I = df[current_col].max()
        return {"central_max_I": central_max_I, "first_order_max_I": np.nan}

    peak_currents = df[current_col].iloc[peaks_indices].values
    
    # Sort peaks by current to find the central maximum (the highest one)
    sorted_peak_indices = np.argsort(-peak_currents) # Sort descending
    
    central_max_I = peak_currents[sorted_peak_indices[0]]
    
    # The next two highest peaks are the first-order maxima
    first_order_max_1 = peak_currents[sorted_peak_indices[1]]
    first_order_max_2 = peak_currents[sorted_peak_indices[2]]
    
    # Average the two first-order maxima for a more robust value
    first_order_max_avg_I = (first_order_max_1 + first_order_max_2) / 2
    
    simple_logger(f"Central maximum found: I = {central_max_I:.2f} x 10^-8 A")
    simple_logger(f"First-order maxima found: I = {first_order_max_1:.2f}, {first_order_max_2:.2f}. Average = {first_order_max_avg_I:.2f} x 10^-8 A")
    
    return {
        "central_max_I": central_max_I,
        "first_order_max_I": first_order_max_avg_I,
        "peak_indices": peaks_indices # Pass this for plotting
    }

def plot_diffraction_pattern(df: pd.DataFrame, peaks_info: Dict, output_path: Path) -> None:
    """Generates and saves the I-x diffraction plot."""
    x_norm = df['x_normalized(mm)']
    current = df['I(10^-8 A)']
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot the diffraction curve
    ax.plot(x_norm, current, label='Diffraction Pattern', color='cyan')
    
    # Highlight the detected peaks
    if "peak_indices" in peaks_info:
        peak_indices = peaks_info["peak_indices"]
        ax.scatter(
            df['x_normalized(mm)'].iloc[peak_indices],
            df['I(10^-8 A)'].iloc[peak_indices],
            color='red',
            zorder=5,
            label='Detected Maxima'
        )

    # --- Formatting ---
    ax.set_title('Single-Slit Diffraction Pattern')
    ax.set_xlabel('Position x (mm)')
    ax.set_ylabel('Photocurrent I ($\\times 10^{-8}$ A)')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Set x-axis tick interval to 0.04 mm
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right") # Rotate for readability
    
    ax.legend()
    fig.tight_layout()

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
    log_content = ""
    try:
        date_str = input("Please enter a date or identifier (e.g., '20251115'): ")
        log_content += simple_logger(f"Starting analysis for identifier: {date_str}")

        # --- File Paths ---
        base_path = Path('./光的衍射/output')
        input_csv = base_path / 'data/input.csv'
        output_txt = base_path / 'data' / f'{date_str}+output.txt'
        output_png = base_path / 'image' / f'{date_str}+output.png'

        # --- Load and Process Data ---
        df = load_or_create_data(input_csv)
        if df is None:
            raise ValueError("Failed to load or create data. Aborting.")
        
        df_processed = process_and_normalize_data(df.copy())
        
        # --- Find Peaks ---
        peaks_info = find_diffraction_peaks(df_processed)
        
        # --- Generate Plot ---
        plot_diffraction_pattern(df_processed, peaks_info, output_png)

        # --- Save Report ---
        log_content += simple_logger(f"Saving report to {output_txt}...")
        report_summary = (
            f"Analysis Report for Single-Slit Diffraction: {date_str}\n"
            f"======================================================\n"
            f"Key Findings:\n"
            f"  - Central Maximum Photocurrent: {peaks_info.get('central_max_I', 'N/A'):.2f} x 10^-8 A\n"
            f"  - First-Order Maximum Photocurrent (Avg): {peaks_info.get('first_order_max_I', 'N/A'):.2f} x 10^-8 A\n"
            f"======================================================\n"
            f"Log Trace:\n"
            f"{log_content}"
        )
        output_txt.parent.mkdir(parents=True, exist_ok=True)
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(report_summary)
        
        print("\n--- Analysis Complete ---")

    except Exception as e:
        simple_logger(f"An unexpected error occurred: {e}", "CRITICAL")

if __name__ == "__main__":
    main()