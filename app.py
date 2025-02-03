from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.styles import PatternFill

app = Flask(__name__)
UPLOAD_FOLDER = os.path.abspath('uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

category_percentages = {
    'OC': 0.31, 'BC': 0.265, 'BCM': 0.035, 'MBC': 0.20,
    'SC': 0.15, 'SCA': 0.03, 'ST': 0.01
}

def round_to_sum(values):
    original_sum = round(sum(values))
    floored_values = [int(v) for v in values]
    floored_sum = sum(floored_values)
    difference = original_sum - floored_sum
    
    remainders = sorted(enumerate(values), key=lambda x: x[1] - floored_values[x[0]], reverse=True)
    for i in range(difference):
        floored_values[remainders[i][0]] += 1
    return floored_values

def add_computed_columns(input_file):
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.strip().str.lower()
    df['total'] = df['total'].astype(float)
    df['general'] = df['total'] * 0.925
    df['7.5% reservation'] = df['total'] * 0.075
    output_file = os.path.join(UPLOAD_FOLDER, "1_" + os.path.basename(input_file))
    df.to_csv(output_file, index=False)
    return output_file

def process_csv(input_file, output_file, column_names):
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.strip().str.lower()
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
    
    df.to_csv(output_file, index=False, float_format="%.4f")
    return output_file

def process_csv_to_excel(file_path, output_file):
    df = pd.read_csv(file_path)
    required_columns = {"7.5% reservation", "general", "total", "oc", "bc", "bcm", "mbc", "sc", "sca", "st", 
                        "oc_7.5", "bc_7.5", "bcm_7.5", "mbc_7.5", "sc_7.5", "sca_7.5", "st_7.5"}
    
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")
    
    df['general+7.5% reservation'] = df['7.5% reservation'] + df['general']
    df['General Sum'] = df[['oc', 'bc', 'bcm', 'mbc', 'sc', 'sca', 'st']].sum(axis=1)
    df['7.5% Reservation Sum'] = df[['oc_7.5', 'bc_7.5', 'bcm_7.5', 'mbc_7.5', 'sc_7.5', 'sca_7.5', 'st_7.5']].sum(axis=1)
    
    wb = Workbook()
    ws = wb.active
    ws.append(df.columns.tolist())
    for index, row in df.iterrows():
        ws.append(row.tolist())
    
    wb.save(output_file)
    return output_file

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part in the request."
        
        file = request.files['file']
        if file.filename == '':
            return "No file selected for uploading."
        
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        process_type = request.form['process_type']
        if process_type == 'process1':
            output_file = add_computed_columns(file_path)
        elif process_type == 'process2':
            output_file = process_csv(file_path, os.path.join(UPLOAD_FOLDER, f"2_{file.filename}"), ['total'])
        elif process_type == 'process3':
            output_file = process_csv(file_path, os.path.join(UPLOAD_FOLDER, f"3_{file.filename}"), list(category_percentages.keys()) + [f"{key}_7.5" for key in category_percentages.keys()])
        elif process_type == 'process4':
            output_file = process_csv_to_excel(file_path, os.path.join(UPLOAD_FOLDER, f"4_{file.filename}.xlsx"))
        else:
            return "Invalid process type."
        
        return send_file(output_file, as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
