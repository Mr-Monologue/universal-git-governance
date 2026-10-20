"""Read-only scaffold and local Markdown link validation (Python 3.11+).

Checks inline links and reference definitions outside fenced code in module
READMEs and root entrypoints. Remote URLs and fragment anchors are excluded;
local targets must exist inside the repository. Anchor headings are not checked.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('standards', 'skills', 'templates', 'tools', 'adapters',
           'handbook', 'examples', 'tests')
ENTRYPOINTS = ('README.md', 'AGENTS.md', 'git-governance/SKILL.md')


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors = []
    for name in MODULES:
        if not (root / name).is_dir():
            errors.append(f'Missing directory: {name}')
    documents = [root / name for name in ENTRYPOINTS]
    documents.extend(root / name / 'README.md' for name in MODULES)
    for path in documents:
        if not path.is_file():
            errors.append(f'Missing file: {path.relative_to(root)}')
            continue
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
        except (OSError, UnicodeError) as error:
            errors.append(f'Cannot read {path.relative_to(root)}: {error}')
            continue
        fence = None
        for number, line in enumerate(lines, 1):
            marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
            if marker:
                chars, rest = marker.groups()
                if fence is None:
                    fence = (chars[0], len(chars))
                elif chars[0] == fence[0] and len(chars) >= fence[1] and not rest.strip():
                    fence = None
                continue
            if fence is not None:
                continue
            targets = re.findall(r'\[[^\]\n]*\]\((<[^>]+>|[^)\n]+)\)', line)
            reference = re.match(r'^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)', line)
            if reference:
                targets.append(reference.group(1))
            for target in targets:
                target = target[1:-1] if target.startswith('<') else target.split()[0]
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or target.startswith('#'):
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve()
                if not resolved.is_relative_to(root) or not resolved.exists():
                    errors.append(f'{path.relative_to(root)}:{number}: invalid local link {target}')
        if fence is not None:
            errors.append(f'{path.relative_to(root)}: unclosed Markdown fence')
    return errors


def main() -> int:
    try:
        errors = validate(ROOT)
    except (OSError, ValueError) as error:
        errors = [str(error)]
    if errors:
        for error in errors:
            print(f'FAIL: {error}', file=sys.stderr)
        return 1
    print(f'PASS: {len(MODULES)} module directories; 11 required documents; local Markdown links')
    return 0


if __name__ == '__main__':
    sys.exit(main())
