"""Isolated CLI E2E validation; never accepts a user project as a target."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
if __package__:
    from .skill_dist_support import ROOT, EXPECTED, catalog, package, require, safe_path, sha, tree, validate_archive
    from .validate_embedded_c import check_decisions, check_doxygen_block
else:
    from skill_dist_support import ROOT, EXPECTED, catalog, package, require, safe_path, sha, tree, validate_archive
    from validate_embedded_c import check_decisions, check_doxygen_block


def contained(base, path):
    """Harness boundary, not a claim about the module generator's own policy."""
    base, path = safe_path(base), safe_path(path)
    require(path != base and path.is_relative_to(base), f'Outside E2E workspace: {path}')
    return path


def snapshot(path):
    """Include file mtimes to catch unnecessary rewrites; ignore directory mtimes."""
    path = safe_path(path)
    if not path.exists():
        return None
    result = {}
    for item in (path, *path.rglob('*')):
        safe_path(item)
        result[str(item.relative_to(path))] = ((item.read_bytes(), item.stat().st_mtime_ns)
                                              if item.is_file() else None)
    return result


@contextmanager
def workspace(keep=False):
    # Validate the tempfile parent before creating anything (TMP may point into a checkout).
    parent = safe_path(Path(tempfile.gettempdir()))
    require(not parent.is_relative_to(ROOT), 'Temporary parent must be outside repository')
    base = safe_path(Path(tempfile.mkdtemp(prefix='skill e2e ', dir=parent)))
    try:
        yield base
    finally:
        if not keep:
            require(base.parent == parent and base.name.startswith('skill e2e '), 'Unexpected cleanup root')
            snapshot(base)  # Refuse cleanup if a link/reparse point appeared.
            shutil.rmtree(base)  # Only the exact directory created above, never a caller-provided target.


