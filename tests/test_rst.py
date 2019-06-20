# coding: utf-8
import py
import pyquery
import textwrap


def test_rst(builder, capsys):
    failures = builder.build_all()
    (out, err) = capsys.readouterr()
    assert not failures
    assert out == ''
    assert err == ''
    dst = py.path.local(builder.destination_path)
    index_html = pyquery.PyQuery(
        dst.join('index.html').read_text('utf-8'))
    de_index_html = pyquery.PyQuery(
        dst.join('de/index.html').read_text('utf-8'))
    for html in (index_html, de_index_html):
        pre_class = html('pre').attr['class']
        assert 'ini' in pre_class
        assert 'literal-block' in pre_class
        link = html('a')
        assert link.attr['href'] == 'http://example.com'
    assert index_html('a').text() == u'Foo bar'
    assert de_index_html('a').text() == u'Föö bär'


def test_config(builder, capsys, project_path):
    # first without config
    failures = builder.build_all()
    (out, err) = capsys.readouterr()
    assert not failures
    assert out == ''
    assert err == ''
    dst = py.path.local(builder.destination_path)
    index_html = pyquery.PyQuery(
        dst.join('index.html').read_text('utf-8'))
    assert index_html('h2').text() == 'Underline title'
    # then with config
    configs = project_path.join('configs').ensure_dir()
    configs.join('rst.ini').write(textwrap.dedent("""\
        [docutils]
        writer = html5
        initial_header_level = 1
    """))
    failures = builder.build_all()
    (out, err) = capsys.readouterr()
    assert not failures
    assert out == ''
    assert err == ''
    dst = py.path.local(builder.destination_path)
    index_html = pyquery.PyQuery(
        dst.join('index.html').read_text('utf-8'))
    assert index_html('h1').text() == 'Underline title'
