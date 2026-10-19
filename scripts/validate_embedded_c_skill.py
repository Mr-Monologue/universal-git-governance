"""Read-only Skill package validation, reusable for an isolated installed copy."""
import argparse
from pathlib import Path
import re
import sys

if __package__:
    from .validate import frontmatter
    from .validate_embedded_c import (check_document, check_metadata, check_decisions,
                                     check_doxygen_standard, check_doxygen_block, require_text,
                                     check_unapproved_claims, check_approved_defaults, check_format_config)
    from .sync_embedded_c_skill import sync
else:
    from validate import frontmatter
    from validate_embedded_c import (check_document, check_metadata, check_decisions,
                                    check_doxygen_standard, check_doxygen_block, require_text,
                                    check_unapproved_claims, check_approved_defaults, check_format_config)
    from sync_embedded_c_skill import sync
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/embedded-c-module'
REQUIRED = ('SKILL.md', 'README.md', 'LICENSE', 'assets/module.h.tpl', 'assets/module.c.tpl',
            'scripts/new_c_module.py', 'references/C_CODING_STANDARD.md',
            'references/REVIEW_CHECKLIST.md', 'references/OPEN_DECISIONS.md',
            'references/CHANGE_REVIEW.md', 'references/STYLE_DECISION_REVIEW.md',
            'references/examples/style-review/README.md', 'references/config/.clang-format')


def validate(skill: Path = SKILL) -> list[str]:
    skill = skill.resolve()
    errors = []
    for name in REQUIRED:
        path = skill / name
        if not path.is_file() or not path.resolve().is_relative_to(skill):
            errors.append(f'Missing or external Skill file: {name}')
    if errors:
        return errors
    data = frontmatter(skill / 'SKILL.md')
    if data.get('name') != skill.name or data.get('name') != 'embedded-c-module':
        errors.append('Skill name must match embedded-c-module directory')
    description = data.get('description')
    if not isinstance(description, str) or not 0 < len(description.strip()) <= 1024:
        errors.append('Skill description must be nonempty and <=1024 characters')
    metadata = data.get('metadata')
    if not isinstance(metadata, dict) or metadata.get('version') != '0.1.0' or metadata.get('status') != 'draft':
        errors.append('Skill metadata must be version 0.1.0 / draft')
    for path in sorted(skill.rglob('*.md')):
        if not path.resolve().is_relative_to(skill):
            errors.append(f'External Markdown file: {path.name}')
            continue
        text = path.read_text(encoding='utf-8')
        errors.extend(check_document(path, skill, text))
        errors.extend(check_unapproved_claims(text, path.relative_to(skill)))
        if re.search(r'(?i)\b[a-z]:[\\/]|/(?:Users|home)/[^\s/]+/', text):
            errors.append(f'Machine-specific path in {path.name}')
    errors.extend(check_metadata((skill / 'references/C_CODING_STANDARD.md').read_text(encoding='utf-8')))
    errors.extend(check_doxygen_standard((skill / 'references/C_CODING_STANDARD.md').read_text(encoding='utf-8'),
                                        'references/C_CODING_STANDARD.md'))
    for name in ('OPEN_DECISIONS.md', 'STYLE_DECISION_REVIEW.md'):
        errors.extend(check_decisions((skill / 'references' / name).read_text(encoding='utf-8'),
                                      'references/' + name, review=name.startswith('STYLE_')))
    errors.extend(check_approved_defaults((skill / 'references/C_CODING_STANDARD.md').read_text(encoding='utf-8'), 'references/C_CODING_STANDARD.md'))
    errors.extend(check_format_config((skill / 'references/config/.clang-format').read_text(encoding='utf-8')))
    entry = (skill / 'SKILL.md').read_text(encoding='utf-8')
    errors.extend(require_text(entry, 'SKILL.md', ('Doxygen 是强制要求', '既有正式规则优先',
                   '目标项目无正式规则时', '已批准默认值', '公开函数、类型', '单位', '范围', 'ISR/RTOS/DMA')))
    errors.extend(require_text((skill / 'README.md').read_text(encoding='utf-8'), 'README.md',
                               ('Doxygen 强制', '既有正式规则优先', 'Skill 保持 Draft / Preview')))
    for suffix in ('h', 'c'):
        name = f'assets/module.{suffix}.tpl'
        text = (skill / name).read_text(encoding='utf-8')
        errors.extend(check_doxygen_block(text, name, (f'@file ${{module}}.{suffix}', '@brief')))
        errors.extend(require_text(text, name, ('Draft',)))
        errors.extend(check_unapproved_claims(text, name))
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir', type=Path, default=SKILL)
    args = parser.parse_args(argv)
    try:
        errors = validate(args.skill_dir)
        if args.skill_dir == SKILL:
            errors.extend(sync(ROOT, check=True))
    except (OSError, ValueError, UnicodeError, yaml.YAMLError) as error:
        errors = [str(error)]
    if errors:
        print('\n'.join('FAIL: ' + error for error in errors), file=sys.stderr)
        return 1
    print('PASS: standalone Skill structure, YAML metadata, Markdown links/fences and Draft standard')
    return 0


if __name__ == '__main__':
    sys.exit(main())
