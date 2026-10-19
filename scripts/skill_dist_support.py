"""Shared, read-only catalog/package and filesystem safety checks."""
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'git-governance': ('git-governance', 'stable'),
            'embedded-c-module': ('skills/embedded-c-module', 'preview'),
            'embedded-project-init': ('skills/embedded-project-init', 'preview')}
EXCLUDED = {'.git', '.venv', '__pycache__', '.pytest_cache', '.DS_Store', 'Thumbs.db'}
RESERVED = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)),
            *(f'lpt{i}' for i in range(1, 10))}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative(name):
    require(isinstance(name, str) and bool(name), 'Empty/non-string relative path')
    require(all(re.fullmatch(r'[A-Za-z0-9_.-]+', part) and part not in ('.', '..')
                and not part.endswith('.') and part.split('.')[0].casefold() not in RESERVED
                for part in name.split('/')), f'Unsafe relative path: {name}')
    return name


def safe_path(path):
    path = Path(path)
    require(not path.drive or path.is_absolute(), 'Drive-relative paths are forbidden')
    require('..' not in path.parts, 'Parent traversal is forbidden')
    # Windows device names, ADS, ambiguous trailing dots/spaces: reject on all hosts.
    for part in path.parts[1:] if path.anchor else path.parts:
        require(not any(c in part for c in ':<>"|?*') and not part.endswith(('.', ' '))
                and part.split('.')[0].casefold() not in RESERVED
                and not any(ord(c) < 32 for c in part), f'Unsafe path component: {part}')
    path = Path(os.path.abspath(path))
    for component in reversed((path, *path.parents)):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
                f'Link/reparse point forbidden: {component}')
        require(component == path or stat.S_ISDIR(info.st_mode), f'Non-directory ancestor: {component}')
        require(stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode), f'Special file: {component}')
        if stat.S_ISREG(info.st_mode):
            require(info.st_nlink == 1, f'Hard-linked file forbidden: {component}')
    return path


def excluded(name):
    return (name in EXCLUDED or name.endswith(('.pyc', '.pyo', '.tmp', '.log', '.swp', '~')))


def tree(path, filter_source=False):
    """Read exact files and directory names; reject links even when excluded."""
    path = safe_path(path)
    require(path.is_dir(), f'Missing directory: {path}')
    files, dirs, folded = {}, [], set()
    def failed(error):
        raise error
    for parent, names, leaves in os.walk(path, followlinks=False, onerror=failed):
        for name in sorted(names + leaves):
            item = safe_path(Path(parent) / name)
            key = item.relative_to(path).as_posix()
            if filter_source and excluded(name):
                if name in names:
                    names.remove(name)
                continue
            relative(key)
            require(key.casefold() not in folded, f'Case-colliding path: {key}')
            folded.add(key.casefold())
            if item.is_dir():
                dirs.append(key)
            else:
                files[key] = item.read_bytes()
    return dict(sorted(files.items())), sorted(dirs)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(safe_path(path).read_text(encoding='utf-8'), object_pairs_hook=unique)


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def catalog(root=ROOT):
    root = safe_path(root)
    data = read_json(root / 'catalog/skills.json')
    require(isinstance(data, dict) and set(data) == {'schema_version', 'skills'}
            and type(data['schema_version']) is int and data['schema_version'] == 1
            and isinstance(data['skills'], list), 'Invalid catalog schema')
    result = {}
    for item in data['skills']:
        require(isinstance(item, dict) and set(item) == {'name', 'source_dir', 'channel', 'description', 'installable'},
                'Invalid catalog entry fields')
        name = item['name']
        require(isinstance(name, str) and name in EXPECTED and name not in result, 'Unknown/duplicate Skill name')
        relative(item['source_dir'])
        require((item['source_dir'], item['channel']) == EXPECTED[name], 'Wrong canonical source/channel')
        require(type(item['installable']) is bool and isinstance(item['description'], str)
                and 0 < len(item['description'].strip()) <= 1024, 'Invalid catalog field types')
        source = safe_path(root / item['source_dir'])
        require(source.is_dir(), f'Missing source: {source}')
        result[name] = item
    require(set(result) == set(EXPECTED), 'Catalog must enumerate exactly three Skills')
    return result


