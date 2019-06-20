# coding: utf-8
import py
import pyquery


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
