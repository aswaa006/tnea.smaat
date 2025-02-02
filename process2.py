import pandas as pd
import os

def add_computed_columns(csv_file):
    # Check if file exists before proceeding
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Error: The file '{csv_file}' was not found.")

    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Standardize column names to lowercase and remove leading/trailing spaces
    df.columns = df.columns.str.strip().str.lower()

    # Ensure 'total' column exists (case insensitive)
    if 'total' not in df.columns:
        raise ValueError("Error: The CSV file must contain a 'total' column.")

    # Convert 'total' column to numeric (handle errors safely)
    df['total'] = pd.to_numeric(df['total'], errors='coerce')

    # Check for missing values in 'total' column after conversion
    if df['total'].isnull().any():
        raise ValueError("Error: 'total' column contains non-numeric values or missing data.")

    # Compute new columns while keeping decimal values
    df['general'] = df['total'] * 0.925
    df['7.5% reservation'] = df['total'] * 0.075

    # Compute values for general category
    df['OC'] = df['general'] * 0.31
    df['BC'] = df['general'] * 0.265
    df['BCM'] = df['general'] * 0.035
    df['MBC'] = df['general'] * 0.20
    df['SC'] = df['general'] * 0.15
    df['SCA'] = df['general'] * 0.03
    df['ST'] = df['general'] * 0.01

    # Compute values for 7.5% reservation category
    df['OC_7.5'] = df['7.5% reservation'] * 0.31
    df['BC_7.5'] = df['7.5% reservation'] * 0.265
    df['BCM_7.5'] = df['7.5% reservation'] * 0.035
    df['MBC_7.5'] = df['7.5% reservation'] * 0.20
    df['SC_7.5'] = df['7.5% reservation'] * 0.15
    df['SCA_7.5'] = df['7.5% reservation'] * 0.03
    df['ST_7.5'] = df['7.5% reservation'] * 0.01

    # Define the output file name
    output_file = f"2_{os.path.basename(csv_file)}"

    # Save the modified CSV (keep decimals up to 4 places)
    df.to_csv(output_file, index=False, float_format="%.4f")

    print(f"Modified CSV saved as: {output_file}")

# Example usage
csv_filename = "og.csv"  # Ensure this file is in the correct directory
add_computed_columns(csv_filename)