def package(name, root=ROOT, require_installable=True):
    """Snapshot canonical source; never repair/synchronize or execute Skill scripts."""
    if __package__:
        from .validate import frontmatter
        from .validate_embedded_c import check_document
        from .sync_embedded_c_skill import COPIES as C_COPIES
        from .sync_embedded_project_skill import COPIES as PROJECT_COPIES
        from .validate_embedded_c_skill import REQUIRED as C_REQUIRED
        from .validate_embedded_project_skill import REQUIRED as PROJECT_REQUIRED
    else:
        from validate import frontmatter
        from validate_embedded_c import check_document
        from sync_embedded_c_skill import COPIES as C_COPIES
        from sync_embedded_project_skill import COPIES as PROJECT_COPIES
        from validate_embedded_c_skill import REQUIRED as C_REQUIRED
        from validate_embedded_project_skill import REQUIRED as PROJECT_REQUIRED
    entries = catalog(root)
    require(name in entries, 'Unknown Skill')
    entry = entries[name]
    require(not require_installable or entry['installable'], f'Not installable: {name}')
    source = safe_path(root / entry['source_dir'])
    files, dirs = tree(source, filter_source=True)
    required = {'SKILL.md', 'LICENSE'}
    copies = {}
    if name == 'embedded-c-module':
        required.update(C_REQUIRED)
        copies = C_COPIES
    elif name == 'embedded-project-init':
        required.update(PROJECT_REQUIRED)
        copies = PROJECT_COPIES
    else:
        required.update(('references/GIT_GOVERNANCE.md', 'adapters/cursor/git-branch-policy.mdc'))
    require(required <= files.keys(), f'Missing resources: {sorted(required - files.keys())}')
    for origin, destination in copies.items():
        key = (root / destination).relative_to(source).as_posix()
        require(safe_path(root / origin).read_bytes() == files.get(key),
                f'Source/copy drift: {destination}; resolve synchronization in a separate authorized task')
    require(files['LICENSE'] == safe_path(root / 'LICENSE').read_bytes(), 'License copy drift')
    import yaml
    try:
        metadata = frontmatter(source / 'SKILL.md')
    except yaml.YAMLError as error:
        raise ValueError(f'Invalid Skill YAML: {error}') from error
    require(metadata.get('name') == name, 'Skill frontmatter name mismatch')
    require(isinstance(metadata.get('description'), str) and 0 < len(metadata['description'].strip()) <= 1024,
            'Invalid Skill description')
    require(isinstance(metadata.get('metadata'), dict), 'Invalid Skill metadata mapping')
    version = metadata['metadata'].get('version')
    require(isinstance(version, str) and re.fullmatch(r'\d+\.\d+\.\d+', version), 'Invalid module version')
    if entry['channel'] == 'stable':
        require(version == '3.0.0', 'Git Governance must remain 3.0.0')
    else:
        require(version == '0.1.0' and metadata['metadata'].get('status') == 'draft', 'Expected Draft 0.1.0')
    for key, content in files.items():
        text = content.decode('utf-8')
        require(not re.search(r'(?i)\b[a-z]:[\\/]|/(?:Users|home)/[^\s/]+/|\\\\[^\s\\]+\\', text),
                f'Machine-specific path: {key}')
        if key.endswith(('.md', '.mdc')):
            errors = check_document(source / key, source, text)
            require(not errors, '; '.join(errors))
    # Reject source changes during validation rather than package an unvalidated snapshot.
    require(tree(source, filter_source=True) == (files, dirs), 'Source changed during validation')
    check_package_documents(files, dirs)
    return {'name': name, 'version': version, 'channel': entry['channel'], 'files': files, 'dirs': dirs}


def check_package_documents(files, dirs):
    """Reuse the existing link parser against the actual in-memory package inventory."""
    if __package__:
        from .validate_embedded_c import check_document
    else:
        from validate_embedded_c import check_document
    entries = {'/package', *('/package/' + p for p in files), *('/package/' + p for p in dirs)}
    class InventoryPath:
        def __init__(self, value):
            self.value = PurePosixPath(value)

        @property
        def name(self):
            return self.value.name

        @property
        def parent(self):
            return InventoryPath(self.value.parent)

        def __truediv__(self, other):
            return InventoryPath(self.value / other)

        def resolve(self):
            return InventoryPath(posixpath.normpath(str(self.value)))

        def is_relative_to(self, other):
            return self.value.is_relative_to(other.value)

        def exists(self):
            return str(self.value) in entries
    for key, content in files.items():
        if key.endswith(('.md', '.mdc')):
            errors = check_document(InventoryPath('/package/' + key), InventoryPath('/package'), content.decode('utf-8'))
            require(not errors, '; '.join(errors))


def archive(bundle):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as zipped:
        for key, content in sorted(bundle['files'].items()):
            relative(key)
            info = zipfile.ZipInfo(bundle['name'] + '/' + key, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            zipped.writestr(info, content)
    payload = output.getvalue()
    validate_archive(payload, bundle['name'])
    return payload


def validate_archive(payload, name):
    """Validate ZIP member paths and types without extracting anything."""
    require(name in EXPECTED, 'Unknown archive Skill')
    files = {}
    with zipfile.ZipFile(io.BytesIO(payload)) as zipped:
        for item in zipped.infolist():
            relative(item.filename)
            require(item.filename.startswith(name + '/'), 'Wrong ZIP root')
            mode = item.external_attr >> 16
            require(not item.is_dir() and stat.S_IFMT(mode) in (0, stat.S_IFREG), 'ZIP link/special entry')
            key = item.filename[len(name) + 1:]
            require(key.casefold() not in {p.casefold() for p in files}, 'Duplicate ZIP member')
            require(item.file_size <= 10_000_000 and len(files) < 1000, 'Archive exceeds package limits')
            files[key] = zipped.read(item)
    require({'SKILL.md', 'LICENSE'} <= files.keys(), 'Missing ZIP entrypoint/license')
    require(not any(b.startswith(a + '/') for a in files for b in files), 'ZIP file/directory collision')
    dirs = sorted({str(parent) for key in files for parent in PurePosixPath(key).parents if str(parent) != '.'})
    all_paths = list(files) + dirs
    require(len({p.casefold() for p in all_paths}) == len(all_paths), 'Case-colliding ZIP paths')
    check_package_documents(files, dirs)
    return files
