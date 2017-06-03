import os
import tempfile

from jinja2_webpack.utils import load_json


def test_load_dict():
    assert load_json({'a': 'b'})['a'] == 'b'


def test_load_fp():
    with tempfile.TemporaryFile(mode='w+') as fp:
        fp.write('{ "a": "b" }')
        fp.seek(0)
        assert load_json(fp)['a'] == 'b'


def test_load_filename():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as fp:
        fp.write('{ "a": "b" }')
        name = fp.name
    try:
        assert load_json(name)['a'] == 'b'
    finally:
        os.unlink(name)
