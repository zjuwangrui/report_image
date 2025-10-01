import pandas as pd
from typing import List

def calculate_restitution_coefficient(input_csv: str, output_csv: str) -> None:
    """
    Calculates the coefficient of restitution from a CSV file and writes it back to the CSV.

    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file.
    """

    try:
        df: pd.DataFrame = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Input file '{input_csv}' not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    # Constants
    m1: float = 0.3071  # kg
    m2: float = 0.3103  # kg

    try:
        # Calculate initial and final momentum
        df['p1_0(kg m/s)'] = m1 * df['v1_0(m/s)']
        df['p1_1(kg m/s)'] = m1 * df['v1_1(m/s)']
        df['p2_0(kg m/s)'] = m2 * df['v2_0(m/s)']
        df['p2_1(kg m/s)'] = m2 * df['v2_1(m/s)']


        # Calculate initial and final kinetic energy
        df['E1_0(J)'] = 0.5 * m1 * df['v1_0(m/s)']**2
        df['E1_1(J)'] = 0.5 * m1 * df['v1_1(m/s)']**2
        df['E2_0(J)'] = 0.5 * m2 * df['v2_0(m/s)']**2
        df['E2_1(J)'] = 0.5 * m2 * df['v2_1(m/s)']**2

        # Calculate total initial and final momentum
        df['p1(kg m/s)'] = df['p1_0(kg m/s)'] + df['p2_0(kg m/s)']
        df['p2(kg m/s)'] = df['p1_1(kg m/s)'] + df['p2_1(kg m/s)']

        # Calculate total initial and final kinetic energy
        df['E1(J)'] = df['E1_0(J)'] + df['E2_0(J)']
        df['E2(J)'] = df['E1_1(J)'] + df['E2_1(J)']

        # Calculate change in total momentum and kinetic energy
        df['deltp(kg m/s)'] = df['p2(kg m/s)'] - df['p1(kg m/s)']
        df['deltE(J)'] = df['E2(J)'] - df['E1(J)']

        # Calculate fractional change in momentum and kinetic energy
        df['deltp/p1'] = df['deltp(kg m/s)'] / df['p1(kg m/s)']
        df['deltE/E1'] = df['deltE(J)'] / df['E1(J)']

        # Calculate coefficient of restitution
        df['e'] = (df['v2_1(m/s)'] - df['v1_1(m/s)']) / (df['v1_0(m/s)'] - df['v2_0(m/s)'])

    except ZeroDivisionError:
        print("Error: Division by zero encountered while calculating 'e' or fractional changes. Check your data.")
        return
    except Exception as e:
        print(f"Error calculating 'e' or other parameters: {e}")
        return

    # Format 'e', 'deltp/p', and 'deltE/E' as percentages
            
    df['p1(kg m/s)'] = df['p1(kg m/s)'].apply(lambda x: f"{x:.4}")
    df['p2(kg m/s)'] = df['p2(kg m/s)'].apply(lambda x: f"{x:.4}")
    df['deltp(kg m/s)'] = df['deltp(kg m/s)'].apply(lambda x: f"{x:.4}")
    df['E1(J)'] = df['E1(J)'].apply(lambda x: f"{x:.4}")
    df['E2(J)'] = df['E2(J)'].apply(lambda x: f"{x:.4}")
    df['deltE(J)'] = df['deltE(J)'].apply(lambda x: f"{x:.4}")
    df['e'] = df['e'].apply(lambda x: f"{x:.1%}")
    df['deltp/p1'] = df['deltp/p1'].apply(lambda x: f"{x:.0%}")
    df['deltE/E1'] = df['deltE/E1'].apply(lambda x: f"{x:.0%}")
    output_columns: List[str] = ['exp_order', 'v1_0(m/s)', 'v1_1(m/s)', 'v2_0(m/s)', 'v2_1(m/s)',
                                 'p1(kg m/s)', 'p2(kg m/s)', 'E1(J)', 'E2(J)', 'deltp(kg m/s)', 'deltE(J)',
                                 'deltp/p1', 'deltE/E1', 'e']
    df_output: pd.DataFrame = df[output_columns]
    try:
        df_output.to_csv(output_csv, index=False)
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        return

    print(f"Successfully calculated parameters and wrote to '{output_csv}'.")

if __name__ == "__main__":
    input_file: str = 'd:\\report_image\\raw_data\\non_total\\col.csv'
    output_file: str = 'd:\\report_image\\raw_data\\non_total\\output.csv'
    calculate_restitution_coefficient(input_file, output_file)