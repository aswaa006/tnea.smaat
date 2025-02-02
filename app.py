from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define category percentages for processing
category_percentages = {
    'OC': 0.31, 'BC': 0.265, 'BCM': 0.035, 'MBC': 0.20,
    'SC': 0.15, 'SCA': 0.03, 'ST': 0.01
}

def round_to_sum(values):
    """Rounds values while ensuring the sum remains unchanged."""
    original_sum = round(sum(values))
    floored_values = [int(v) for v in values]
    floored_sum = sum(floored_values)
    difference = original_sum - floored_sum

    remainders = sorted(enumerate(values), key=lambda x: x[1] - floored_values[x[0]], reverse=True)

    for i in range(difference):
        floored_values[remainders[i][0]] += 1

    return floored_values

def add_computed_columns(input_file):
    """Processes CSV by adding 'general' and '7.5% reservation' columns."""
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.strip().str.lower()

    if 'total' not in df.columns:
        raise ValueError(f"The CSV file must contain a 'total' column. Found columns: {df.columns}")

    df['total'] = df['total'].astype(float)
    df['general'] = df['total'] * 0.925
    df['7.5% reservation'] = df['total'] * 0.075

    output_file = os.path.join(UPLOAD_FOLDER, "1_" + os.path.basename(input_file))
    df.to_csv(output_file, index=False)
    return output_file

def process_csv(input_file, output_file, column_names):
    """Processes CSV by calculating category-based distributions and rounding values."""
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

    df = df.loc[:, ~df.columns.duplicated()]
    df = df.dropna(axis=1, how='all')

    cols_to_drop = df.columns[24:38].tolist() + ['bo']
    df = df.drop(columns=cols_to_drop, errors='ignore')

    df.to_csv(output_file, index=False, float_format="%.4f")
    return output_file

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            process_type = request.form['process_type']

            if process_type == 'process1':
                output_file = add_computed_columns(file_path)
            elif process_type == 'process2':
                output_file = process_csv(file_path, os.path.join(UPLOAD_FOLDER, f"2_{file.filename}"), ['total'])
            else:
                output_file = process_csv(file_path, os.path.join(UPLOAD_FOLDER, f"3_{file.filename}"), list(category_percentages.keys()) + [f"{key}_7.5" for key in category_percentages.keys()])

            return send_file(output_file, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
