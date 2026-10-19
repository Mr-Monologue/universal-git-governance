"""Synchronize distribution copies; --check never writes files."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = Path('skills/embedded-c-module')
REFERENCE_NAMES = ('C_CODING_STANDARD.md', 'REVIEW_CHECKLIST.md',
                   'OPEN_DECISIONS.md', 'CHANGE_REVIEW.md', 'STYLE_DECISION_REVIEW.md',
                   'examples/style-review/README.md')
COPIES = {Path('standards/embedded-c') / name: SKILL_PATH / 'references' / name
          for name in REFERENCE_NAMES}
COPIES[Path('LICENSE')] = SKILL_PATH / 'LICENSE'


def sync(root: Path = ROOT, check: bool = False) -> list[str]:
    root = root.resolve()
    pairs = [(root / source, root / target) for source, target in COPIES.items()]
    # Pre-read all sources and reject links before allowing any write.
    for source, target in pairs:
        if (not source.is_file() or not source.resolve().is_relative_to(root)
                or target.is_symlink() or not target.resolve().is_relative_to(root)):
            raise ValueError(f'Unsafe or missing synchronization path: {source} -> {target}')
    contents = [(source, target, source.read_bytes()) for source, target in pairs]
    errors = []
    for source, target, data in contents:
        if target.is_file() and target.read_bytes() == data:
            continue
        if check:
            errors.append(f'Distribution copy differs or is missing: {target.relative_to(root)}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return errors


def main(argv=None) -> int:
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
    print(f'PASS: {len(COPIES)} distribution copies {"match sources" if args.check else "synchronized"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
