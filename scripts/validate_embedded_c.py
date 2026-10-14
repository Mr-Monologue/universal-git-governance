"""Read-only Draft package smoke checks; not a C/Doxygen/MISRA analyzer.

Accepts a repository root for isolated tests. Checks inline Markdown links and
reference definitions outside code fences; URL destinations and heading anchors
are excluded. Frontmatter is deliberately limited to unique flat scalar fields,
matching this standard's metadata; it does not implement general YAML.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MODULE = Path('standards/embedded-c')
DOCUMENTS = ('README.md', 'C_CODING_STANDARD.md', 'REVIEW_CHECKLIST.md',
             'CHANGE_REVIEW.md', 'OPEN_DECISIONS.md')
EXAMPLES = ('adc_scale.h', 'adc_scale.c', 'test_adc_scale.c')
REQUIRED = (*DOCUMENTS, 'config/.clang-format',
            *(f'examples/{name}' for name in EXAMPLES))


def check_document(path: Path, root: Path, text: str) -> list[str]:
    errors = []
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            chars, rest = marker.groups()
            if fence is None:
                if chars[0] == '`' and '`' in rest:
                    errors.append(f'{path.name}:{number}: invalid code fence')
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
            try:
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or target.startswith('#'):
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve()
                if not resolved.is_relative_to(root) or not resolved.exists():
                    errors.append(f'{path.name}:{number}: invalid local link {target}')
            except ValueError:
                errors.append(f'{path.name}:{number}: invalid link {target}')
    if fence is not None:
        errors.append(f'{path.name}: unclosed code fence')
    return errors


def check_metadata(text: str) -> list[str]:
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not match:
        return ['C_CODING_STANDARD.md: missing or unclosed frontmatter']
    fields = {}
    for line in match.group(1).splitlines():
        item = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_-]*):\s+([^\r\n]+)', line)
        if not item:
            return ['C_CODING_STANDARD.md: malformed flat-scalar frontmatter']
        key, value = item.groups()
        value = value.strip()
        if key in fields or not value:
            return ['C_CODING_STANDARD.md: duplicate or empty frontmatter field']
        if value[0] in "\"'":
            if len(value) < 2 or value[-1] != value[0]:
                return ['C_CODING_STANDARD.md: malformed quoted frontmatter value']
            value = value[1:-1]
        elif any(char in value for char in '[]{}'):
            return ['C_CODING_STANDARD.md: frontmatter values must be scalar']
        fields[key] = value
    errors = []
    for key, expected in (('version', '0.1.0'), ('status', 'Draft')):
        if fields.get(key) != expected:
            errors.append(f'C_CODING_STANDARD.md: {key} must be {expected}')
    return errors


def validate(root: Path) -> list[str]:
    root = root.resolve()
    module = root / MODULE
    errors = []
    for name in REQUIRED:
        path = module / name
        if not path.is_file() or not path.resolve().is_relative_to(root):
            errors.append(f'Missing or external required file: {MODULE / name}')
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as error:
            errors.append(f'Cannot read {name}: {error}')
            continue
        if name in DOCUMENTS:
            errors.extend(check_document(path, root, text))
        if name == 'C_CODING_STANDARD.md':
            errors.extend(check_metadata(text))
        if name.startswith('examples/'):
            blocks = re.findall(r'/\*\*(.*?)\*/', text, re.S)
            file_header = any(
                re.search(r'@file\s+' + re.escape(path.name) + r'(?=\s|$)', block)
                and re.search(r'@brief\s+[^\s*]', block) for block in blocks)
            if not file_header:
                errors.append(f'{name}: missing Doxygen @file/@brief header')
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
    print('PASS: 9 Embedded C files; Markdown links/fences; Draft 0.1.0 metadata; '
          '3 Doxygen file-header smoke checks (not full semantics or MISRA compliance)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
