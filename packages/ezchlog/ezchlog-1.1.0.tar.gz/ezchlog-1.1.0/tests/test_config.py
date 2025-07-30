from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

from ezchlog.config import Config


@patch('ezchlog.config.Config.root_dir', new_callable=PropertyMock)
@patch('ezchlog.config.Config.pyproject', new_callable=PropertyMock)
@patch('ezchlog.config.Config.ezchlogconf', new_callable=PropertyMock)
@patch('ezchlog.config.Config.editorconfig', new_callable=PropertyMock)
@patch('ezchlog.config.Config.git_dir', new_callable=PropertyMock)
@patch('ezchlog.config.environ', new_callable=dict)
def test_config_init_no_conf(environ, git_dir, editorconfig, ezchlogconf, pyproject, root_dir) -> None:
    root_path = Path('/some/root/project')
    git_dir.return_value = root_path
    editorconfig.return_value = None
    ezchlogconf.return_value = None
    pyproject.return_value = None
    root_dir.return_value = root_path
    cfg = Config()
    assert cfg.log_file == root_path / 'CHANGELOG.md'
    assert cfg.log_dir == root_path / '_CHANGELOGS'
    assert cfg.category_list == [
        'Security',
        'Fixed',
        'Changed',
        'Added',
        'Removed',
        'Deprecated',
    ]
    assert cfg.category_default == 'Changed'
    assert (
        cfg.default_changelog
        == """\
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).
"""
    )
    assert not cfg.no_git
    assert cfg.branch_format == "%{ref}%{sep}%{name}"
    assert cfg.branch_separator == "_"
    assert cfg.branch_lowercase_for == ['cat', 'name']


@patch('ezchlog.config.Config.root_dir', new_callable=PropertyMock)
@patch('ezchlog.config.Config.pyproject', new_callable=PropertyMock)
@patch('ezchlog.config.Config.ezchlogconf', new_callable=PropertyMock)
@patch('ezchlog.config.Config.editorconfig', new_callable=PropertyMock)
@patch('ezchlog.config.Config.git_dir', new_callable=PropertyMock)
@patch('ezchlog.config.environ', new_callable=dict)
def test_config_init_conf_vars(environ, git_dir, editorconfig, ezchlogconf, pyproject, root_dir) -> None:
    environ.update(
        {
            'EZCHLOG_LOG_FILE': 'changelogs.md',
            'EZCHLOG_LOG_DIR': '.changelogs',
            'EZCHLOG_CATEGORY_LIST': 'add,fix,chore',
            'EZCHLOG_CATEGORY_DEFAULT': 'chore',
            'EZCHLOG_DEFAULT_CHANGELOG': '# Changelogs\nChanges:\n',
            'EZCHLOG_NO_GIT': 'true',
            'EZCHLOG_BRANCH_FORMAT': '%{ref}%{sep}%{cat}%{sep}%{name}',
            'EZCHLOG_BRANCH_SEPARATOR': '-',
            'EZCHLOG_BRANCH_LOWERCASE_FOR': 'ref,name',
        }
    )
    root_path = Path('/some/root/project')
    git_dir.return_value = root_path
    editorconfig.return_value = None
    ezchlogconf.return_value = None
    pyproject.return_value = None
    root_dir.return_value = root_path
    cfg = Config()
    assert cfg.log_file == root_path / 'changelogs.md'
    assert cfg.log_dir == root_path / '.changelogs'
    assert cfg.category_list == ['add', 'fix', 'chore']
    assert cfg.category_default == 'chore'
    assert cfg.default_changelog == '# Changelogs\nChanges:\n'
    assert cfg.no_git
    assert cfg.branch_format == '%{ref}%{sep}%{cat}%{sep}%{name}'
    assert cfg.branch_separator == '-'
    assert cfg.branch_lowercase_for == ['ref', 'name']


