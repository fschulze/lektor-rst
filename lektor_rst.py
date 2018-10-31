# -*- coding: utf-8 -*-
from io import StringIO
from lektor.context import get_ctx
from lektor.pluginsystem import Plugin
from lektor.types import Type
from lxml import etree
from markupsafe import Markup
from weakref import ref as weakref
import datetime
import docutils.core
import docutils.writers.html4css1


def rst_to_html(text, extra_params, record):
    ctx = get_ctx()
    if ctx is None:
        raise RuntimeError('Context is required for markdown rendering')

    pub = docutils.core.Publisher(
        destination_class=docutils.io.StringOutput)
    pub.set_components('standalone', 'restructuredtext', 'html')
    pub.process_programmatic_settings(None, extra_params, None)
    pub.set_source(
        source=StringIO(text),
        source_path=record.source_filename if record is not None else None)
    pub.publish()

    metadata = {}
    for docinfo in pub.document.traverse(docutils.nodes.docinfo):
        for element in docinfo.children:
            if element.tagname == 'field':
                name_elem, body_elem = element.children
                name = name_elem.astext()
                value = body_elem.astext()
            else:
                name = element.tagname
                value = element.astext()
            name = name.lower()
            if name == 'date':
                value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M")
            metadata[name] = value

    parts = pub.writer.parts
    body = parts['html_title'] + parts['html_subtitle'] + parts['fragment']

    return body, metadata


def clean_rst(text, border=True, colgroup=True, valign=True, th_head=True,
              section=True, docutils=True):
    root = etree.HTML(text.html)
    body = root.xpath('/html/body')[0]

    if border:
        # remove border attributes from table elements
        for node in body.xpath('//table[@border]'):
            del node.attrib['border']

    if colgroup:
        # remove colgroup elements
        for node in body.xpath('//table/colgroup'):
            node.getparent().remove(node)

    if valign:
        # remove valign attributes
        for node in body.xpath('//*[@valign]'):
            del node.attrib['valign']

    if th_head:
        # remove head class from th elements
        for node in body.xpath('//th[@class="head"]'):
            del node.attrib['class']

    if section:
        # convert section divs into section elements
        for node in body.xpath('//div[@class="section"]'):
            node.tag = "section"

    if docutils:
        # remove docutils classes
        for node in body.xpath('//div[contains(@class, "docutils container")]'):
            classes = node.attrib['class'].replace('docutils container', '').strip()
            if not classes:
                del node.attrib['class']
            else:
                node.attrib['class'] = classes
        for node in body.xpath('//*[contains(@class, "docutils")]'):
            classes = node.attrib['class'].replace('docutils', '').strip()
            if not classes:
                del node.attrib['class']
            else:
                node.attrib['class'] = classes

    cleaned = StringIO()
    for child in body:
        cleaned.write(etree.tostring(child, encoding='unicode', method='html',
                      pretty_print=True))
    return Markup(cleaned.getvalue())


class Rst(object):
    def __init__(self, source, extra_params, record):
        self.source = source
        self.extra_params = extra_params
        self.__record = weakref(record) if record is not None else lambda: None
        self.__cached_for_ctx = None
        self.__html = None
        self.__meta = None
        
    def __bool__(self):
        return bool(self.source)

    def __nonzero__(self):
        return bool(self.source)

    def __render(self):
        # When the markdown instance is attached to a cached object we can
        # end up in the situation where the context changed from the time
        # we were put into the cache to the time where we got referenced
        # by something elsewhere.  In that case we need to re-process our
        # markdown.  For instance this affects relative links.
        if self.__html is None or \
           self.__cached_for_ctx != get_ctx():
            self.__html, self.__meta = rst_to_html(
                self.source, self.extra_params, self.__record())
            self.__cached_for_ctx = get_ctx()

    @property
    def meta(self):
        self.__render()
        return self.__meta

    @property
    def html(self):
        self.__render()
        return Markup(self.__html)

    def __getitem__(self, name):
        return self.meta[name]

    def __unicode__(self):
        self.__render()
        return self.__html

    def __html__(self):
        self.__render()
        return Markup(self.__html)


class RstDescriptor(object):
    def __init__(self, source, extra_params):
        self.source = source
        self.extra_params = extra_params

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return Rst(self.source, self.extra_params, obj)


class RstType(Type):
    widget = 'multiline-text'

    def __init__(self, env, options):
        Type.__init__(self, env, options)
        self.extra_params = {
            'doctitle_xform': False,
            'initial_header_level': '2',
            'syntax_highlight': 'short'}
        self.extra_params.update(options)

    def value_from_raw(self, raw):
        return RstDescriptor(raw.value or u'', self.extra_params)


class RstPlugin(Plugin):
    name = "reStructuredText"
    description = "Adds reStructuredText support"

    def on_setup_env(self, **extra):
        self.env.types['rst'] = RstType
        self.env.jinja_env.filters['cleanrst'] = clean_rst
