import textwrap
from pathlib import Path

import pyquery


def test_rst(builder, capsys):
    failures = builder.build_all()
    (out, err) = capsys.readouterr()
    assert not failures
    assert out == ""
    assert err == ""
    dst = Path(builder.destination_path)
    index_html = pyquery.PyQuery(dst.joinpath("index.html").read_text("utf-8"))
    de_index_html = pyquery.PyQuery(dst.joinpath("de/index.html").read_text("utf-8"))
    for html in (index_html, de_index_html):
        pre_class = html("pre").attr["class"]
        assert "ini" in pre_class
        assert "literal-block" in pre_class
        link = html("a")
        assert link.attr["href"] == "http://example.com"
    assert index_html("a").text() == "Foo bar"
    assert de_index_html("a").text() == "Föö bär"


def test_config(builder, capsys, project_path):
    # first without config
    failures = builder.build_all()
    (out, err) = capsys.readouterr()
    assert not failures
    assert out == ""
    assert err == ""
    index_html_path = Path(builder.destination_path, "index.html")
    index_html = pyquery.PyQuery(index_html_path.read_text("utf-8"))
    assert index_html("h2").text() == "Underline title"
    # then with config
    configs = Path(project_path, "configs")
    configs.mkdir(exist_ok=True)
    ini_path = configs / "rst.ini"
    ini_path.write_text(
        textwrap.dedent("""\
        [docutils]
        writer = html5
        initial_header_level = 1
    """)
    )
    failures = builder.build_all()
    (out, err) = capsys.readouterr()
    assert not failures
    assert out == ""
    assert err == ""
    index_html = pyquery.PyQuery(index_html_path.read_text("utf-8"))
    assert index_html("h1").text() == "Underline title"
