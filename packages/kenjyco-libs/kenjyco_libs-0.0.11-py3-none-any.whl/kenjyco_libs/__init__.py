import os.path
import bg_helper as bh
import fs_helper as fh
import settings_helper as sh


SETTINGS = sh.get_all_settings(__name__).get(sh.APP_ENV, {})

_package_repos_base_path = SETTINGS.get('package_repos_base_path')
_kenjyco_libs_repo_names = SETTINGS.get('kenjyco_libs_repo_names')
_dependency_repos_base_path = SETTINGS.get('dependency_repos_base_path')
if not _package_repos_base_path or not _kenjyco_libs_repo_names or not _dependency_repos_base_path:
    # Sync settings.ini with vimdiff
    sh.sync_settings_file(__name__)
    SETTINGS = sh.get_all_settings(__name__).get(sh.APP_ENV, {})
    _package_repos_base_path = SETTINGS.get('package_repos_base_path')
    _kenjyco_libs_repo_names = SETTINGS.get('kenjyco_libs_repo_names')
    _dependency_repos_base_path = SETTINGS.get('dependency_repos_base_path')

assert _package_repos_base_path and _kenjyco_libs_repo_names and _dependency_repos_base_path, (
    'PACKAGE_REPOS_BASE_PATH, KENJYCO_LIBS_REPO_NAMES, and DEPENDENCY_REPOS_BASE_PATH are not set'
)

_dependency_repos_dict = {
    'beautifulsoup4': 'https://git.launchpad.net/beautifulsoup',
    'boto3': 'https://github.com/boto/boto3',
    'click': 'https://github.com/pallets/click',
    'cryptography': 'https://github.com/pyca/cryptography',
    'hiredis': 'https://github.com/redis/hiredis-py',
    'importlib-metadata': 'https://github.com/python/importlib_metadata',
    'ipython': 'https://github.com/ipython/ipython',
    'jinja2': 'https://github.com/pallets/jinja',
    'lxml': 'https://github.com/lxml/lxml',
    'pipdeptree': 'https://github.com/naiquevin/pipdeptree',
    'psycopg2-binary': 'https://github.com/psycopg/psycopg2',
    'pymongo': 'https://github.com/mongodb/mongo-python-driver',
    'pymysql': 'https://github.com/PyMySQL/PyMySQL',
    'pytest': 'https://github.com/pytest-dev/pytest',
    'pytest-cov': 'https://github.com/pytest-dev/pytest-cov',
    'pytz': 'https://git.launchpad.net/pytz',
    'redis': 'https://github.com/redis/redis-py',
    'requests': 'https://github.com/psf/requests',
    'sqlalchemy': 'https://github.com/sqlalchemy/sqlalchemy',
    'ujson': 'https://github.com/ultrajson/ultrajson',
    'urllib3': 'https://github.com/urllib3/urllib3',
    'xmljson': 'https://github.com/sanand0/xmljson',
}

# _skip_editable_install_for_these = (
#     'cryptography',     # Requires rust compiler
#     'hiredis',          # Exact version needed for redis-helper
#     'lxml',             # RuntimeError when trying to build without Cython
#     'redis',            # Exact version needed for redis-helper
#     'requests',         # Not compatible with latest urllib3
#     'pymongo',          # Exact version needed for mongo-helper
#     'pytz',             # Has setup.py in src directory, not root of repo
#     'sqlalchemy',       # Latest (2.0 beta) not compatible with sql-helper
#     'ujson',            # Exact version needed for redis-helper
#     'urllib3',          # Not compatible with latest requests
# )

_package_repos_base_path = fh.abspath(_package_repos_base_path)
_dependency_repos_base_path = fh.abspath(_dependency_repos_base_path)


