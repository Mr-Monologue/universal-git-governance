"""Local Skill distribution. Target mutations require --apply; no network or Git."""
import argparse
import os
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
if __package__:
    from .skill_dist_support import (ROOT, EXPECTED, archive, catalog, encoded, package,
                                     read_json, relative, require, safe_path, sha, tree)
else:
    from skill_dist_support import (ROOT, EXPECTED, archive, catalog, encoded, package,
                                    read_json, relative, require, safe_path, sha, tree)

MANAGEMENT = '.skill-dist'


def record(bundle):
    return {'schema_version': 1, 'name': bundle['name'], 'version': bundle['version'],
            'channel': bundle['channel'], 'dirs': bundle['dirs'],
            'files': {key: sha(value) for key, value in bundle['files'].items()}}


def target_paths(target, name, root=ROOT):
    require(name in EXPECTED, 'Unknown Skill')
    target = safe_path(target)
    require(target != Path(target.anchor), 'Filesystem root is not an installation directory')
    source_root = safe_path(root)
    require(not target.is_relative_to(source_root) and not source_root.is_relative_to(target),
            'Installation target must be outside the source repository and its ancestors')
    if target.exists():
        require(target.is_dir(), 'Target is not a directory')
    skill = safe_path(target / name)
    state = safe_path(target / MANAGEMENT)
    if state.exists():
        require(state.is_dir(), 'Management path is not a directory')
        # An interrupted transaction needs manual review; never silently delete it.
        for item in state.iterdir():
            safe_path(item)
            require(item.name in {n + '.json' for n in EXPECTED},
                    f'Pending transaction/unknown management entry: {item}')
    return target, skill, state / (name + '.json')


def verify_at(skill, receipt, name):
    require(receipt.is_file(), 'No managed installation record; refusing adoption')
    data = read_json(receipt)
    require(isinstance(data, dict) and set(data) == {'schema_version', 'name', 'version', 'channel', 'files', 'dirs'}
            and type(data['schema_version']) is int and data['schema_version'] == 1
            and data['name'] == name and isinstance(data['version'], str)
            and data['channel'] == EXPECTED[name][1]
            and isinstance(data['files'], dict) and isinstance(data['dirs'], list), 'Invalid installation record')
    for key, value in data['files'].items():
        relative(key)
        require(isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value),
                'Invalid recorded SHA-256')
    for key in data['dirs']:
        relative(key)
    require({'SKILL.md', 'LICENSE'} <= data['files'].keys(), 'Incomplete installation record')
    files, dirs = tree(skill)
    require({key: sha(value) for key, value in files.items()} == data['files'] and dirs == data['dirs'],
            'Integrity conflict: changed/missing/extra files or directories; manual review required')
    return data, (files, dirs)


def verify(name, target, root=ROOT):
    _, skill, receipt = target_paths(target, name, root)
    verify_at(skill, receipt, name)
    return 'PASS: managed installation integrity ' + name


def mkdirs(path, created):
    missing = []
    cursor = safe_path(path)
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    require(cursor.is_dir(), 'Non-directory creation parent')
    for item in reversed(missing):
        safe_path(item).mkdir()
        created.append(item)


def write_new(path, content, created):
    safe_path(path)
    with path.open('xb') as stream:
        created.append(path)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def delete_exact(path, expected):
    """No recursive deletion: verify exact contents, then unlink known files/rmdir."""
    require(tree(path) == expected, f'Refusing cleanup of changed tree: {path}')
    files, dirs = expected
    for key, content in files.items():
        item = safe_path(path / key)
        require(item.read_bytes() == content, f'Cleanup conflict: {item}')
        item.unlink()
    for key in sorted(dirs, key=lambda value: (value.count('/'), value), reverse=True):
        safe_path(path / key).rmdir()
    safe_path(path).rmdir()


