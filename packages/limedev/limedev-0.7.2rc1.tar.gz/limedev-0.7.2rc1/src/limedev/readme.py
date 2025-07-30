"""For generating readme.md file."""
import datetime
import re
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import yamdog as md

from ._aux import import_from_path
from ._aux import PATH_PROJECT
from ._aux import upsearch
#=======================================================================
# Hinting types
if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any
    from typing import NotRequired
    from typing import TypeAlias
    from typing import TypedDict

    _TOMLElemental: TypeAlias = str | bool | float | int

    TOMLValue: TypeAlias = (_TOMLElemental |
                            list['TOMLValue'] |
                            dict[str, 'TOMLValue'])

    BuildSystemInfo = TypedDict('BuildSystemInfo',
                                {'requires': list[str],
                                 'build-backend': str})

    class AuthorInfo(TypedDict):
        name: str
        email: NotRequired[str]

    _Urls = TypedDict('_Urls',
                     {'Homepage': str,
                      'Changelog': NotRequired[str],
                      'Issure Tracker': NotRequired[str]})

    _PyprojectProject = TypedDict('_PyprojectProject',
        {
         'authors': list[AuthorInfo],
         'maintainers': list[AuthorInfo],
         'classifiers': list[str],
         'description': str,
         'name': str,
         'readme': str,
         'requires-python': str,
         'version': str,

         'dependencies': NotRequired[list[str]],
         'optional-dependencies': NotRequired[dict[str, list[str]]],
         'dynamic': NotRequired[list[str]],
         'license': NotRequired[str],
         'license-files': NotRequired[list[str]],
         'scripts': NotRequired[dict[str, str]],
         'urls': _Urls})

    Pyproject = TypedDict('Pyproject',
                          {'build-system': BuildSystemInfo,
                           'project': _PyprojectProject,
                           'tool': dict[str, dict[str, TOMLValue]]})
else:
    Pyproject = object
    Iterable = tuple
# ----------------------------------------------------------------------
re_heading = re.compile(r'^#* .*$')
# ----------------------------------------------------------------------
def parse_md_element(text: str):
    """Very simple parser able to parse part of markdown syntax into.

    YAMDOG.

    objects.
    """
    if match := re_heading.match(text):
        hashes, content = match[0].split(' ', 1)
        return md.Heading(content, len(hashes))
    return md.Raw(text)
#-----------------------------------------------------------------------
def parse_md(text: str):
    """Loops md parser."""
    return md.Document([parse_md_element(item.strip())
                        for item in text.split('\n\n')])
#=======================================================================
def make_intro(full_name: str,
               pypiname: str,
               semi_description: Any) -> md.Document:
    """Builds intro from metadata."""

    pypi_project_url = f'https://pypi.org/project/{pypiname}'
    pypi_badge_info = (('v', 'PyPI Package latest release'),
                       ('wheel', 'PyPI Wheel'),
                       ('pyversions', 'Supported versions'),
                       ('implementation', 'Supported implementations'))
    pypi_badges = [md.Link(pypi_project_url,
                           md.Image(f'https://img.shields.io/pypi/'
                                    f'{code}/{pypiname}.svg',
                                    desc), 'Project PyPI page')
                   for code, desc in pypi_badge_info]
    doc = md.Document([md.Paragraph(pypi_badges, '\n'),
                       md.Heading(full_name, 1, in_TOC = False)])
    doc += semi_description
    doc += md.Heading('Table of Contents', 2, in_TOC = False)
    doc += md.TOC()
    return doc
#=======================================================================
def make_setup_guide(name: str,
                     pypiname: str,
                     package_name: str,
                     abbreviation: str
                     ) -> md.Document:
    """Builds setup guide from metadata."""
    doc = md.Document([
        md.Heading('Quick start guide', 1),
        "Here's how you can start ",
        md.Heading('The first steps', 2),
        md.Heading('Installing', 3),
        f'Install {name} with pip',
        md.CodeBlock(f'pip install {pypiname}'),
        md.Heading('Importing', 3),
        md.Paragraph([(f'Import name is '
                       f"{'' if pypiname == package_name else 'not '}"
                       f'the same as install name, '),
                       md.Code(pypiname),
                       '.']),
        md.CodeBlock(f'import {package_name}', 'python')])

    if abbreviation:
        doc += md.Paragraph(['Since the package is accessed often,  abbreviation ',
                             md.Code(abbreviation),
                      ' is used. The abbreviation is used throughout this document.'])
        doc += md.CodeBlock(f'import {package_name} as {abbreviation}', 'python')
    return doc
#=======================================================================
def make_changelog(level: int, path_changelog: Path, version: str
                   ) -> md.Document:
    """Loads changelog and reformats it for README document."""
    doc = md.Document([md.Heading('Changelog', level, in_TOC = False)])
    changelog = parse_md(path_changelog.read_text())
    if changelog:
        if (latest := changelog.content[0]).content.split(' ', 1)[0] == version:
            latest.content = f'{version} {datetime.date.today().isoformat()}'
        else:
            raise ValueError(f'Changelog not up to date. Version {version} Latest: {latest}')

        # Updating the changelog file
        path_changelog.write_text(str(changelog) + '\n')

        for item in changelog:
            if isinstance(item, md.Heading):
                item.level += level
                item.in_TOC = False

        doc += changelog

    return doc
#=======================================================================
def make_annexes(annexes: Iterable[tuple[Any, Any]]):
    """Formats annexes into sections."""
    doc = md.Document([md.Heading('Annexes', 1)])
    for index, (heading_content, body) in enumerate(annexes, start = 1):
        doc += md.Heading(f'Annex {index}: {heading_content}', 2)
        doc += body
    return doc
#=======================================================================
def make(package,
         semi_description: Any,
         *,
         name: str = '',
         pypiname: str = '',
         abbreviation: str = '',
         quick_start: Any = None,
         readme_body: Any = None,
         annexes: Iterable[tuple[Any, Any]] = (),
         ) -> md.Document:
    """Builds a README document from given metadata and contents."""
    if not name:
        name = package.__name__.capitalize()
    if not pypiname:
        pypiname = package.__name__
    doc = make_intro(name, pypiname, semi_description)
    doc += make_setup_guide(name, pypiname, package.__name__, abbreviation)

    if quick_start is not None:
        doc += quick_start

    if readme_body is not None:
        doc += readme_body
    if (path_changelog := upsearch('*changelog.md',
                                    Path(package.__file__).parent,
                                    deep = True)) is None:
        raise FileNotFoundError('Changelog not found')

    doc += make_changelog(1, path_changelog, package.__version__)

    if annexes:
        doc += make_annexes(annexes)
    return doc
#=======================================================================
def main() -> int:
    """Command line interface entry point."""
    import tomllib

    pyproject: Pyproject = tomllib.loads(( # type: ignore[assignment]
        PATH_PROJECT / 'pyproject.toml').read_text())
    (PATH_PROJECT / 'README.md'
     ).write_text(str(import_from_path(PATH_PROJECT / 'readme' / 'readme.py'
                                       ).main(pyproject))
                  + '\n')
    return 0
#=======================================================================
if __name__ == '__main__':
    raise SystemExit(main())
