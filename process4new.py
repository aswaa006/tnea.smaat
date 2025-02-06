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

category_percentages = {
    'OC': 0.31, 
    'BC': 0.265, 
    'BCM': 0.035, 
    'MBC': 0.20,
    'SCA': 0.03, 
    'SC': 0.15, 
    'ST': 0.01
}

def process_csv(input_file, output_file, categories):
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.strip().str.lower()

    if 'total' not in df.columns:
        raise ValueError("The CSV file must contain a 'total' column.")

    identifier_column = 'college code'
    df[identifier_column] = df[identifier_column].astype(str)

    total_rows = df[df[identifier_column].str.contains("Total", case=False, na=False)].index
    to_drop = [idx for idx in total_rows if idx > 0 and idx < len(df) - 1]
    df = df.drop(index=to_drop)

    if df[identifier_column].iloc[-1] in ["nan", "", None]:
        df = df.iloc[:-1]

    df['total'] = df['total'].astype(float)
    df['general'] = df['total'] * 0.925
    df['7.5% reservation'] = df['total'] * 0.075

    for cat, perc in category_percentages.items():
        df[cat] = df['general'] * perc
        df[f'{cat}_7.5'] = df['7.5% reservation'] * perc

    grouped = df.groupby(identifier_column)
    adjusted_frames = []
    round_columns = categories + [f"{cat}_7.5" for cat in categories]
    for _, group in grouped:
        adjusted_group = group.copy()
        for column_name in round_columns:
            if column_name in adjusted_group.columns:
                values = adjusted_group[column_name].tolist()
                adjusted_values = round_to_sum(values)
                adjusted_group[f'Rounded_{column_name}'] = adjusted_values
                adjusted_group[f'Difference_{column_name}'] = [
                    round(adjusted - original, 2)
                    for adjusted, original in zip(adjusted_values, values)
                ]
        adjusted_frames.append(adjusted_group)

    df = pd.concat(adjusted_frames, ignore_index=True)
    df = df.loc[:, ~df.columns.duplicated()].dropna(axis=1, how='all')

    for cat in categories:
        df[f'Rounded_{cat}+Rounded_{cat}_7.5'] = df[f'Rounded_{cat}'] + df[f'Rounded_{cat}_7.5']
        df[f'Difference_{cat}+Difference_{cat}_7.5'] = df[f'Difference_{cat}'] + df[f'Difference_{cat}_7.5']
        df[f'{cat}+{cat}_7.5'] = df[cat] + df[f'{cat}_7.5']

    all_castes = list(categories)
    all_castes_7_5 = [f"{cat}_7.5" for cat in categories]
    all_castes_rounded = [f"Rounded_{cat}" for cat in categories]
    all_castes_rounded_7_5 = [f"Rounded_{cat}_7.5" for cat in categories]

    df['ALL CASTES TOTAL_DECIMAL-VALUE'] = df[all_castes].sum(axis=1)
    df['ALL CASTES_7.5 TOTAL_DECIMAL-VALUE'] = df[all_castes_7_5].sum(axis=1)
    df['ALL CASTES TOTAL_DECIMAL-VALUE+ALL CASTES_7.5 TOTAL_DECIMAL-VALUE'] = (
        df['ALL CASTES TOTAL_DECIMAL-VALUE'] + df['ALL CASTES_7.5 TOTAL_DECIMAL-VALUE']
    )
    df['ALL CASTE TOTAL_INTEGER-VALUE'] = df[all_castes_rounded].sum(axis=1)
    df['ALL CASTES_7.5 TOTAL_INTEGER-VALUE'] = df[all_castes_rounded_7_5].sum(axis=1)
    df['ALL CASTE TOTAL_INTEGER-VALUE+ALL CASTES_7.5 TOTAL_INTEGER-VALUE'] = (
        df['ALL CASTE TOTAL_INTEGER-VALUE'] + df['ALL CASTES_7.5 TOTAL_INTEGER-VALUE']
    )

    new_column_order = [
        identifier_column, 'category', 'autonomous status', 'co.ed status',
        'district', 'college name', 'course', 'total', 'general', '7.5% reservation'
    ]

    ordered_categories = ['OC', 'BC', 'BCM', 'MBC', 'SCA', 'SC', 'ST']
    for cat in ordered_categories:
        new_column_order.extend([
            cat, f'Rounded_{cat}', f'Difference_{cat}', f'{cat}_7.5', f'Rounded_{cat}_7.5',
            f'Difference_{cat}_7.5', f'Rounded_{cat}+Rounded_{cat}_7.5',
            f'Difference_{cat}+Difference_{cat}_7.5', f'{cat}+{cat}_7.5'
        ])

    new_column_order += [
        'ALL CASTES TOTAL_DECIMAL-VALUE',
        'ALL CASTES_7.5 TOTAL_DECIMAL-VALUE',
        'ALL CASTES TOTAL_DECIMAL-VALUE+ALL CASTES_7.5 TOTAL_DECIMAL-VALUE',
        'ALL CASTE TOTAL_INTEGER-VALUE',
        'ALL CASTES_7.5 TOTAL_INTEGER-VALUE',
        'ALL CASTE TOTAL_INTEGER-VALUE+ALL CASTES_7.5 TOTAL_INTEGER-VALUE'
    ]

    df = df[new_column_order]

    new_rows = []
    for _, group in df.groupby(identifier_column):
        new_rows.append(group)
        total_row = group.sum(numeric_only=True)
        total_row[identifier_column] = "Total"
        new_rows.append(pd.DataFrame([total_row]))

    df = pd.concat(new_rows, ignore_index=True)
    df = df.iloc[:-3]

    final_total = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            final_total[col] = df[col].sum()
        else:
            final_total[col] = ""
    final_total[identifier_column] = "Grand Total"
    df = pd.concat([df, pd.DataFrame([final_total])], ignore_index=True)

    df.to_csv(output_file, index=False, float_format="%.4f")
    print(f"Processed CSV saved as {output_file}")

# Example usage:
process_csv("1322233112output.csv", "13222222331aa34512output.csv", list(category_percentages.keys()))