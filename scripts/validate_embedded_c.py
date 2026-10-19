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
             'CHANGE_REVIEW.md', 'OPEN_DECISIONS.md', 'STYLE_DECISION_REVIEW.md',
             'examples/style-review/README.md')
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


def require_text(text, path, fragments):
    """Bounded regression assertions, not natural-language policy interpretation."""
    return [f'{path}: missing required policy/contract fragment: {part}'
            for part in fragments if part not in text]


def check_decisions(text, path, review=False):
    errors = []
    expected = {f'C-STYLE-{i:02}' for i in range(1, 12)}
    if review:
        sections = re.findall(r'^## (C-STYLE-\d+) [^\n]*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
        ids = [key for key, _ in sections]
        for key, body in sections:
            errors.extend(require_text(body, f'{path}:{key}', ('状态：OPEN；推荐：PROPOSED。',)))
    else:
        rows = [line for line in text.splitlines() if re.match(r'^\| C-STYLE-', line)]
        ids = []
        for line in rows:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            ids.append(cells[0])
            if len(cells) != 5 or cells[-2:] != ['OPEN', 'PROPOSED']:
                errors.append(f'{path}:{cells[0]}: decision must remain OPEN / PROPOSED')
    if set(ids) != expected or len(ids) != len(expected):
        errors.append(f'{path}: expected exactly C-STYLE-01 through C-STYLE-11')
    errors.extend(check_unapproved_claims(text, path))
    return errors


def check_unapproved_claims(text, path):
    # Catch explicit status assertions; arbitrary prose still needs human review.
    patterns = (r'C-STYLE-\d+[^\n]*(?:ACCEPTED|APPROVED)',
                r'(?:K&R|Allman|100\s*列|4\s*空格|snake_case|C11)[^\n。;；]*(?:已批准|已冻结|全局强制)',
                r'Doxygen\s*(?:是|为|：|:)?\s*(?:可选|非强制|optional)')
    return [f'{path}: conflicting approval/Doxygen assertion: {match.group(0)}'
            for pattern in patterns for match in re.finditer(pattern, text, re.I)]


def check_doxygen_standard(text, path):
    return require_text(text, path, ('## 10. Doxygen 文档规范（强制）', '**本章为强制基线**',
                        '公开 `struct/enum/typedef`', '@param[in]', '@param[out]', '@retval',
                        '单位', '范围', 'ISR/RTOS/DMA API')) + check_unapproved_claims(text, path)


def check_doxygen_block(text, path, fragments):
    blocks = '\n'.join(re.findall(r'/\*\*(.*?)\*/', text, re.S))
    return require_text(blocks, path, fragments)


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
            errors.extend(check_doxygen_standard(text, name))
        if name in ('OPEN_DECISIONS.md', 'STYLE_DECISION_REVIEW.md'):
            errors.extend(check_decisions(text, name, review=name.startswith('STYLE_')))
        if name == 'config/.clang-format' and not re.search(r'(?i)draft|proposed', text):
            errors.append(f'{name}: configuration must remain Draft/Proposed')
        if name == 'examples/adc_scale.h':
            errors.extend(check_doxygen_block(text, name, ('@param[in] raw_code', '@param[in] full_scale_code',
                          '@param[in] reference_mv', '@param[out] result_mv', '@retval ADC_SCALE_OK',
                          '@retval ADC_SCALE_INVALID_ARG', '@note', 'mV', '范围')))
        if name in {f'examples/{item}' for item in EXAMPLES}:
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
    print(f'PASS: {len(REQUIRED)} Embedded C files; Markdown links/fences; OPEN/PROPOSED decisions; Draft 0.1.0 metadata; '
          '3 Doxygen file-header smoke checks (not full semantics or MISRA compliance)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
