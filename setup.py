from setuptools import setup


setup(
    name='lektor-rst',
    description='Adds reStructuredText support to Lektor.',
    version='0.3.0',
    author=u'Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='http://github.com/fschulze/lektor-rst',
    license='MIT',
    install_requires=[
        'Lektor',
        'Pygments',
        'docutils'],
    extras_require={
        'dev': [
            'pyquery',
            'pytest',
            'pytest-cov',
            'pytest-flake8']},
    py_modules=['lektor_rst'],
    python_requires=">=3.7",
    entry_points={
        'lektor.plugins': [
            'rst = lektor_rst:RstPlugin']})
