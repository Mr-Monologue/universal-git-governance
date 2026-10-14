"""Copy canonical templates into the standalone Skill; --check is read-only."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path('skills/embedded-project-init')
SOURCE = Path('templates/embedded-project')
PROFILES = ('firmware', 'embedded-fullstack', 'robotics')
COPIES = {SOURCE / 'profiles' / f'{name}.json': SKILL / 'assets/profiles' / f'{name}.json'
          for name in PROFILES}
COPIES.update({SOURCE / 'assets' / name: SKILL / 'assets/templates' / name
               for name in ('README.md.tpl', 'gitignore.tpl')})
COPIES[Path('LICENSE')] = SKILL / 'LICENSE'


def safe(path, root):
    if not path.resolve().is_relative_to(root):
        raise ValueError(f'External synchronization path: {path}')
    for component in (path, *path.parents):
        if component == root:
            break
        if component.exists() or component.is_symlink():
            info = component.lstat()
            if component.is_symlink() or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError(f'Linked synchronization path: {component}')


def sync(root=ROOT, check=False):
    root = root.resolve()
    expected = {root / target for target in COPIES.values()}
    assets = root / SKILL / 'assets'
    safe(assets, root)
    if assets.exists():
        for path in assets.rglob('*'):
            safe(path, root)
            if not path.is_dir() and path not in expected:
                raise ValueError(f'Unexpected distribution file; review manually: {path}')
    contents = []
    for source, target in COPIES.items():
        source, target = root / source, root / target
        safe(source, root)
        safe(target, root)
        contents.append((target, source.read_bytes()))
    errors = []
    for target, data in contents:
        if target.is_file() and target.read_bytes() == data:
            continue
        if check:
            errors.append(f'Missing or drifting copy: {target.relative_to(root)}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        errors = sync(check=args.check)
    except (OSError, ValueError) as error:
        errors = [str(error)]
    if errors:
        print('\n'.join('FAIL: ' + error for error in errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(COPIES)} project Skill distribution copies {"match" if args.check else "synchronized"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
