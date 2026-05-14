from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)
CSV_FILE = 'assignments.csv'

# Helper function to read assignments
def read_assignments():
    assignments = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                assignments.append(row)
    return assignments


# Helper function to add an assignment
def write_assignment(title, subject, deadline):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        fieldnames = ['title', 'subject', 'deadline', 'status']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'title': title, 
            'subject': subject, 
            'deadline': deadline, 
            'status': 'Pending'
        })



@app.route('/')
def index():
    tasks = read_assignments()
    # "Smart" sorting: nearest deadline first
    tasks.sort(key=lambda x: x['deadline']) 
    return render_template('index.html', assignments=tasks)



@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    subject = request.form.get('subject')
    deadline = request.form.get('deadline')
    write_assignment(title, subject, deadline)
    return redirect(url_for('index'))


@app.route('/delete/<int:task_index>')
def delete_task(task_index):
    tasks = read_assignments()
    
    # Check if the index is valid
    if 0 <= task_index < len(tasks):
        # Remove the item from the list
        tasks.pop(task_index)
        
        # Rewrite the entire CSV file with the remaining tasks
        with open(CSV_FILE, mode='w', newline='') as file:
            fieldnames = ['title', 'subject', 'deadline', 'status']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tasks)
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)