import csv
import pandas as pd

def round_to_sum(values):
    original_sum = round(sum(values))
    floored_values = [int(v) for v in values]
    floored_sum = sum(floored_values)
    difference = original_sum - floored_sum

    remainders = [(i, v - floored_values[i]) for i, v in enumerate(values)]
    remainders.sort(key=lambda x: x[1], reverse=True)

    for i in range(difference):
        floored_values[remainders[i][0]] += 1

    return floored_values

# Define category_percentages globally
category_percentages = {
    'OC': 0.31, 'BC': 0.265, 'BCM': 0.035, 'MBC': 0.20,
    'SC': 0.15, 'SCA': 0.03, 'ST': 0.01
}

def process_csv(input_file, output_file, column_names):
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.strip().str.lower()
    
    if 'total' not in df.columns:
        raise ValueError("The CSV file must contain a 'total' column.")
    
    df['total'] = df['total'].astype(float)
    df['general'] = df['total'] * 0.925
    df['7.5% reservation'] = df['total'] * 0.075
    
    for category, percentage in category_percentages.items():
        df[category] = df['general'] * percentage
        df[f'{category}_7.5'] = df['7.5% reservation'] * percentage
    
    for column_name in column_names:
        if column_name in df.columns:
            values = df[column_name].tolist()
            adjusted_values = round_to_sum(values)
            df[f'Rounded_{column_name}'] = adjusted_values
            df[f'Difference_{column_name}'] = [round(adjusted - original, 2) for adjusted, original in zip(adjusted_values, values)]
    
    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Remove empty columns
    df = df.dropna(axis=1, how='all')
    
    # Drop columns Y to AL and BO
    cols_to_drop = df.columns[24:38].tolist() + ['bo']  # Adjusted index range and added 'bo'
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    df.to_csv(output_file, index=False, float_format="%.4f")
    print(f"Processed CSV saved as {output_file}")

# Example usage
#input_csv = "2_1_govtreserved.csv"  # Replace with actual input file
#output_csv = "444443_2_1_govtreserved.csv"  # Replace with desired output file
#process_csv(input_csv, output_csv, list(category_percentages.keys()) + [f"{key}_7.5" for key in category_percentages.keys()])
