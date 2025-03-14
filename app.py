from flask import Flask, render_template, request, redirect, url_for, session
import boto3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# AWS DynamoDB Configuration
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
users_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'CollegeUsers'))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    response = users_table.get_item(Key={'email': email})
    user = response.get('Item')
    
    if user and check_password_hash(user['password'], password):
        session['user'] = user['email']
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid Credentials, try again!'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        users_table.put_item(Item={'email': email, 'password': password})
        return redirect(url_for('home'))
    
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