def manage(action, name, target, apply=False, root=ROOT):
    require(action in ('install', 'upgrade', 'remove'), 'Unknown management action')
    target, skill, receipt = target_paths(target, name, root)
    old = old_tree = None
    if skill.exists() or receipt.exists():
        old, old_tree = verify_at(skill, receipt, name)
    elif action != 'install':
        raise ValueError('No managed installation to ' + action)
    bundle = package(name, root) if action != 'remove' else None
    new = record(bundle) if bundle else None
    if action == 'install' and old:
        require(old == new, 'Already installed with different content; use upgrade')
        return 'UNCHANGED: ' + name
    if action == 'upgrade' and old == new:
        return 'UNCHANGED: ' + name
    if not apply:
        return f'DRY RUN: {action} {name} at {skill}; no writes'

    made_dirs, made_files = [], []
    state = receipt.parent
    lock = state / 'lock'
    transaction = state / ('txn-' + uuid.uuid4().hex)
    staged, backup, pending, old_record = (transaction / n for n in ('new', 'old', 'record.json', 'old.json'))
    moved_old = moved_record = installed = recorded = committed = locked = False
    try:
        mkdirs(state, made_dirs)
        write_new(lock, b'Local distribution transaction; do not remove without review\n', made_files)
        locked = True
        # Recheck under our lock. This serializes this tool, not arbitrary other programs.
        if old is not None:
            require(verify_at(skill, receipt, name) == (old, old_tree), 'Installation changed since preview')
        else:
            require(not skill.exists() and not receipt.exists(), 'Target appeared since preview')
        mkdirs(transaction, made_dirs)
        if bundle:
            mkdirs(staged, made_dirs)
            for key in bundle['dirs']:
                mkdirs(staged / key, made_dirs)
            for key, content in bundle['files'].items():
                mkdirs((staged / key).parent, made_dirs)
                write_new(staged / key, content, made_files)
            require(tree(staged) == (bundle['files'], bundle['dirs']), 'Staged copy differs')
            write_new(pending, encoded(new), made_files)
        if old is not None:
            require(verify_at(skill, receipt, name) == (old, old_tree), 'Installation changed during preparation')
            safe_path(skill).rename(backup)
            moved_old = True
            safe_path(receipt).rename(old_record)
            moved_record = True
        if bundle:
            require(not skill.exists() and not receipt.exists(), 'Destination appeared during transaction')
            staged.rename(skill)
            installed = True
            pending.rename(receipt)
            recorded = True
            verify_at(skill, receipt, name)
        committed = True
    except BaseException as error:
        failures = []
        try:
            if recorded:
                require(safe_path(receipt).read_bytes() == encoded(new), 'New receipt changed')
                receipt.unlink()
            if installed:
                delete_exact(skill, (bundle['files'], bundle['dirs']))
            if moved_record:
                require(not receipt.exists(), 'Receipt occupied during recovery')
                safe_path(old_record).rename(receipt)
            if moved_old:
                require(not skill.exists(), 'Skill occupied during recovery')
                safe_path(backup).rename(skill)
        except (OSError, ValueError) as recovery:
            failures.append(str(recovery))
        # Only paths created by this invocation. Empty dirs only; never remove preexisting files.
        if not failures:
            for path in reversed(made_files):
                if path == lock:
                    continue
                try:
                    if path.exists():
                        safe_path(path).unlink()
                except (OSError, ValueError) as cleanup:
                    failures.append(str(cleanup))
            for path in reversed(made_dirs):
                if path in (state, target) or path in state.parents:
                    continue
                try:
                    if path.exists():
                        safe_path(path).rmdir()
                except (OSError, ValueError) as cleanup:
                    failures.append(str(cleanup))
        if failures:
            raise OSError(f'{error}; recovery incomplete; retain {transaction}: ' + '; '.join(failures)) from error
        raise
    finally:
        if locked or lock in made_files:
            safe_path(lock).unlink()
        if not committed:
            for path in reversed(made_dirs):
                try:
                    if path.exists():
                        safe_path(path).rmdir()
                except (OSError, ValueError):
                    pass  # Never recursively remove remnants; report original/recovery error.
    # Commit completed. Cleanup errors preserve the new state and report the recovery directory.
    try:
        if moved_old:
            delete_exact(backup, old_tree)
        if moved_record:
            require(read_json(old_record) == old, 'Backup record changed')
            old_record.unlink()
        transaction.rmdir()
    except (OSError, ValueError) as error:
        raise OSError(f'{action} committed, cleanup incomplete at {transaction}: {error}') from error
    return f'PASS: {action} {name}'


def pack(name, output, root=ROOT):
    bundle = package(name, root)
    output = safe_path(output)
    for source, _ in EXPECTED.values():
        require(not output.is_relative_to(safe_path(root / source)), 'Output cannot be inside a Skill source')
    payload = archive(bundle)
    filename = f'{name}-{bundle["version"]}-{bundle["channel"]}.zip'
    products = {output / filename: payload,
                output / (filename + '.sha256'): (sha(payload) + '  ' + filename + '\n').encode('ascii')}
    for path, content in products.items():
        safe_path(path)
        require(not path.exists() or (path.is_file() and path.read_bytes() == content),
                f'Output conflict; choose a new output directory: {path}')
    dirs, files = [], []
    try:
        mkdirs(output, dirs)
        for path, content in products.items():
            if not path.exists():
                write_new(path, content, files)
    except BaseException:
        for path in reversed(files):
            safe_path(path).unlink()
        for path in reversed(dirs):
            safe_path(path).rmdir()
        raise
    return f'PASS: {output / filename}\nSHA256: {sha(payload)}'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    for name in ('pack', 'install', 'verify', 'upgrade', 'remove'):
        command = sub.add_parser(name)
        command.add_argument('--skill', required=True, choices=tuple(EXPECTED))
        command.add_argument('--output-dir' if name == 'pack' else '--target-dir', required=True, type=Path)
        if name in ('install', 'upgrade', 'remove'):
            command.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'list':
            for name, item in catalog().items():
                bundle = package(name, require_installable=False)
                print(f'{name}\t{bundle["version"]}\t{item["channel"]}\t{item["source_dir"]}\tinstallable={item["installable"]}')
        elif args.command == 'pack':
            print(pack(args.skill, args.output_dir))
        elif args.command == 'verify':
            print(verify(args.skill, args.target_dir))
        else:
            print(manage(args.command, args.skill, args.target_dir, args.apply))
        return 0
    except (OSError, ValueError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
