"""Read-only validation; accepts additional user directories and edited README text."""
import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True  # Keep CLI validation read-only, including the Skill tree.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_common import (ASSETS, MANIFEST, VERSION, all_directories, load_profile,
                            project_name, read_json, scan_target, target_path)


def validate(target, profile_id, assets=ASSETS):
    profile = load_profile(profile_id, assets)
    target = target_path(target)
    scan_target(target)
    errors = []
    for name in all_directories(profile):
        if not (target / name).is_dir():
            errors.append(f'Missing directory: {name}')
    for name in ('README.md', '.gitignore', MANIFEST):
        if not (target / name).is_file():
            errors.append(f'Missing file: {name}')
    for name in profile['directories']:
        leaf = target / name
        if leaf.is_dir() and not any(p.name != '.gitkeep' for p in leaf.iterdir()):
            keep = leaf / '.gitkeep'
            if not keep.is_file() or keep.stat().st_size != 0:
                errors.append(f'Missing empty-leaf placeholder: {name}/.gitkeep')
    path = target / MANIFEST
    if path.is_file():
        data = read_json(path)
        if (not isinstance(data, dict) or type(data.get('schema_version')) is not int
                or data.get('schema_version') != 1 or data.get('generator_version') != VERSION
                or data.get('profile') != profile_id or data.get('directories') != profile['directories']):
            errors.append('Manifest does not match profile/schema/generator version')
        if isinstance(data, dict):
            project_name(data.get('project_name'))
    return errors


def main(argv=None):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--profile', required=True)
    args = parser.parse_args(argv)
    try:
        errors = validate(args.target, args.profile)
    except (OSError, ValueError, UnicodeError) as error:
        errors = [str(error)]
    if errors:
        print('\n'.join('FAIL: ' + error for error in errors), file=sys.stderr)
        return 1
    print(f'PASS: {args.profile} directories, metadata and empty-leaf placeholders')
    return 0


if __name__ == '__main__':
    sys.exit(main())
