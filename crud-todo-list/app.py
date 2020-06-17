from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os, json, sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class TodoList(db.Model):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    items = db.relationship('TodoItem', backref='list', lazy=True)
    completed = db.Column(db.Boolean, nullable=False, default=False, server_default="FALSE")

class TodoItem(db.Model):
    __tablename__ = 'todoitem'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolist.id'), nullable=False)

@app.route('/')
def todo_lists():
    """Index page, redirect to /lists/1"""
    return redirect(url_for("lists", list_id=1))

@app.route('/todo-list/<list_id>')
def lists(list_id):
    """Return lists, and items in list with list_id"""
    items = TodoItem.query.order_by('id').filter_by(list_id=list_id).all()
    lists = TodoList.query.order_by('id').all()
    return render_template("list.html", items=items, lists=lists, active_list_id=list_id)

@app.route('/todo-list/create', methods=["POST"])
def create_todo_list():
    """Create a new list"""
    try:
        data = request.get_json()
        new_list = TodoList(name=data['name'])
        db.session.add(new_list)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
    finally:
        db.session.close()
    return jsonify(data)

@app.route('/todo-list/<list_id>/delete', methods=["DELETE"])
def delete_todo_list(list_id):
    """Delete list with given id"""
    try:
        todo_list = TodoList.query.get(list_id)
        for todo in todo_list.items:
            db.session.delete(todo)
        db.session.delete(todo_list)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
    finally:
        db.session.close()
    return jsonify({'success': True})

@app.route('/todo-list/<list_id>/update', methods=["POST"])
def update_todo_list(list_id):
    """Update completed status of the list"""
    try:
        data = request.get_json()
        todo_list = TodoList.query.get(list_id)
        todo_list.completed = data['completed']
        for todo in todo_list.items:
            todo.completed = data['completed']
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
    finally:
        db.session.close()
    return jsonify(data)

@app.route('/todo-item/create', methods=["POST"])
def create():
    """Create a new todo item"""
    if request.method == 'POST':
        data = request.get_json()
        new_todo = TodoItem(description=data['description'], list_id=data['listId'])
        try:
            db.session.add(new_todo)
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())
            abort(500)
        finally:
            db.session.close()
        return jsonify(data)

@app.route('/todo-item/<todo_id>/update', methods=["POST"])
def update(todo_id):
    """Update list item as completed or not completed"""
    try:
        data = request.get_json()
        todo = TodoItem.query.get(todo_id)
        todo.completed = data['completed']
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
    finally:
        db.session.close()
    return jsonify(data)

@app.route('/todo-item/<todo_id>/delete', methods=['DELETE'])
def delete(todo_id):
    """Delete a todo item"""
    try:
        todo = TodoItem.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(500)
    finally:
        db.session.close()
    return jsonify({'success': True})