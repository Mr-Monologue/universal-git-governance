"""Read-only repository/package validation using the existing Markdown/YAML checks."""
import argparse
from pathlib import Path
import re
import runpy
from string import Template
import sys
import yaml

if __package__:
    from .validate import frontmatter
    from .validate_embedded_c import check_document
    from .sync_embedded_project_skill import COPIES, ROOT, SKILL, sync
else:
    from validate import frontmatter
    from validate_embedded_c import check_document
    from sync_embedded_project_skill import COPIES, ROOT, SKILL, sync

REQUIRED = ('SKILL.md', 'README.md', 'LICENSE', 'references/PROFILE_GUIDE.md',
            'scripts/init_project.py', 'scripts/validate_project.py', 'scripts/project_common.py',
            'assets/profiles/firmware.json', 'assets/profiles/embedded-fullstack.json',
            'assets/profiles/robotics.json', 'assets/templates/README.md.tpl', 'assets/templates/gitignore.tpl')


def validate(skill=ROOT / SKILL):
    skill = skill.resolve()
    errors = []
    for name in REQUIRED:
        path = skill / name
        if not path.is_file() or not path.resolve().is_relative_to(skill):
            errors.append(f'Missing or external Skill file: {name}')
    if errors:
        return errors
    common = runpy.run_path(str(skill / 'scripts/project_common.py'))
    common['scan_target'](skill)
    data = frontmatter(skill / 'SKILL.md')
    if data.get('name') != skill.name or skill.name != 'embedded-project-init':
        errors.append('Skill directory/name mismatch')
    if not isinstance(data.get('description'), str) or not 0 < len(data['description'].strip()) <= 1024:
        errors.append('Invalid description')
    if data.get('metadata') != {'version': '0.1.0', 'status': 'draft'}:
        errors.append('Expected Draft 0.1.0 metadata')
    for path in skill.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        if re.search(r'(?i)\b[a-z]:[\\/]|/(?:Users|home)/[^\s/]+/', text):
            errors.append(f'Machine-specific absolute path: {path.relative_to(skill)}')
        if path.suffix == '.md':
            errors.extend(check_document(path, skill, text))
    profiles = {key: common['load_profile'](key, skill / 'assets') for key in common['PROFILES']}
    for base, expanded in (('firmware', 'embedded-fullstack'), ('embedded-fullstack', 'robotics')):
        if not set(profiles[base]['directories']) < set(profiles[expanded]['directories']):
            errors.append(f'Profile inclusion broken: {base} -> {expanded}')
    for key, profile in profiles.items():
        common['render_files'](profile, 'Example Project', skill / 'assets')
        if key != 'robotics' and any(p.startswith('10_Course') for p in profile['directories']):
            errors.append(f'Unexpected Course in {key}')
    for name in ('README.md.tpl', 'gitignore.tpl'):
        text = (skill / 'assets/templates' / name).read_text(encoding='utf-8')
        template = Template(text)
        if not template.is_valid() or not set(template.get_identifiers()) <= {'name', 'profile', 'description', 'modules'}:
            errors.append(f'Unsafe or unknown template placeholders: {name}')
    ignores = (skill / 'assets/templates/gitignore.tpl').read_text(encoding='utf-8')
    if re.search(r'(?im)^\s*\*?\.(?:bin|hex|pdf)\s*$', ignores):
        errors.append('Template ignores engineering deliverables')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir', type=Path)
    args = parser.parse_args(argv)
    try:
        errors = validate(args.skill_dir or ROOT / SKILL)
        if args.skill_dir is None:
            errors.extend(sync(check=True))
            path = ROOT / 'templates/embedded-project/README.md'
            errors.extend(check_document(path, ROOT, path.read_text(encoding='utf-8')))
    except (OSError, ValueError, KeyError, UnicodeError, yaml.YAMLError) as error:
        errors = [str(error)]
    if errors:
        print('\n'.join('FAIL: ' + error for error in errors), file=sys.stderr)
        return 1
    print('PASS: project Skill metadata, links, safe profiles/templates and distribution checks')
    return 0


if __name__ == '__main__':
    sys.exit(main())