@patch('ezchlog.config.Config.root_dir', new_callable=PropertyMock)
@patch('ezchlog.config.Config.pyproject', new_callable=PropertyMock)
@patch('ezchlog.config.Config.ezchlogconf', new_callable=PropertyMock)
@patch('ezchlog.config.Config.editorconfig', new_callable=PropertyMock)
@patch('ezchlog.config.Config.git_dir', new_callable=PropertyMock)
@patch('ezchlog.config.Path.cwd')
@patch('ezchlog.config.environ', new_callable=dict)
def test_config_init_conf_ezchlog(environ, cwd, git_dir, editorconfig, ezchlogconf, pyproject, root_dir, tmp_path) -> None:
    cwd.return_value = tmp_path
    git_dir.return_value = tmp_path
    editorconfig.return_value = None
    cfg_toml = '''
log_file = "changelogs.md"
log_dir = ".changelogs"
category_list = ["add", "fix", "chore"]
category_default = "chore"
default_changelog = """
# Changelogs
Changes:
"""
no_git = true
branch_format = "%{ref}%{sep}%{cat}%{sep}%{name}"
branch_separator = "-"
branch_lowercase_for = ["ref", "name"]
'''
    (tmp_path / '.ezchlog.toml').write_text(cfg_toml, encoding='utf-8')
    ezchlogconf.return_value = tmp_path / '.ezchlog.toml'
    pyproject.return_value = None
    root_dir.return_value = tmp_path
    cfg = Config()
    assert cfg.log_file == tmp_path / 'changelogs.md'
    assert cfg.log_dir == tmp_path / '.changelogs'
    assert cfg.category_list == ['add', 'fix', 'chore']
    assert cfg.category_default == 'chore'
    assert cfg.default_changelog == '# Changelogs\nChanges:\n'
    assert cfg.no_git
    assert cfg.branch_format == '%{ref}%{sep}%{cat}%{sep}%{name}'
    assert cfg.branch_separator == '-'
    assert cfg.branch_lowercase_for == ['ref', 'name']


@patch('ezchlog.config.Config.root_dir', new_callable=PropertyMock)
@patch('ezchlog.config.Config.pyproject', new_callable=PropertyMock)
@patch('ezchlog.config.Config.ezchlogconf', new_callable=PropertyMock)
@patch('ezchlog.config.Config.editorconfig', new_callable=PropertyMock)
@patch('ezchlog.config.Config.git_dir', new_callable=PropertyMock)
@patch('ezchlog.config.Path.cwd')
@patch('ezchlog.config.environ', new_callable=dict)
def test_config_init_conf_pyproject(environ, cwd, git_dir, editorconfig, ezchlogconf, pyproject, root_dir, tmp_path) -> None:
    cwd.return_value = tmp_path
    git_dir.return_value = tmp_path
    editorconfig.return_value = None
    cfg_toml = '''
[tool.ezchlog]
log_file = "changelogs.md"
log_dir = ".changelogs"
category_list = ["add", "fix", "chore"]
category_default = "chore"
default_changelog = """
# Changelogs
Changes:
"""
no_git = true
branch_format = "%{ref}%{sep}%{cat}%{sep}%{name}"
branch_separator = "-"
branch_lowercase_for = ["ref", "name"]
'''
    ezchlogconf.return_value = None
    (tmp_path / 'pyproject.toml').write_text(cfg_toml, encoding='utf-8')
    pyproject.return_value = tmp_path / 'pyproject.toml'
    root_dir.return_value = tmp_path
    cfg = Config()
    assert cfg.log_file == tmp_path / 'changelogs.md'
    assert cfg.log_dir == tmp_path / '.changelogs'
    assert cfg.category_list == ['add', 'fix', 'chore']
    assert cfg.category_default == 'chore'
    assert cfg.default_changelog == '# Changelogs\nChanges:\n'
    assert cfg.no_git
    assert cfg.branch_format == '%{ref}%{sep}%{cat}%{sep}%{name}'
    assert cfg.branch_separator == '-'
    assert cfg.branch_lowercase_for == ['ref', 'name']


def test_ezchlogconf_none(tmp_path) -> None:
    cfg = MagicMock(curr_dir=tmp_path)
    ezchlogconf_func = Config.ezchlogconf.func  # type: ignore
    assert ezchlogconf_func(self=cfg) is None


def test_ezchlogconf_path(tmp_path) -> None:
    subdir = tmp_path / 'sub1' / 'sub2' / 'sub3'
    subdir.mkdir(parents=True)
    cfg_path = tmp_path / 'sub1' / '.ezchlog.toml'
    cfg_path.touch()
    cfg = MagicMock(curr_dir=subdir)
    ezchlogconf_func = Config.ezchlogconf.func  # type: ignore
    assert ezchlogconf_func(self=cfg) == cfg_path


def test_pyproject_none(tmp_path) -> None:
    cfg = MagicMock(curr_dir=tmp_path)
    pyproject_func = Config.pyproject.func  # type: ignore
    assert pyproject_func(self=cfg) is None


def test_pyproject_path(tmp_path) -> None:
    subdir = tmp_path / 'sub1' / 'sub2' / 'sub3'
    subdir.mkdir(parents=True)
    cfg_path = tmp_path / 'sub1' / 'pyproject.toml'
    cfg_path.touch()
    cfg = MagicMock(curr_dir=subdir)
    pyproject_func = Config.pyproject.func  # type: ignore
    assert pyproject_func(self=cfg) == cfg_path


