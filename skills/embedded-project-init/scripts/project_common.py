"""Standard-library profile parsing and conservative filesystem checks."""
import json
import os
from pathlib import Path
import re
import stat
from string import Template

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
PROFILES = ('firmware', 'embedded-fullstack', 'robotics')
VERSION = '0.1.0'
MANIFEST = '.engineering-project.json'
RESERVED = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)),
            *(f'lpt{i}' for i in range(1, 10))}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def check_path(path):
    """Reject links/reparse points in every existing path component, without resolving them."""
    path = Path(os.path.abspath(path))
    for item in reversed((path, *path.parents)):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(info.st_mode)
                or getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
            raise ValueError(f'Unsafe link or reparse point: {item}')
        if item != path and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f'Ancestor is not a directory: {item}')
    return path


def target_path(target):
    target = Path(target)
    if '..' in target.parts:
        raise ValueError('Target must not contain parent traversal (..)')
    return check_path(target)


def scan_target(target):
    check_path(target)
    if not target.exists():
        return
    if not target.is_dir():
        raise ValueError(f'Target is not a directory: {target}')
    def failed(error):
        raise error
    for directory, names, files in os.walk(target, followlinks=False, onerror=failed):
        for name in (*names, *files):
            path = check_path(Path(directory) / name)
            mode = path.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError(f'Unsupported filesystem object: {path}')


def load_profile(profile_id, assets=ASSETS):
    if profile_id not in PROFILES:
        raise ValueError(f'Unknown profile: {profile_id}')
    path = check_path(Path(assets) / 'profiles' / f'{profile_id}.json')
    profile = read_json(path)
    if (not isinstance(profile, dict)
            or set(profile) != {'id', 'description', 'schema_version', 'directories'}
            or profile['id'] != profile_id
            or type(profile['schema_version']) is not int or profile['schema_version'] != 1
            or not isinstance(profile['description'], str) or not profile['description'].strip()
            or any(ord(c) < 32 for c in profile['description'])):
        raise ValueError('Invalid profile metadata/schema')
    directories = profile['directories']
    if not isinstance(directories, list) or not 0 < len(directories) <= 200:
        raise ValueError('Profile directories must be a nonempty list (maximum 200)')
    seen = set()
    prefixes = {}
    for name in directories:
        if not isinstance(name, str) or not name:
            raise ValueError('Directory must be a nonempty relative path')
        parts = name.split('/')
        if any(not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_-]*', p) or p.casefold() in RESERVED for p in parts):
            raise ValueError(f'Unsafe profile directory: {name}')
        if name.casefold() in seen:
            raise ValueError(f'Duplicate directory: {name}')
        seen.add(name.casefold())
        for index in range(1, len(parts) + 1):
            prefix = '/'.join(parts[:index])
            key = prefix.casefold()
            if key in prefixes and prefixes[key] != prefix:
                raise ValueError(f'Case-conflicting directory: {name}')
            prefixes[key] = prefix
    if any(a != b and b.casefold().startswith(a.casefold() + '/') for a in directories for b in directories):
        raise ValueError('List only leaf directories; overlapping entries are redundant')
    return profile


def all_directories(profile):
    names = set()
    for name in profile['directories']:
        parts = name.split('/')
        names.update('/'.join(parts[:index]) for index in range(1, len(parts) + 1))
    return sorted(names, key=lambda name: (name.count('/'), name))


def project_name(name):
    if not isinstance(name, str) or not re.fullmatch(r'[\w][\w .-]{0,99}', name):
        raise ValueError('Name must be 1-100 letters/digits/spaces/dots/hyphens/underscores')
    return name


def manifest(profile, name):
    return {'schema_version': 1, 'generator_version': VERSION, 'profile': profile['id'],
            'project_name': project_name(name), 'directories': profile['directories']}


def render_files(profile, name, assets=ASSETS):
    values = {'name': project_name(name), 'profile': profile['id'],
              'description': profile['description'],
              'modules': '\n'.join('- `' + p + '`' for p in profile['directories'])}
    result = {}
    for target, template in (('README.md', 'README.md.tpl'), ('.gitignore', 'gitignore.tpl')):
        text = check_path(Path(assets) / 'templates' / template).read_text(encoding='utf-8')
        result[target] = Template(text).substitute(values).encode('utf-8')
    result[MANIFEST] = (json.dumps(manifest(profile, name), ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return result
