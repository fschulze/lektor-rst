import shutil
from pathlib import Path

import pytest
from lektor.builder import Builder
from lektor.db import Database
from lektor.environment import Environment
from lektor.project import Project


@pytest.fixture
def project_path(tmp_path):
    shutil.copytree(Path(__file__).parent / "demo-project", tmp_path / "project")
    return tmp_path / "project"


@pytest.fixture
def project(project_path):
    prj = Project.from_path(project_path)
    assert prj is not None
    return prj


@pytest.fixture
def env(project):
    return Environment(project)


@pytest.fixture
def pad(env):
    return Database(env).new_pad()


@pytest.fixture
def builder(tmp_path, pad):
    return Builder(pad, tmp_path / "output")
