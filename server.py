from flask import Flask, render_template, redirect, request
import subprocess

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Play with Friends → Runs friends.py
@app.route('/friends_mode', methods=['GET', 'POST'])
def friends_mode():
    if request.method == 'POST':
        subprocess.run(['python', 'friends.py'])  # Run friends.py
        return redirect('/')
    return render_template('friends_mode.html')

# Play with Computer → Show Mode Selection
@app.route('/computer_mode')
def computer_mode():
    return render_template('computer_mode.html')

# Classical Mode → Runs classical.py
@app.route('/run_classical', methods=['POST'])
def run_classical():
    subprocess.run(['python', 'classical.py'])  # Run classical.py
    return redirect('/')

# Enemy Easy Mode → Runs easy_mode.py
@app.route('/run_easy_mode', methods=['POST'])
def run_easy_mode():
    subprocess.run(['python', 'easy_mode.py'])  # Run easy_mode.py
    return redirect('/')

# Enemy Hard Mode → Runs hard_mode.py
@app.route('/run_hard_mode', methods=['POST'])
def run_hard_mode():
    subprocess.run(['python', 'hard_mode.py'])  # Run hard_mode.py
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
