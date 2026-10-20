"""Generate a C/H scaffold without overwriting existing paths (standard library)."""
import argparse
from contextlib import ExitStack
import os
from pathlib import Path
import re
from string import Template
import sys

SKILL = Path(__file__).resolve().parents[1]
C_KEYWORDS = set('auto break case char const continue default do double else enum extern '
                 'float for goto if inline int long register restrict return short signed '
                 'sizeof static struct switch typedef union unsigned void volatile while '
                 'alignas alignof bool constexpr false nullptr static_assert thread_local '
                 'true typeof typeof_unqual'.split())
DEVICE_NAMES = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)),
                *(f'lpt{i}' for i in range(1, 10))}


def render(module: str, skill: Path = SKILL) -> dict[str, str]:
    if (len(module) > 64 or not re.fullmatch(r'[a-z][a-z0-9]*(?:_[a-z0-9]+)*', module)
            or module in C_KEYWORDS | DEVICE_NAMES):
        raise ValueError('module must be portable snake_case, <=64 characters, not a reserved name')
    values = {'module': module, 'guard': module.upper() + '_H_'}
    return {f'{module}.{suffix}': Template(
        (skill / 'assets' / f'module.{suffix}.tpl').read_text(encoding='utf-8')
    ).substitute(values) for suffix in ('h', 'c')}


def generate(module: str, output: Path, dry_run: bool = False,
             skill: Path = SKILL) -> dict[Path, str]:
    contents = render(module, skill)  # Validate/render everything before any writes.
    output = output.absolute()
    targets = {output / name: text for name, text in contents.items()}
    for path in targets:
        if os.path.lexists(path):
            raise FileExistsError(f'Target already exists: {path}')
    missing_dirs = []
    ancestor = output
    while not ancestor.exists():
        missing_dirs.append(ancestor)
        ancestor = ancestor.parent
    if not ancestor.is_dir():
        raise NotADirectoryError(f'Output ancestor is not a directory: {ancestor}')
    if dry_run:
        return targets

    created_dirs = []
    created_files = []
    try:
        for directory in reversed(missing_dirs):
            directory.mkdir()
            created_dirs.append(directory)
        with ExitStack() as stack:
            streams = []
            # Exclusive creation also handles a target appearing after preflight.
            for path, text in targets.items():
                stream = path.open('x', encoding='utf-8', newline='\n')
                created_files.append(path)
                stack.enter_context(stream)
                streams.append((stream, text))
            for stream, text in streams:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException as error:
        cleanup_errors = []
        for path in reversed(created_files):
            try:
                path.unlink()
            except OSError as cleanup_error:
                cleanup_errors.append(f'{path}: {cleanup_error}')
        for directory in reversed(created_dirs):
            try:
                directory.rmdir()  # Never recursively delete anything.
            except OSError as cleanup_error:
                cleanup_errors.append(f'{directory}: {cleanup_error}')
        if cleanup_errors:
            raise OSError(f'{error}; rollback incomplete: ' + '; '.join(cleanup_errors)) from error
        raise
    return targets


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        targets = generate(args.module, args.output, args.dry_run)
    except (OSError, UnicodeError, ValueError, KeyError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 2 if isinstance(error, ValueError) else 1
    for path, text in targets.items():
        print(f'{"PREVIEW" if args.dry_run else "CREATED"}: {path} '
              f'({len(text.splitlines())} lines; Doxygen file header; no business API)')
    print('Draft scaffold only; complete the real API, contract, implementation and tests.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
