from collections.abc import Iterator
from enum import Enum
from enum import EnumMeta
from functools import cached_property
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata
from os import environ
from pathlib import Path
from typing import Any
from typing import Optional
from typing import TypedDict
from typing import Union

try:
    from tomllib import load  # type: ignore[import-not-found]
except ModuleNotFoundError:
    from tomli import load  # type: ignore
try:
    _metadata_message = metadata(__package__ or __name__)
    if not hasattr(_metadata_message, 'json'):
        # patch _metadata_message for python 3.9 compat
        from re import split

        def _json(self):
            multiple_keys = [
                'Classifier',
                'Obsoletes-Dist',
                'Platform',
                'Project-URL',
                'Provides-Dist',
                'Provides-Extra',
                'Requires-Dist',
                'Requires-External',
                'Supported-Platform',
                'Dynamic',
            ]
            return {
                key.lower().replace('-', '_'): self.get_all(key)
                if key in multiple_keys
                else (split(r'\s+', self.get(key)) if key == 'Keywords' else self.get(key))
                for key in self.keys()
            }

        setattr(_metadata_message, 'json', _json(_metadata_message))  # noqa: B010
        assert hasattr(_metadata_message, 'json')
    __metadata__ = _metadata_message.json
except PackageNotFoundError:
    __metadata__ = dict(
        name=__name__,
        version='unknown',
        summary=__name__,
        author_email='unknown',
    )


class ConfigParams(TypedDict):
    log_file: str
    log_dir: str
    category_list: list[str]
    category_default: str
    default_changelog: str
    no_git: bool
    branch_format: str
    branch_separator: str
    branch_lowercase_for: list[str]


DEFAULTS = ConfigParams(
    log_file='CHANGELOG.md',
    log_dir='_CHANGELOGS',
    category_list=[
        'Security',
        'Fixed',
        'Changed',
        'Added',
        'Removed',
        'Deprecated',
    ],
    category_default='Changed',
    default_changelog="""\
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).
""",
    no_git=False,
    branch_format="%{ref}%{sep}%{name}",  # allowed variables: ref, cat, name, sep
    branch_separator="_",
    branch_lowercase_for=['cat', 'name'],  # allowed variables: ref, cat, name
)


class Config:
    curr_dir: Path
    log_file: Path
    log_dir: Path
    category_list: list[str]
    category_default: str
    default_changelog: str
    no_git: bool
    branch_format: str
    branch_separator: str
    branch_lowercase_for: list[str]

    def __init__(self) -> None:
        self.curr_dir = Path.cwd().resolve()
        cfg: dict[str, Any] = {}
        if self.pyproject:
            with self.pyproject.open('rb') as f:
                cfg |= load(f).get('tool', {}).get('ezchlog', {})
        if self.ezchlogconf:
            with self.ezchlogconf.open('rb') as f:
                cfg |= load(f)
        self.log_file = Path(environ.get('EZCHLOG_LOG_FILE', cfg.get('log_file', DEFAULTS['log_file'])))
        if not self.log_file.is_absolute():
            self.log_file = self.root_dir / self.log_file
        self.log_dir = Path(environ.get('EZCHLOG_LOG_DIR', cfg.get('log_dir', DEFAULTS['log_dir'])))
        if not self.log_dir.is_absolute():
            self.log_dir = self.root_dir / self.log_dir
        raw_categories: Union[str, list[str]] = environ.get('EZCHLOG_CATEGORY_LIST', cfg.get('category_list', DEFAULTS['category_list']))
        self.category_list = raw_categories.split(',') if isinstance(raw_categories, str) else raw_categories
        self.category_default = environ.get('EZCHLOG_CATEGORY_DEFAULT', cfg.get('category_default', DEFAULTS['category_default']))
        self.default_changelog = environ.get('EZCHLOG_DEFAULT_CHANGELOG', cfg.get('default_changelog', DEFAULTS['default_changelog']))
        self.no_git = environ.get('EZCHLOG_NO_GIT', cfg.get('no_git', DEFAULTS['no_git'])) in (True, 'true', 'True', '1', 'on')
        self.branch_format = environ.get('EZCHLOG_BRANCH_FORMAT', cfg.get('branch_format', DEFAULTS['branch_format']))
        self.branch_separator = environ.get('EZCHLOG_BRANCH_SEPARATOR', cfg.get('branch_separator', DEFAULTS['branch_separator']))
        raw_br_lc_for: Union[str, list[str]] = environ.get('EZCHLOG_BRANCH_LOWERCASE_FOR', cfg.get('branch_lowercase_for', DEFAULTS['branch_lowercase_for']))
        self.branch_lowercase_for = raw_br_lc_for.split(',') if isinstance(raw_br_lc_for, str) else raw_br_lc_for

    @cached_property
    def ezchlogconf(self) -> Optional[Path]:
        p_root = self.curr_dir
        for p in [p_root] + list(p_root.parents):
            pf = p / '.ezchlog.toml'
            if pf.is_file():
                return pf
        else:
            return None

    @cached_property
    def pyproject(self) -> Optional[Path]:
        p_root = self.curr_dir
        for p in [p_root] + list(p_root.parents):
            pf = p / 'pyproject.toml'
            if pf.is_file():
                return pf
        else:
            return None

    @cached_property
    def editorconfig(self) -> Optional[Path]:
        p_root = self.curr_dir
        for p in [p_root] + list(p_root.parents):
            pf = p / '.editorconfig'
            if pf.is_file():
                return pf
        else:
            return None

    @cached_property
    def git_dir(self) -> Optional[Path]:
        p_root = self.curr_dir
        for p in [p_root] + list(p_root.parents):
            pd = p / '.git'
            if pd.is_dir():
                return pd
        else:
            return None

    @cached_property
    def root_dir(self) -> Path:
        for attr in ('ezchlogconf', 'pyproject', 'editorconfig', 'git_dir'):
            if path := getattr(self, attr):
                return path.parent
        else:
            return self.curr_dir

    @cached_property
    def category_class(self) -> EnumMeta:
        category_class = Enum('Category', names=self.category_list)  # type: ignore
        return category_class

    def __iter__(self) -> Iterator[tuple[str, object]]:
        Category = self.category_class
        category_names = list(cat.name for cat in list[Enum](Category))
        d = ConfigParams(
            log_file=str(self.log_file),
            log_dir=str(self.log_dir),
            category_list=category_names,
            category_default=self.category_default,
            default_changelog=self.default_changelog,
            no_git=self.no_git,
            branch_format=self.branch_format,
            branch_separator=self.branch_separator,
            branch_lowercase_for=self.branch_lowercase_for,
        )
        return iter(d.items())