def _get_clone_status_for_packages():
    cloned = {}
    uncloned = {}
    for repo in _kenjyco_libs_repo_names:
        repo_path = os.path.join(_package_repos_base_path, repo)
        if os.path.isdir(repo_path):
            cloned[repo] = repo_path
        else:
            uncloned[repo] = repo_path

    return {
        'cloned': cloned,
        'uncloned': uncloned
    }


def _get_clone_status_for_dependencies():
    cloned = {}
    uncloned = {}
    for repo in _dependency_repos_dict:
        repo_path = os.path.join(_dependency_repos_base_path, repo)
        if os.path.isdir(repo_path):
            cloned[repo] = repo_path
        else:
            uncloned[repo] = repo_path

    return {
        'cloned': cloned,
        'uncloned': uncloned
    }


def _get_kenjyco_pkgs_in_venv():
    installed_pkgs_set = set(bh.tools.installed_packages().keys())
    full_kenjyco_pkgs_set = set(_kenjyco_libs_repo_names)
    full_kenjyco_pkgs_set.add('kenjyco-libs')
    return installed_pkgs_set.intersection(full_kenjyco_pkgs_set)


def _get_dependencies_in_venv():
    installed_pkgs_set = set([
        name.lower()
        for name in bh.tools.installed_packages().keys()
    ])
    full_dep_repos_set = set(_dependency_repos_dict.keys())
    return installed_pkgs_set.intersection(full_dep_repos_set)


def _clone_packages(show=True):
    """Clone package repos locally

    - show: if True, show the `git` command before executing
    """
    clone_status = _get_clone_status_for_packages()
    pkgs_in_venv = _get_kenjyco_pkgs_in_venv()
    uncloned_set = set(clone_status['uncloned'].keys())
    to_clone = uncloned_set.intersection(pkgs_in_venv)
    if 'libs' in uncloned_set:
        to_clone.add('libs')
    for name in sorted(to_clone):
        url = 'https://github.com/kenjyco/{}'.format(name)
        bh.tools.git_clone(
            url,
            path=_package_repos_base_path,
            name=name,
            show=show
        )


def _clone_dependencies(show=True):
    """Clone dependency repos locally

    - show: if True, show the `git` command before executing
    """
    clone_status = _get_clone_status_for_dependencies()
    deps_in_venv = _get_dependencies_in_venv()
    uncloned_set = set(clone_status['uncloned'].keys())
    for name in sorted(uncloned_set.intersection(deps_in_venv)):
        url = _dependency_repos_dict[name]
        bh.tools.git_clone(
            url,
            path=_dependency_repos_base_path,
            name=name,
            show=show
        )


def clone_all_missing(show=True):
    """Clone package and dependency repos locally

    - show: if True, show the `git` command before executing
    """
    _clone_packages(show=show)
    _clone_dependencies(show=show)


def install_packages_in_editable_mode(show=True):
    """Install all kenjyco packages that are cloned locally in editable mode

    - show: if True, show the `pip` command before executing
    """
    cloned_locally = _get_clone_status_for_packages()['cloned']
    if 'libs' in cloned_locally:
        cloned_locally['kenjyco-libs'] = cloned_locally['libs']
    # cloned_locally.update(_get_clone_status_for_dependencies()['cloned'])
    installed_packages = bh.tools.installed_packages(name_only=True)
    # editable_install_ok = (set(cloned_locally.keys()) & set(installed_packages)) - set(_skip_editable_install_for_these)
    editable_install_ok = set(cloned_locally.keys()) & set(installed_packages)
    paths = [cloned_locally[pkg] for pkg in editable_install_ok]
    return bh.tools.pip_install_editable(paths, show=show)


def dev_setup(py_versions='', show=True):
    """Calls some funcs so you don't have to

    - py_versions: string containing Python versions to make venvs for separated
      by any of , ; |
    - show: if True, show the `git`/`pip` commands before executing

    Calls these in order:

    - clone_all_missing
    - install_packages_in_editable_mode
    """
    clone_all_missing(show=show)
    install_packages_in_editable_mode(show=show)
