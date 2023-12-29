import os
import datetime
from flask import (Flask, render_template, request,
                   redirect, url_for)
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()


def main():
    app = Flask(__name__, static_folder='assets')
    client = MongoClient(os.getenv('MONGODB_URI'))
    app.db = client.todos

    @app.route('/', methods=['GET', 'POST'])
    def index():
        page_title = 'Todo Juggler Home'
        if request.method == 'POST':
            heading = request.form.get('heading')
            todo = request.form.get('todo')

            app.db.todo.insert_one({
                'entry_date': get_current_date(),
                'completion_date': '',
                'heading': heading,
                'todo': todo,
            })
            return redirect(url_for('index'))
        
        return render_template('index.html', 
                               page_title=page_title, get_todos=get_todos(app), get_completed=get_completed(app))
    
    @app.route('/about')
    def about():
        page_title = 'About Todo Juggler'
        return render_template('about.html', 
                               page_title=page_title)
    
    @app.route('/remove_from_todo/<todo_id>', methods=['POST'])
    def remove_from_todo(todo_id):
        remove = app.db.todo.delete_one({'_id': ObjectId(todo_id)})
        return redirect(url_for('index'))
    
    @app.route('/remove_from_complete/<complete_id>', methods=['POST'])
    def remove_from_complete(complete_id):
        remove = app.db.completed.delete_one({'_id': ObjectId(complete_id)})
        return redirect(url_for('index'))

    @app.route('/complete/<todo_id>', methods=['POST'])
    def complete(todo_id):
        completed_todo = app.db.todo.find_one({'_id': ObjectId(todo_id)})
        completion_date = get_current_date()
        completed_todo['completion_date'] = completion_date
        if completed_todo:
            remove_completed_todo = app.db.todo.delete_one({'_id': ObjectId(todo_id)})
            place_completed_todo = app.db.completed.insert_one(completed_todo)
        return redirect(url_for('index'))

    @app.errorhandler(404)
    def page_not_found(e):
        page_title = 'Page Not Found'
        return render_template('page_not_found.html',
                               page_title=page_title), 404

    return app

app = main()

def get_current_date():
    return datetime.datetime.today().strftime('%Y-%m-%d')

def get_todos(app):
    todos = [
        (
            todo['entry_date'],
            todo['completion_date'],
            todo['heading'],
            todo['todo'],
            todo['_id']
        )
        for todo in app.db.todo.find({})
    ]
    todos.reverse()
    print(todos)
    return todos

def get_completed(app):
    completed = [
        (
            complete['entry_date'],
            complete['completion_date'],
            complete['heading'],
            complete['todo'],
            complete['_id']
        )
        for complete in app.db.completed.find({})
    ]
    completed.reverse()
    print(completed)
    return completed

if __name__ == '__main__':
    app.run(debug=True)
