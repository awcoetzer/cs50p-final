import pytest
from app import main


@pytest.fixture
def app_fixture():
    app = main()
    app.config['TESTING'] = True
    app.config['MONGODB_URI'] = 'mongodb://localhost:27017/test_database'
    return app


@pytest.fixture
def client(app_fixture):
    return app_fixture.test_client()
