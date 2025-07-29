import pytest
from flask import Flask
from flask_quill import Quill

@pytest.fixture
def app():
    app = Flask(__name__)
    return app

def test_quill_init_app(app):
    quill = Quill()
    quill.init_app(app)
    assert 'quill' in app.jinja_env.globals

def test_quill_load():
    quill = Quill()
    html = quill.load()
    assert 'quill.js' in html
    assert 'quill.snow.css' in html

def test_quill_create_editor():
    quill = Quill()
    html = quill.create_editor('testfield')
    assert 'testfield' in html
    assert 'Quill' in html

def test_quill_config():
    quill = Quill()
    html = quill.config('mytextarea')
    assert 'mytextarea' in html
    assert 'Quill' in html 