class Evidence:
    def __init__(self, verbose=False):
        self.items = []
        self.commands = []
        self.verbose = verbose

    def add(self, layer, name, status, reason=''):
        self.items.append(dict(layer=layer, name=name, status=status, reason=reason))
        print(f'{status}: [{layer}] {name}' + (f' — {reason}' if reason else ''), flush=True)

    def command(self, args, cwd, expected=0):
        args = list(map(str, args))
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                                encoding='utf-8', errors='replace', timeout=120)
        self.commands.append(dict(argv=args, cwd=str(cwd), expected=expected,
                                  exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
        if self.verbose:
            print(json.dumps(self.commands[-1], ensure_ascii=False), flush=True)
        require(result.returncode == expected,
                f'Unexpected exit {result.returncode}, expected {expected}: {args}\n{result.stdout}{result.stderr}')
        return result

    def counts(self):
        return {status: sum(item['status'] == status for item in self.items)
                for status in ('PASS', 'FAIL', 'NOT RUN')}


def source_state():
    return {name: tree(ROOT / name, filter_source=True) for name in
            ('git-governance', 'skills', 'catalog', 'standards', 'templates')}


def copy_fixture(base):
    fixture = contained(base, base / 'source fixture')
    fixture.mkdir()
    for name in ('git-governance', 'skills', 'catalog', 'standards', 'templates', 'scripts'):
        files, dirs = tree(ROOT / name, filter_source=True)
        target = fixture / name
        target.mkdir()
        for relative in dirs:
            (target / relative).mkdir(parents=True, exist_ok=True)
        for relative, data in files.items():
            (target / relative).write_bytes(data)
    (fixture / 'LICENSE').write_bytes((ROOT / 'LICENSE').read_bytes())
    return fixture


def cli(evidence, base, script, *args, expected=0, standalone=False):
    flags = ['-I', '-S', '-B', '-X', 'utf8'] if standalone else ['-B', '-X', 'utf8']
    return evidence.command([sys.executable, *flags, script, *args], base, expected)


def distribute(base, fixture, target, evidence):
    manager = fixture / 'scripts/skill_dist.py'
    entries = catalog(fixture)
    cli(evidence, base, manager, 'list')
    for name in EXPECTED:
        require(entries[name]['installable'], f'{name} is not installable')
        bundle = package(name, fixture)
        payloads = []
        for iteration in ('one', 'two'):
            output = contained(base, base / ('packages ' + iteration))
            cli(evidence, base, manager, 'pack', '--skill', name, '--output-dir', output)
            archive = output / f'{name}-{bundle["version"]}-{bundle["channel"]}.zip'
            payload = archive.read_bytes()
            require(validate_archive(payload, name) == bundle['files'], 'ZIP/source mismatch')
            require(archive.with_suffix('.zip.sha256').read_text().split()[0] == sha(payload), 'ZIP hash mismatch')
            payloads.append(payload)
        require(payloads[0] == payloads[1], 'ZIP reproducibility failure')
        args = ['--skill', name, '--target-dir', contained(base, target)]
        before = snapshot(target)
        cli(evidence, base, manager, 'install', *args)
        require(snapshot(target) == before, 'Install dry run wrote files')
        cli(evidence, base, manager, 'install', *args, '--apply')
        require(tree(target / name) == (bundle['files'], bundle['dirs']), 'Installed payload mismatch')
        before = snapshot(target)
        cli(evidence, base, manager, 'verify', *args)
        repeat = cli(evidence, base, manager, 'install', *args, '--apply')
        require('UNCHANGED' in repeat.stdout and snapshot(target) == before, 'Install not idempotent/read-only')
        evidence.add('distribution', name, 'PASS', f'{bundle["version"]} / {bundle["channel"]}; reproducible ZIP, install, verify, repeat')


def check_scaffold(core, name):
    for suffix in ('h', 'c'):
        path = core / f'{name}.{suffix}'
        errors = check_doxygen_block(path.read_text(encoding='utf-8'), path.name,
                                      (f'@file {name}.{suffix}', '@brief'))
        require(not errors, '; '.join(errors))
    header = (core / f'{name}.h').read_text(encoding='utf-8')
    require(f'#ifndef {name.upper()}_H_' in header and f'#define {name.upper()}_H_' in header
            and '#endif' in header, 'Missing include guard')
    require('${' not in header and 'Draft' in header, 'Unrendered or non-Draft header')


def scenario(base, target, profile, evidence, compiler, doxygen):
    project = contained(base, base / (profile + ' test project'))
    init = target / 'embedded-project-init/scripts/init_project.py'
    check = init.with_name('validate_project.py')
    module = target / 'embedded-c-module/scripts/new_c_module.py'
    args = ['--target', project, '--name', 'E2E ' + profile, '--profile', profile]
    cli(evidence, base, init, *args, '--dry-run', standalone=True)
    require(not project.exists(), 'Project dry run wrote files')
    cli(evidence, base, init, *args, standalone=True)
    core = contained(base, project / '05_Firmware/Core')
    name = 'e2e_sample'
    before = snapshot(project)
    cli(evidence, base, module, '--module', name, '--output', core, '--dry-run', standalone=True)
    require(snapshot(project) == before, 'Module dry run wrote files')
    cli(evidence, base, module, '--module', name, '--output', core, standalone=True)
    check_scaffold(core, name)
    before = snapshot(project)
    cli(evidence, base, check, '--target', project, '--profile', profile, standalone=True)
    cli(evidence, base, init, *args, standalone=True)
    cli(evidence, base, module, '--module', name, '--output', core, expected=1, standalone=True)
    cli(evidence, base, module, '--module', '../invalid', '--output', core, expected=2, standalone=True)
    require(snapshot(project) == before, 'Repeat/invalid name/validation changed project')
    if profile == 'robotics':
        for folder in ('02_Motor', '03_Mechanical', '04_Hardware', '07_Simulation'):
            require((project / folder).is_dir(), f'Missing robotics area: {folder}')
            require(all(p.name == '.gitkeep' for p in (project / folder).rglob('*') if p.is_file()),
                    'Unexpected fabricated engineering asset')
    evidence.add('independent', profile, 'PASS', str(project) + '; isolated Python -I -S -B; repeat and overwrite protection')
    # Empty generator scaffold has no public API. Exercise an EXISTING documented API
    # from the installed reference as a separate fixture; never claim it was generated.
    reference = (target / 'embedded-c-module/references/examples/style-review/README.md').read_text(encoding='utf-8')
    contract = contained(base, base / (profile + ' contract fixture'))
    contract.mkdir()
    for marker, filename in (('header-100', 'style_sample.h'), ('source-attach', 'style_sample.c')):
        match = re.search(r'<!-- sample: ' + marker + r' -->\s*```c\n(.*?)```', reference, re.S)
        require(match is not None, 'Missing installed contract example')
        (contract / filename).write_text(match.group(1), encoding='utf-8')
    errors = check_doxygen_block((contract / 'style_sample.h').read_text(encoding='utf-8'), 'style_sample.h',
                                 ('@param[in]', '@param[out]', '@retval', '@pre', '@note', 'mV', 'ISR'))
    require(not errors, '; '.join(errors))
    evidence.add('independent', profile + ' Doxygen contract markers', 'PASS', 'installed reference example; scaffold has no business API')
    if compiler:
        evidence.command([compiler, '--version'], base)
        for source in (core / (name + '.c'), contract / 'style_sample.c'):
            output = contained(base, contract / (source.stem + '.o'))
            evidence.command([compiler, '-std=c11', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
                              '-Wsign-conversion', '-Werror', '-c', source, '-o', output], base)
        evidence.add('tools', profile + ' compile', 'PASS')
    else:
        evidence.add('tools', profile + ' compile', 'NOT RUN', 'GCC/Clang not found')
    if doxygen:
        evidence.command([doxygen, '--version'], base)
        config = contract / 'Doxyfile'
        inputs = [core / (name + '.h'), core / (name + '.c'), contract / 'style_sample.h', contract / 'style_sample.c']
        config.write_text('INPUT = ' + ' '.join('"' + str(p).replace('\\', '/') + '"' for p in inputs)
                          + '\nOUTPUT_DIRECTORY = "' + str(contract / 'docs').replace('\\', '/') + '"\n'
                          + 'INPUT_ENCODING = UTF-8\nEXTRACT_ALL = NO\nWARNINGS = YES\n'
                          + 'WARN_IF_UNDOCUMENTED = YES\nWARN_IF_DOC_ERROR = YES\nWARN_NO_PARAMDOC = YES\n'
                          + 'WARN_AS_ERROR = YES\nGENERATE_HTML = YES\nGENERATE_XML = YES\n'
                          + 'GENERATE_LATEX = NO\nHAVE_DOT = NO\nQUIET = YES\n', encoding='utf-8')
        evidence.command([doxygen, config], base)
        evidence.add('tools', profile + ' Doxygen', 'PASS', 'warning checks, not semantic/ISR proof')
    else:
        evidence.add('tools', profile + ' Doxygen', 'NOT RUN', 'Doxygen not found')


def safety(base, fixture, target, evidence):
    manager = fixture / 'scripts/skill_dist.py'
    init = target / 'embedded-project-init/scripts/init_project.py'
    name = 'embedded-c-module'
    path = target / name / 'SKILL.md'
    original = path.read_bytes()
    path.write_bytes(original + b'\nE2E tamper\n')
    before = snapshot(target)
    for action in ('verify', 'remove'):
        cli(evidence, base, manager, action, '--skill', name, '--target-dir', target,
            *(['--apply'] if action == 'remove' else []), expected=1)
    require(snapshot(target) == before, 'Tamper check modified installation')
    path.write_bytes(original)  # Restore ONLY our deliberately modified fixture.
    conflict = contained(base, base / 'conflict project')
    conflict.mkdir()
    (conflict / '05_Firmware').write_bytes(b'preserve existing file')
    before = snapshot(base)
    cli(evidence, base, init, '--target', conflict, '--name', 'Conflict', '--profile', 'firmware', expected=1, standalone=True)
    traversal = base / 'unexpected' / '..' / 'escape'
    cli(evidence, base, init, '--target', traversal, '--name', 'Traversal', '--profile', 'firmware', expected=1, standalone=True)
    cli(evidence, base, manager, 'install', '--skill', name, '--target-dir', traversal, '--apply', expected=1)
    for invalid in (traversal, base.parent / 'outside e2e', base):
        try:
            contained(base, invalid)
        except ValueError:
            pass
        else:
            raise ValueError('Harness accepted unexpected target')
    require(snapshot(base) == before, 'Rejected input wrote files')
    evidence.add('safety', 'tamper, conflicts, traversal, containment', 'PASS')
    for name in EXPECTED:
        before = snapshot(target)
        cli(evidence, base, manager, 'remove', '--skill', name, '--target-dir', target)
        require(snapshot(target) == before, 'Remove preview wrote files')
        others = {p.name: snapshot(p) for p in target.iterdir() if p.name not in (name, '.skill-dist')}
        cli(evidence, base, manager, 'remove', '--skill', name, '--target-dir', target, '--apply')
        require(not (target / name).exists(), 'Skill removal failed')
        require(all(snapshot(target / key) == value for key, value in others.items()), 'Removal changed unrelated content')
    evidence.add('distribution', 'safe removal', 'PASS', 'other Skills and unrelated sentinel preserved')


def run(keep=False, verbose=False, compiler=None, doxygen=None):
    evidence = Evidence(verbose)
    location = None
    try:
        before = source_state()
        with workspace(keep) as base:
            location = str(base)
            print('ISOLATION: ' + location, flush=True)
            try:
                fixture = copy_fixture(base)
                target = contained(base, base / 'agent test project/.agents/skills')
                target.mkdir(parents=True)
                (target / 'unrelated.txt').write_bytes(b'preserve unrelated user fixture')
                distribute(base, fixture, target, evidence)
                hidden = contained(base, base / 'unavailable source fixture')
                fixture.rename(hidden)
                try:
                    for profile in ('firmware', 'robotics'):
                        scenario(base, target, profile, evidence, compiler, doxygen)
                finally:
                    hidden.rename(fixture)
                safety(base, fixture, target, evidence)
                text = (ROOT / 'standards/embedded-c/OPEN_DECISIONS.md').read_text(encoding='utf-8')
                require(not check_decisions(text, 'OPEN_DECISIONS.md'), 'Decision status changed')
                evidence.add('policy', '11 ACCEPTED owner decisions', 'PASS')
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                evidence.add('workflow', 'E2E interrupted', 'FAIL', str(error))
                evidence.add('workflow', 'remaining dependent steps', 'NOT RUN', 'stopped after failure')
            finally:
                try:
                    unchanged = source_state() == before
                    evidence.add('policy', 'repository Skill/catalog/standard/template sources unchanged',
                                 'PASS' if unchanged else 'FAIL')
                except (OSError, ValueError) as error:
                    evidence.add('policy', 'source snapshot failed', 'FAIL', str(error))
                for agent in ('Codex', 'Cursor', 'GitHub Copilot'):
                    evidence.add('native-agent', agent, 'NOT RUN', 'no actual native discovery/invocation evidence; CLI is not Agent loading')
                (base / 'report.json').write_text(json.dumps(dict(isolation=location, kept=keep,
                    counts=evidence.counts(), checks=evidence.items, commands=evidence.commands),
                    ensure_ascii=False, indent=2), encoding='utf-8')
    except (OSError, ValueError) as error:
        evidence.add('workflow', 'source snapshot / workspace setup / cleanup', 'FAIL', str(error))
    print('SUMMARY: ' + json.dumps(evidence.counts()), flush=True)
    if location:
        print(('RETAINED: ' if Path(location).exists() else 'CLEANED: ') + location, flush=True)
    return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--keep-temp', action='store_true', help='Keep only this run\'s temporary workspace and report.json')
    parser.add_argument('--verbose', action='store_true', help='Print argv, cwd, exit, stdout and stderr for each command')
    parser.add_argument('--compiler', help='Existing GCC/Clang executable; otherwise search PATH')
    parser.add_argument('--doxygen', help='Existing Doxygen executable; otherwise search PATH')
    args = parser.parse_args(argv)
    evidence = run(args.keep_temp, args.verbose,
                   args.compiler or shutil.which('gcc') or shutil.which('clang'),
                   args.doxygen or shutil.which('doxygen'))
    return 1 if evidence.counts()['FAIL'] else 0


if __name__ == '__main__':
    sys.exit(main())
