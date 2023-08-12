from flask import Flask, render_template, request, session, redirect
import pandas as pd
import json
import io
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Sample user data for demonstration (replace with secure methods)
users = {
    'Demo': generate_password_hash('1234'),
    'demo': generate_password_hash('1234')
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        if request.method == 'POST':
            file = request.files.get('csvfile')
            if file:
                session['csvfile'] = file.read().decode('utf-8')
                df = pd.read_csv(io.StringIO(session['csvfile']))
                headers = list(df.columns)
                return render_template('select.html', headers=headers)
            else:
                return render_template('index.html', error_message='No file selected.')
        return render_template('index.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error_message='Invalid credentials.')

    return render_template('login.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    param1 = request.form['param1']
    param2 = request.form['param2']
    csvfile = session['csvfile']
    df = pd.read_csv(io.StringIO(csvfile))
    df_cleaned = df[[param1, param2]].dropna()
    mean_value = df_cleaned[param2].mean()
    median_value = df_cleaned[param2].median()
    std_deviation = df_cleaned[param2].std()
    
    chart_data = {
        'labels': df_cleaned[param1].tolist(),
        'datasets': [{
            'label': param2,
            'data': df_cleaned[param2].tolist(),
            'backgroundColor': 'bg-blue-500 bg-opacity-50',
            'borderColor': 'border-blue-500',
            'borderWidth': 1
        }]
    }
    chart_data = json.dumps(chart_data)
    headers = list(df.columns)
    return render_template('select.html', headers=headers, chart_data=chart_data,
                           mean_value=mean_value, median_value=median_value, std_deviation=std_deviation)



if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
