import os
import py
import pytest
import shutil
import tempfile


@pytest.fixture
def project_path(request, tmpdir):
    path = os.path.join(os.path.dirname(__file__), "demo-project")
    py.path.local(path).copy(tmpdir)
    return tmpdir


@pytest.fixture
def project(request, project_path):
    from lektor.project import Project
    prj = Project.from_path(project_path.strpath)
    assert prj is not None
    return prj


@pytest.fixture
def env(request, project):
    from lektor.environment import Environment
    return Environment(project)


@pytest.fixture
def pad(request, env):
    from lektor.db import Database
    return Database(env).new_pad()


def make_builder(request, pad):
    from lektor.builder import Builder

    out = tempfile.mkdtemp()
    b = Builder(pad, out)

    def cleanup():
        try:
            shutil.rmtree(out)
        except (OSError, IOError):
            pass

    request.addfinalizer(cleanup)
    return b


@pytest.fixture
def builder(request, pad):
    return make_builder(request, pad)
