import pytest
from app import main, get_current_date, get_todos, get_completed
from bson import ObjectId
from conftest import app_fixture

def test_index(client, app_fixture):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Todo Juggler Home' in response.data


def test_about(client, app_fixture):
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About Todo Juggler' in response.data

# The below test has no function, but is located within the main() function. 
# This is just data being added to the database
def test_add_todo_to_database(client, app_fixture):
    # Use the test database URI in the app configuration
    app_fixture.config['MONGODB_URI'] = 'mongodb://localhost:27017/test_database'

    response = client.post(
        '/', data={'heading': 'PyTest Heading', 'todo': 'PyTest Todo'})
    assert response.status_code == 302

    # Check if the data was added to the test database
    added_data = app_fixture.db.todo.find_one({'heading': 'PyTest Heading'})
    assert added_data is not None
    assert added_data['todo'] == 'PyTest Todo'

# test_complete is located within the main() function as its own function
def test_complete(client, app_fixture):
    # Use the test database URI in the app configuration
    app_fixture.config['MONGODB_URI'] = 'mongodb://localhost:27017/test_database'

    # Adding a test todo to the database
    test_todo = {
        'entry_date': 'PyTest Entry Date',
        'completion_date': 'PyTest Completion',
        'heading': 'PyTest Heading',
        'todo': 'PyTest Todo',
    }
    app_fixture.db.todo.insert_one(test_todo)

    # Getting the ID of the test todo created
    todo_id = app_fixture.db.todo.find_one({'heading': 'PyTest Heading'})['_id']

    # Moving the test todo to the 'completed' collection
    with app_fixture.app_context():
        response = client.post(f'/complete/{str(todo_id)}')
        assert response.status_code == 302

        # Check if the todo was added to the 'completed' collection
        completed_todo = app_fixture.db.completed.find_one({'_id': ObjectId(todo_id)})
        assert completed_todo is not None


def test_get_current_date(app_fixture):
    with app_fixture.app_context():
        date = get_current_date()
        assert isinstance(date, str)

def test_get_todos(app_fixture):
    with app_fixture.app_context():
        todos = get_todos(app_fixture)
        assert isinstance(todos, list)

def test_get_completed(app_fixture):
    with app_fixture.app_context():
        completed = get_completed(app_fixture)
        assert isinstance(completed, list)
