import pandas as pd

def add_computed_columns(csv_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Standardize column names to lowercase
    df.columns = df.columns.str.strip().str.lower()  

    # Check if 'total' column exists
    if 'total' not in df.columns:
        raise ValueError(f"The CSV file must contain a 'total' column. Found columns: {df.columns}")

    # Ensure 'total' column contains numerical values
    df['total'] = df['total'].astype(float)  

    # Compute new columns (preserving float values)
    df['general'] = df['total'] * 0.925
    df['7.5% reservation'] = df['total'] * 0.075

    # Save the modified CSV
    output_file = "1_" + csv_file
    df.to_csv(output_file, index=False)
    print(f"Modified CSV saved as {output_file}")

# Example usage
csv_filename = "govtreserved.csv"  # Replace with your actual file
add_computed_columns(csv_filename)
