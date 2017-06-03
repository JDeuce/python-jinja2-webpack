import logging
import os
import runpy
import tempfile

import pytest
from jinja2.exceptions import TemplateError

from jinja2_webpack.scan import build_output, main, scan

HERE = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.DEBUG)


def _normpath(paths):
    # On Windows, convert forward slashes to backward slashes,
    # so we will reference the command line the proper way for the OS.
    return [os.path.normpath(path) for path in paths]


def _scan(directories, templates):
    directories = _normpath(directories)
    templates = _normpath(templates)
    return scan(
        reference_root=HERE,
        root=HERE,
        directories=directories,
        templates=templates)


def test_scan_single():
    assets = _scan(
        directories=['templates1/'],
        templates=['templates1/*.jinja2'])

    assert assets == ['test1']


def test_scan_multiple():
    assets = _scan(
        directories=['templates*'],
        templates=['template*/*.jinja2'])
    assert 'test1' in assets
    assert 'test2' in assets


def test_scan_relative():
    assets = _scan(
        directories=['templates*'],
        templates=['template*/*.jinja2'])
    assert os.path.join('templates2', 'test.png') in assets


def test_scan_invalid_throws_exception():
    with pytest.raises(TemplateError):
        _scan(
            directories=['invalid'],
            templates=['invalid/*.jinja2'])


def test_variable_to_filter():
    _scan(
        directories=['variable'],
        templates=['variable/*.jinja2'])


def test_build_output():
    assets = _scan(
        directories=['templates*'],
        templates=['template*/*.jinja2'])
    assert len(assets) >= 3

    with tempfile.TemporaryFile('w+') as fp:
        build_output(
            reference_root=HERE,
            assets=assets,
            outfile=fp)
        fp.seek(0)
        content = fp.read()

    assert 'require("./templates2/test.png")' in content


def test_main_file():
    try:
        with tempfile.NamedTemporaryFile(
                delete=False, dir=HERE) as fp:
            name = fp.name

        main([
            '--root', HERE,
            '--directories', os.path.join(HERE, 'templates*'),
            '--outfile', name,
            os.path.join('template*', '*.jinja2')
        ])

        with open(name) as fp:
            data = fp.read()
    finally:
        os.unlink(name)

    assert 'require("./templates2/test.png")' in data


def test_main_stdout(capsys):
    curdir = os.getcwd()
    try:
        os.chdir(HERE)

        main([
            '--root', HERE,
            '--directories', os.path.join(HERE, 'templates*'),
            '--',
            os.path.join('template*', '*.jinja2')
        ])

        data, _ = capsys.readouterr()

    finally:
        os.chdir(curdir)

    assert 'require("./templates2/test.png")' in data


def test_main_reference():
    try:
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            name = fp.name

        main([
            '--root', HERE,
            '--reference-root', os.path.join(HERE, '..'),
            '--directories', os.path.join(HERE, 'templates*'),
            '--outfile', name,
            os.path.join('template*', '*.jinja2')
        ])

        with open(name) as fp:
            data = fp.read()
    finally:
        os.unlink(name)

    assert 'require("./test_scan/templates2/test.png")' in data


def test_ifmain():
    runpy.run_module('jinja2_webpack.scan')
