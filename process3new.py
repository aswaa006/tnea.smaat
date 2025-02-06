import csv
import pandas as pd

def round_to_sum(values):
    original_sum = round(sum(values))
    floored_values = [int(v) for v in values]
    floored_sum = sum(floored_values)
    difference = original_sum - floored_sum
    
    remainders = sorted(enumerate(values), key=lambda x: x[1] - floored_values[x[0]], reverse=True)
    
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
    
    identifier_column = 'college code'  # Adjust based on actual column name
    df[identifier_column] = df[identifier_column].astype(str)

    total_rows = df[df[identifier_column].str.contains("Total", case=False, na=False)].index
    to_drop = [idx for idx in total_rows if idx > 0 and idx < len(df) - 1]
    df = df.drop(index=to_drop)

    if df[identifier_column].iloc[-1] in ["nan", "", None]:
        df = df.iloc[:-1]
    
    df['total'] = df['total'].astype(float)
    df['general'] = df['total'] * 0.925
    df['7.5% reservation'] = df['total'] * 0.075
    
    for category, percentage in category_percentages.items():
        df[category] = df['general'] * percentage
        df[f'{category}_7.5'] = df['7.5% reservation'] * percentage
    
    grouped = df.groupby(identifier_column)
    adjusted_frames = []
    
    for _, group in grouped:
        adjusted_group = group.copy()
        for column_name in column_names:
            if column_name in adjusted_group.columns:
                values = adjusted_group[column_name].tolist()
                adjusted_values = round_to_sum(values)
                adjusted_group[f'Rounded_{column_name}'] = adjusted_values
                adjusted_group[f'Difference_{column_name}'] = [round(adjusted - original, 2) for adjusted, original in zip(adjusted_values, values)]
        adjusted_frames.append(adjusted_group)
    
    df = pd.concat(adjusted_frames, ignore_index=True)
    df = df.loc[:, ~df.columns.duplicated()].dropna(axis=1, how='all')
    
    new_column_order = [identifier_column, 'category', 'autonomous status', 'co.ed status', 'district', 'college name', 'course', 'total', 'general', '7.5% reservation']
    for category in category_percentages.keys():
        new_column_order.append(category)
        new_column_order.append(f'Rounded_{category}')
        new_column_order.append(f'Difference_{category}')
        new_column_order.append(f'{category}_7.5')
        new_column_order.append(f'Rounded_{category}_7.5')
        new_column_order.append(f'Difference_{category}_7.5')
    
    df = df[new_column_order]
    
    new_rows = []
    for _, group in df.groupby(identifier_column):
        new_rows.append(group)
        total_row = group.sum(numeric_only=True)
        total_row[identifier_column] = "Total"
        new_rows.append(pd.DataFrame([total_row]))
    
    df = pd.concat(new_rows, ignore_index=True)
    df.to_csv(output_file, index=False, float_format="%.4f")
    print(f"Processed CSV saved as {output_file}")

# Example usage:
process_csv("2_og.csv", "1322111rr233112aaoutput.csv", list(category_percentages.keys()) + [f"{key}_7.5" for key in category_percentages.keys()])
