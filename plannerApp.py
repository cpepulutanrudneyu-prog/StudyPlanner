from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)
CSV_FILE = 'smart_planner.csv'

def get_priority_metrics(deadline_str):
    """Smart Analysis: Calculates urgency and returns UI colors."""
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_left = (deadline - datetime.now()).days
        
        if days_left < 0:
            return "Overdue", "danger", 100 # High score for overdue
        elif days_left <= 1:
            return "Critical", "danger", 90
        elif days_left <= 3:
            return "Urgent", "warning", 60
        else:
            return "On Track", "success", 20
    except:
        return "Planned", "info", 0

def get_smart_insights(assignments):
    """Workload Balancing Logic: Analyzes all tasks to give advice."""
    urgent_tasks = [a for a in assignments if a['days_left'] <= 3 and a['days_left'] >= 0]
    count = len(urgent_tasks)
    
    if count >= 4:
        return "🔥 High Stress Detected: Break tasks into 15-minute chunks.", "danger"
    elif count >= 2:
        return "⚠️ Busy Week: Prioritize your 'Critical' assignments first.", "warning"
    elif len(assignments) > 0:
        return "✅ Balanced: Your schedule looks manageable.", "success"
    else:
        return "🌟 Clear Skies: Add your next goal to stay ahead!", "info"

def read_data():
    assignments = []
    study_plans = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Add Smart Metadata
                status, color, score = get_priority_metrics(row['date'])
                row['smart_status'] = status
                row['color_class'] = color
                row['priority_score'] = score
                row['days_left'] = (datetime.strptime(row['date'], '%Y-%m-%d') - datetime.now()).days
                
                if row['category'] == 'Assignment':
                    assignments.append(row)
                else:
                    study_plans.append(row)
    return assignments, study_plans

@app.route('/')
def index():
    assignments, study_plans = read_data()
    # Sort by Priority Score (Highest first)
    assignments.sort(key=lambda x: x['priority_score'], reverse=True)
    
    insight_msg, insight_color = get_smart_insights(assignments)
    
    return render_template('index.html', 
                           assignments=assignments, 
                           study_plans=study_plans, 
                           insight=insight_msg, 
                           insight_color=insight_color)

@app.route('/add', methods=['POST'])
def add():
    category = request.form.get('category')
    title = request.form.get('title')
    subject = request.form.get('subject')
    date = request.form.get('date')
    
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        fieldnames = ['category', 'title', 'subject', 'date']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()
        writer.writerow({'category': category, 'title': title, 'subject': subject, 'date': date})
    return redirect(url_for('index'))

@app.route('/delete/<category>/<int:index>')
def delete_item(category, index):
    all_rows = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r') as file:
            all_rows = list(csv.DictReader(file))
    
    cat_list = [i for i, row in enumerate(all_rows) if row['category'] == category]
    if index < len(cat_list):
        all_rows.pop(cat_list[index])
        
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['category', 'title', 'subject', 'date'])
        writer.writeheader()
        writer.writerows(all_rows)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, port=5000)