import pytest
from flask_quill.fields import QuillField
from wtforms import Form

class SampleForm(Form):
    content = QuillField('Content')

def test_quillfield_render():
    form = SampleForm()
    html = form.content()
    assert 'textarea' in html