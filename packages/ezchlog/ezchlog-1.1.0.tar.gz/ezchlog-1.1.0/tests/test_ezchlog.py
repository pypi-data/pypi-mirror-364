from enum import Enum
from enum import EnumMeta
from pathlib import Path
from subprocess import run
from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture
from pytest import raises

from ezchlog.ezchlog import EzChLog


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_init(config_class) -> None:
    cfg = config_class()
    ezchlog = EzChLog()
    assert ezchlog.cfg == cfg


def test_ezchlog_get_slug() -> None:
    assert EzChLog.get_slug('test') == 'test'
    assert (
        EzChLog.get_slug(
            '(a simple)  message w!th accented letter$: « Café », symbols and too long',
        )
        == 'a_simple_message_wth_accented_letter_cafe_symbols'
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_add_simple(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
        branch_format='%{ref}%{sep}%{name}',
        branch_separator='_',
        branch_lowercase_for=['cat', 'name'],
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    cat = MagicMock()
    cat.name = 'changed'
    log_file, msg = ezchlog.add(dry_run=False, message="- simple message", cat=cat, ref="", create_branch=False, add_to_index=False)
    assert Path('logs') / log_file == Path() / 'logs' / 'changed' / 'simple_message.md'
    assert msg == "- simple message"
    content = (tmp_path / 'logs' / log_file).read_text(encoding='utf-8')
    assert content == "- simple message\n"
    assert (
        run(
            'git diff --staged --name-only'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == ''
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_add_complex(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
        branch_format='%{ref}%{sep}%{name}',
        branch_separator='_',
        branch_lowercase_for=['cat', 'name'],
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    cat = MagicMock()
    cat.name = 'changed'
    log_file, msg = ezchlog.add(dry_run=False, message="complex message\nwith\nother\nlines", cat=cat, ref="42", create_branch=True, add_to_index=True)
    assert Path('logs') / log_file == Path() / 'logs' / 'changed' / '42-complex_message.md'
    assert msg == "- complex message (42)  \nwith  \nother  \nlines"
    content = (tmp_path / 'logs' / log_file).read_text(encoding='utf-8')
    assert content == "- complex message (42)  \nwith  \nother  \nlines\n"
    assert (
        run(
            'git symbolic-ref --quiet HEAD'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == 'refs/heads/42_complex_message\n'
    )
    assert (
        run(
            'git diff --staged --name-only'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == 'logs/changed/42-complex_message.md\n'
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_commit_no_partlog(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    with raises(ValueError, match="No part log file found. Cannot commit for you, use `add` first."):
        ezchlog.commit(dry_run=False, partlog_path=None)
    assert (
        run(
            'git log --pretty=tformat:%s --all -1'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == ''
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_commit_partlog_is_not_new(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    (tmp_path / 'logs' / 'add').mkdir(parents=True)
    (tmp_path / 'logs' / 'add' / 'toto.md').write_text("- toto content", encoding='utf-8')
    run('git add logs/add/toto.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    run('git commit -m first'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    partlog_path = str(tmp_path / 'logs' / 'add' / 'toto.md')
    with raises(ValueError, match=f"{partlog_path} is not amongst added part log files."):
        ezchlog.commit(dry_run=False, partlog_path=partlog_path)
    assert (
        run(
            'git log --pretty=tformat:%s --all -1'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == 'first\n'
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_commit_partlog_too_many(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    (tmp_path / 'logs' / 'add').mkdir(parents=True)
    (tmp_path / 'logs' / 'add' / 'toto.md').write_text("- toto content", encoding='utf-8')
    (tmp_path / 'logs' / 'add' / 'a_test.md').write_text("- test content", encoding='utf-8')
    run('git add logs/add/toto.md logs/add/a_test.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    with raises(ValueError, match="Multiple part log files found. Please specify which one is primary as command line paramater."):
        ezchlog.commit(dry_run=False, partlog_path=None)
    assert (
        run(
            'git log --pretty=tformat:%s --all -1'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == ''
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_commit_partlog_one_but_not_in_index(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    (tmp_path / 'logs' / 'add').mkdir(parents=True)
    (tmp_path / 'logs' / 'add' / 'toto.md').write_text("- toto content", encoding='utf-8')
    ezchlog = EzChLog()
    with raises(ValueError, match="No part log file found. Cannot commit for you, use `add` first."):
        ezchlog.commit(dry_run=False, partlog_path=None)
    assert (
        run(
            'git log --pretty=tformat:%s --all -1'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == ''
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_commit_partlog_one_but_removed_from_index(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    (tmp_path / 'logs' / 'add').mkdir(parents=True)
    (tmp_path / 'logs' / 'add' / 'toto.md').write_text("- toto content", encoding='utf-8')
    run('git add logs/add/toto.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    run('git commit -m first'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    run('git rm logs/add/toto.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    with raises(ValueError, match="No part log file found. Cannot commit for you, use `add` first."):
        ezchlog.commit(dry_run=False, partlog_path=None)
    assert (
        run(
            'git log --pretty=tformat:%s --all -1'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == 'first\n'
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_commit_partlog_one_with_sharp_ref(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    (tmp_path / 'logs' / 'add').mkdir(parents=True)
    (tmp_path / 'logs' / 'add' / 'toto.md').write_text("- toto content (#42)\n- other info", encoding='utf-8')
    run('git add logs/add/toto.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    msg = ezchlog.commit(dry_run=False, partlog_path=None)
    assert msg == "Ref #42: toto content\n\n- other info\n"
    assert (
        run(
            'git log --pretty=tformat:%s --all -1'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == "Ref #42: toto content\n"
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_commit_partlog_multiple_with_selection(config_class, tmp_path) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        git_dir=tmp_path / '.git',
        root_dir=tmp_path,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    (tmp_path / 'logs' / 'add').mkdir(parents=True)
    (tmp_path / 'logs' / 'add' / 'toto.md').write_text("- toto content (#42)\n- other info", encoding='utf-8')
    (tmp_path / 'logs' / 'add' / 'a_test.md').write_text("simple message", encoding='utf-8')
    run('git add logs/add/toto.md logs/add/a_test.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    partlog_path = str(tmp_path / 'logs' / 'add' / 'a_test.md')
    msg = ezchlog.commit(dry_run=False, partlog_path=partlog_path)
    assert msg == "simple message\n\n- toto content (#42)\n- other info\n"
    assert (
        run(
            'git log --pretty=tformat:%s --all -1'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == "simple message\n"
    )


@fixture
def category_class() -> EnumMeta:
    category_class = Enum('Category', names=['fix', 'add'])  # type: ignore
    return category_class


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_list(config_class, tmp_path, category_class) -> None:
    config_class.return_value = MagicMock(
        log_dir=tmp_path / 'logs',
        category_class=category_class,
    )
    (tmp_path / 'logs' / 'add').mkdir(parents=True)
    (tmp_path / 'logs' / 'add' / 'toto.md').touch()
    (tmp_path / 'logs' / 'add' / 'a_test.md').touch()
    (tmp_path / 'logs' / 'fix').mkdir(parents=True)
    (tmp_path / 'logs' / 'fix' / 'some_fix.md').touch()
    ezchlog = EzChLog()
    assert ezchlog.list() == [
        Path('fix') / 'some_fix.md',
        Path('add') / 'a_test.md',
        Path('add') / 'toto.md',
    ]


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_merge_empty_version(config_class, tmp_path, category_class) -> None:
    log_dir = tmp_path / 'logs'
    log_file = tmp_path / 'chglogs.md'
    git_dir = tmp_path / '.git'
    default_changelog = '# Changelogs'
    config_class.return_value = MagicMock(
        log_dir=log_dir,
        log_file=log_file,
        git_dir=git_dir,
        root_dir=tmp_path,
        category_class=category_class,
        default_changelog=default_changelog,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    ezchlog = EzChLog()
    expected_content = "# Changelogs\n"
    assert ezchlog.merge(dry_run=False, next_version="1.0.0", update_index=False) == expected_content
    assert log_file.read_text(encoding='utf-8') == expected_content
    assert (
        run(
            'git diff --staged --name-only'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == ''
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_merge_not_existing(config_class, tmp_path, category_class) -> None:
    log_dir = tmp_path / 'logs'
    log_file = tmp_path / 'chglogs.md'
    git_dir = tmp_path / '.git'
    default_changelog = '# Changelogs'
    config_class.return_value = MagicMock(
        log_dir=log_dir,
        log_file=log_file,
        git_dir=git_dir,
        root_dir=tmp_path,
        category_class=category_class,
        default_changelog=default_changelog,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    (log_dir / 'add').mkdir(parents=True)
    (log_dir / 'add' / 'toto.md').write_text("- toto content", encoding='utf-8')
    (log_dir / 'add' / 'a_test.md').write_text("- test content", encoding='utf-8')
    (log_dir / 'fix').mkdir(parents=True)
    (log_dir / 'fix' / 'some_fix.md').write_text("- fix content", encoding='utf-8')
    run('git add logs/add/toto.md logs/add/a_test.md logs/fix/some_fix.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    run('git commit -m test'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    assert (
        run(
            'git diff --staged --name-only'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == ''
    )
    ezchlog = EzChLog()
    expected_content = """\
# Changelogs

## 1.0.0
### fix
- fix content
### add
- test content
- toto content
"""
    assert ezchlog.merge(dry_run=False, next_version="1.0.0", update_index=True) == expected_content
    assert log_file.read_text(encoding='utf-8') == expected_content
    assert not (log_dir / 'add' / 'toto.md').exists()
    assert not (log_dir / 'add' / 'a_test.md').exists()
    assert not (log_dir / 'fix' / 'some_fix.md').exists()
    assert (
        run(
            'git diff --staged --name-only'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == '\n'.join(
            [
                'chglogs.md',
                'logs/add/a_test.md',
                'logs/add/toto.md',
                'logs/fix/some_fix.md',
            ]
        )
        + '\n'
    )


@patch('ezchlog.ezchlog.Config')
def test_ezchlog_merge_existing(config_class, tmp_path, category_class) -> None:
    log_dir = tmp_path / 'logs'
    log_file = tmp_path / 'chglogs.md'
    git_dir = tmp_path / '.git'
    default_changelog = '# Changelogs'
    config_class.return_value = MagicMock(
        log_dir=log_dir,
        log_file=log_file,
        git_dir=git_dir,
        root_dir=tmp_path,
        category_class=category_class,
        default_changelog=default_changelog,
    )
    run('git init'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    log_file.write_text(
        """\
# Changelogs

## 1.0.0
### fix
- fix content
### add
- test content
- toto content
""",
        encoding='utf-8',
    )
    (log_dir / 'fix').mkdir(parents=True)
    (log_dir / 'fix' / 'minor_modif.md').write_text("- a minor modif", encoding='utf-8')
    run('git add chglogs.md logs/fix/minor_modif.md'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    run('git commit -m test'.split(' '), cwd=tmp_path, text=True, capture_output=True, check=True)
    assert (
        run(
            'git diff --staged --name-only'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == ''
    )
    ezchlog = EzChLog()
    expected_content = """\
# Changelogs

## 1.1.0
### fix
- a minor modif

## 1.0.0
### fix
- fix content
### add
- test content
- toto content
"""
    assert ezchlog.merge(dry_run=False, next_version="1.1.0", update_index=True) == expected_content
    assert log_file.read_text(encoding='utf-8') == expected_content
    assert not (log_dir / 'fix' / 'minor_modif.md').exists()
    assert (
        run(
            'git diff --staged --name-only'.split(' '),
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        == '\n'.join(
            [
                'chglogs.md',
                'logs/fix/minor_modif.md',
            ]
        )
        + '\n'
    )