def test_editorconfig_none(tmp_path) -> None:
    cfg = MagicMock(curr_dir=tmp_path)
    git_dir_func = Config.git_dir.func  # type: ignore
    assert git_dir_func(self=cfg) is None


def test_editorconfig_path(tmp_path) -> None:
    subdir = tmp_path / 'sub1' / 'sub2' / 'sub3'
    subdir.mkdir(parents=True)
    editorconfig_path = tmp_path / 'sub1' / '.editorconfig'
    editorconfig_path.touch()
    cfg = MagicMock(curr_dir=subdir)
    editorconfig_func = Config.editorconfig.func  # type: ignore
    assert editorconfig_func(self=cfg) == editorconfig_path


def test_git_dir_none(tmp_path) -> None:
    cfg = MagicMock(curr_dir=tmp_path)
    editorconfig_func = Config.editorconfig.func  # type: ignore
    assert editorconfig_func(self=cfg) is None


def test_git_dir_path(tmp_path) -> None:
    subdir = tmp_path / 'sub1' / 'sub2' / 'sub3'
    subdir.mkdir(parents=True)
    git_path = tmp_path / 'sub1' / '.git'
    git_path.mkdir()
    cfg = MagicMock(curr_dir=subdir)
    git_dir_func = Config.git_dir.func  # type: ignore
    assert git_dir_func(self=cfg) == git_path


def test_root_dir_curr_dir(tmp_path) -> None:
    cfg = MagicMock(
        curr_dir=tmp_path,
        ezchlogconf=None,
        pyproject=None,
        editorconfig=None,
        git_dir=None,
    )
    root_dir_func = Config.root_dir.func  # type: ignore
    assert root_dir_func(self=cfg) == tmp_path


def test_root_dir_pyproject_dir(tmp_path) -> None:
    cfg = MagicMock(
        curr_dir=tmp_path,
        ezchlogconf=None,
        pyproject=tmp_path / 'project' / 'pyproject.toml',
        editorconfig=None,
        git_dir=None,
    )
    root_dir_func = Config.root_dir.func  # type: ignore
    assert root_dir_func(self=cfg) == tmp_path / 'project'


def test_category_class() -> None:
    cfg = MagicMock(category_list=['toto', 'titi'])
    category_class_func = Config.category_class.func  # type: ignore
    category_class = category_class_func(self=cfg)
    assert [c.name for c in category_class] == ['toto', 'titi']


@patch('ezchlog.config.Config.pyproject', new_callable=PropertyMock)
@patch('ezchlog.config.Config.ezchlogconf', new_callable=PropertyMock)
@patch('ezchlog.config.Config.editorconfig', new_callable=PropertyMock)
@patch('ezchlog.config.Config.git_dir', new_callable=PropertyMock)
@patch('ezchlog.config.Path.cwd')
@patch('ezchlog.config.environ', new_callable=dict)
def test_iterable(environ, cwd, git_dir, editorconfig, ezchlogconf, pyproject, tmp_path) -> None:
    environ.update(
        {
            'EZCHLOG_LOG_FILE': 'changelogs.md',
            'EZCHLOG_LOG_DIR': '.changelogs',
            'EZCHLOG_CATEGORY_LIST': 'add,fix,chore',
            'EZCHLOG_CATEGORY_DEFAULT': 'chore',
            'EZCHLOG_DEFAULT_CHANGELOG': '# Changelogs\nChanges:\n',
            'EZCHLOG_NO_GIT': '1',
            'EZCHLOG_BRANCH_FORMAT': '%{ref}%{sep}%{cat}%{sep}%{name}',
            'EZCHLOG_BRANCH_SEPARATOR': '-',
            'EZCHLOG_BRANCH_LOWERCASE_FOR': 'ref,name',
        }
    )
    cwd.return_value = tmp_path
    git_dir.return_value = None
    editorconfig.return_value = None
    ezchlogconf.return_value = None
    pyproject.return_value = None
    cfg = Config()
    cfg_dict = dict(cfg)
    assert cfg_dict == dict(
        log_dir=str(tmp_path / '.changelogs'),
        log_file=str(tmp_path / 'changelogs.md'),
        category_list=['add', 'fix', 'chore'],
        category_default='chore',
        default_changelog='# Changelogs\nChanges:\n',
        no_git=True,
        branch_format='%{ref}%{sep}%{cat}%{sep}%{name}',
        branch_separator='-',
        branch_lowercase_for=['ref', 'name'],
    )
