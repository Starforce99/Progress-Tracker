from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = '453b6e15f8f145250cd8ee16915d79b2af94a504721bab44'  # Required for session

# File to store tasks
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Define Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), default="other")
    priority = db.Column(db.String(20), default="medium")
    def __repr__(self):
        return f'<Task {self.name}>'

#Create Database Tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    filter_type = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'date')
    search_query = request.args.get('search', '')

    query = Task.query

    # Apply search filter if provided
    if search_query:
        query = query.filter(Task.name.contains(search_query))

    # Apply task status filter
    if filter_type == 'active':
        query = query.filter_by(completed=False)
    elif filter_type == 'completed':
        query = query.filter_by(completed=True)

    # Apply sorting
    if sort_by == 'date':
        query = query.order_by(Task.created_at)
    elif sort_by == 'name':
        query = query.order_by(Task.name)

    tasks = query.all()
    return render_template('index.html', tasks=tasks, filter=filter_type, sort=sort_by, search=search_query)

@app.route('/add', methods=['POST'])
def add():
    task_name = request.form.get('task_name')
    due_date = request.form.get('due_date')
    category = request.form.get('category','other')
    priority = request.form.get('priority','medium')

    new_task = Task(name=task_name, due_date=due_date,category=category,priority=priority)
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)