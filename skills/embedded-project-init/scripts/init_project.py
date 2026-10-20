"""Create a numbered project scaffold; no Git, installation or network actions."""
import argparse
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True  # Dry Run must not create a local import cache either.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_common import (ASSETS, all_directories, check_path, load_profile,
                            render_files, scan_target, target_path)


def plan(target, name, profile_id, assets=ASSETS):
    profile = load_profile(profile_id, assets)
    target = target_path(target)
    scan_target(target)
    directories = [target / name for name in all_directories(profile)]
    files = {target / name: data for name, data in render_files(profile, name, assets).items()}
    conflicts = []
    for path in directories:
        check_path(path)
        if path.exists() and not path.is_dir():
            conflicts.append(f'CONFLICT directory: {path}')
    if conflicts:
        return target, directories, files, conflicts
    for name in profile['directories']:
        leaf = target / name
        if not leaf.exists() or not any(p.name != '.gitkeep' for p in leaf.iterdir()):
            files[leaf / '.gitkeep'] = b''
    for path, data in files.items():
        check_path(path)
        if path.exists() and (not path.is_file() or path.read_bytes() != data):
            conflicts.append(f'CONFLICT file: {path}')
    return target, directories, files, conflicts


def initialize(target, name, profile_id, dry_run=False, assets=ASSETS):
    target, directories, files, conflicts = plan(target, name, profile_id, assets)
    actions = [('UNCHANGED' if p.exists() else 'CREATE') + f' directory: {p}' for p in directories]
    actions += [('UNCHANGED' if p.exists() and p.is_file() and p.read_bytes() == data
                 else 'CONFLICT' if p.exists() else 'CREATE')
                + f' file: {p}' for p, data in files.items() if not p.exists() or p.is_file()]
    if conflicts:
        return actions + conflicts, False  # Entire operation has no writes on a known conflict.
    if dry_run:
        return actions, True
    created_dirs, created_files = [], []
    try:
        missing = []
        parent = target
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        for path in [*reversed(missing), *directories]:
            check_path(path)
            if not path.exists():
                path.mkdir()
                created_dirs.append(path)
            elif not path.is_dir():
                raise FileExistsError(f'Directory conflict: {path}')
        for path, data in files.items():
            check_path(path)
            if path.exists():
                if not path.is_file() or path.read_bytes() != data:
                    raise FileExistsError(f'File changed after planning: {path}')
                continue
            if path.name == '.gitkeep' and any(path.parent.iterdir()):
                continue  # Do not add placeholders to a leaf that became nonempty.
            with path.open('xb') as stream:
                created_files.append(path)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException as error:
        failures = []
        for path in reversed(created_files):
            try:
                check_path(path)
                path.unlink()
            except (OSError, ValueError) as cleanup:
                failures.append(f'{path}: {cleanup}')
        for path in reversed(created_dirs):
            try:
                check_path(path)
                path.rmdir()
            except (OSError, ValueError) as cleanup:
                failures.append(f'{path}: {cleanup}')
        if failures:
            raise OSError(f'{error}; rollback incomplete: ' + '; '.join(failures)) from error
        raise
    return actions, True


def main(argv=None):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        actions, success = initialize(args.target, args.name, args.profile, args.dry_run)
        print('\n'.join(actions))
        print(('PASS' if success else 'FAIL') + (': dry run (no writes)' if args.dry_run else ': initialization'))
        return 0 if success else 1
    except (OSError, ValueError, KeyError, UnicodeError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
