"""Distribution acceptance tests use external temporary fixtures, never user projects."""
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import skill_dist as dist
from scripts import skill_dist_support as support
from scripts import validate_skill_distribution as validator


def snapshot(path):
    return {str(p.relative_to(path)): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
            for p in (path, *path.rglob('*'))} if path.exists() else None


class DistributionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='skill-distribution-')
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.repo = self.base / 'source'
        self.repo.mkdir()
        for name in ('catalog', 'git-governance', 'skills/embedded-c-module',
                     'skills/embedded-project-init', 'standards', 'templates'):
            shutil.copytree(support.ROOT / name, self.repo / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copyfile(support.ROOT / 'LICENSE', self.repo / 'LICENSE')
        self.target = self.base / '隔离 project' / '.agents' / 'skills'
        self.name = 'embedded-project-init'

    def manage(self, action, apply=False, name=None):
        return dist.manage(action, name or self.name, self.target, apply, self.repo)

    def edit_catalog(self, mutate):
        path = self.repo / 'catalog/skills.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        mutate(data)
        path.write_bytes(support.encoded(data))

    def test_catalog_and_all_sources_pass(self):
        validator.validate(self.repo)
        self.assertEqual(set(support.catalog(self.repo)), set(support.EXPECTED))

    def test_disabled_catalog_entry_cannot_install_or_pack(self):
        self.edit_catalog(lambda data: data['skills'][0].update(installable=False))
        validator.validate(self.repo)
        for action in (lambda: dist.pack('git-governance', self.base / 'packages', self.repo),
                       lambda: self.manage('install', True, 'git-governance')):
            with self.assertRaises(ValueError):
                action()
        self.assertFalse(self.target.exists())

    def test_invalid_catalog_entries(self):
        path = self.repo / 'catalog/skills.json'
        original = path.read_bytes()
        mutations = [lambda d: d['skills'].append(d['skills'][0]),
                     lambda d: d['skills'].pop(),
                     lambda d: d['skills'][0].update(source_dir='../outside'),
                     lambda d: d['skills'][0].update(source_dir='/absolute'),
                     lambda d: d['skills'][0].update(source_dir='missing'),
                     lambda d: d['skills'][0].update(channel='preview'),
                     lambda d: d['skills'][0].update(installable='true'),
                     lambda d: d['skills'][0].update(name='unknown'),
                     lambda d: d.update(schema_version=True)]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                path.write_bytes(original)
                self.edit_catalog(mutate)
                with self.assertRaises(ValueError):
                    support.catalog(self.repo)
        path.write_text('{"skills":[],"skills":[]}', encoding='utf-8')
        with self.assertRaises(ValueError):
            support.catalog(self.repo)

    def test_missing_source_resource_license_and_drift(self):
        paths = ['git-governance/SKILL.md', 'git-governance/LICENSE',
                 'skills/embedded-c-module/assets/module.h.tpl',
                 'skills/embedded-project-init/scripts/project_common.py']
        for name in paths:
            path = self.repo / name
            original = path.read_bytes()
            path.unlink()
            with self.subTest(path=name), self.assertRaises(ValueError):
                validator.validate(self.repo)
            path.write_bytes(original)
        path = self.repo / 'templates/embedded-project/assets/README.md.tpl'
        path.write_bytes(path.read_bytes() + b'\nnew source\n')
        before = snapshot(self.base)
        with self.assertRaisesRegex(ValueError, 'drift'):
            self.manage('install', True)
        self.assertEqual(snapshot(self.base), before)

    def test_metadata_and_links_and_machine_paths_fail(self):
        path = self.repo / 'git-governance/SKILL.md'
        original = path.read_bytes()
        for content in [original.replace(b'name: git-governance', b'name: wrong'),
                        original + b'\n[Bad](missing.md)\n',
                        original + b'\nC:/private/workspace\n']:
            path.write_bytes(content)
            with self.assertRaises(ValueError):
                support.package('git-governance', self.repo)

    def test_all_archives_reproducible_correct_root_and_resources(self):
        for name in support.EXPECTED:
            with self.subTest(name=name):
                one, two = self.base / ('one ' + name), self.base / ('two ' + name)
                dist.pack(name, one, self.repo)
                source = self.repo / support.EXPECTED[name][0]
                for path in source.rglob('*'):
                    os.utime(path, (1234567890, 1234567890))
                dist.pack(name, two, self.repo)
                first, second = next(one.glob('*.zip')), next(two.glob('*.zip'))
                self.assertEqual(first.read_bytes(), second.read_bytes())
                self.assertEqual(support.validate_archive(first.read_bytes(), name), support.package(name, self.repo)['files'])
                self.assertIn(support.sha(first.read_bytes()), next(one.glob('*.sha256')).read_text())
                before = snapshot(one)
                dist.pack(name, one, self.repo)
                self.assertEqual(snapshot(one), before)

    def test_excludes_caches_and_temp_files(self):
        source = self.repo / 'git-governance'
        for name in ('.git', '.venv', '__pycache__'):
            (source / name).mkdir()
            (source / name / 'secret').write_bytes(b'no')
        (source / 'private.tmp').write_bytes(b'no')
        files = support.package('git-governance', self.repo)['files']
        self.assertFalse(any('secret' in key or key.endswith('.tmp') for key in files))

    def test_links_to_excluded_resources_fail(self):
        source = self.repo / 'git-governance'
        (source / 'omitted.tmp').write_bytes(b'temporary')
        entry = source / 'SKILL.md'
        entry.write_bytes(entry.read_bytes() + b'\n[Resource](omitted.tmp)\n')
        with self.assertRaises(ValueError):
            support.package('git-governance', self.repo)

    def test_unsafe_zip_members_rejected(self):
        for name, mode in [('../escape', stat.S_IFREG), ('/absolute', stat.S_IFREG),
                           ('C:/absolute', stat.S_IFREG), ('git-governance/a\\b', stat.S_IFREG),
                           ('git-governance/link', stat.S_IFLNK), ('other/file', stat.S_IFREG)]:
            with self.subTest(name=name):
                output = io.BytesIO()
                with zipfile.ZipFile(output, 'w') as zipped:
                    info = zipfile.ZipInfo(name)
                    info.external_attr = (mode | 0o644) << 16
                    zipped.writestr(info, b'unsafe')
                with self.assertRaises(ValueError):
                    support.validate_archive(output.getvalue(), 'git-governance')

    def test_install_preview_apply_repeat_verify_all_skills(self):
        for name in support.EXPECTED:
            with self.subTest(name=name):
                before = snapshot(self.base)
                self.assertIn('DRY RUN', self.manage('install', name=name))
                self.assertEqual(snapshot(self.base), before)
                self.manage('install', True, name)
                self.assertIn('PASS', dist.verify(name, self.target, self.repo))
                before = snapshot(self.target)
                self.assertIn('UNCHANGED', self.manage('install', True, name))
                self.assertEqual(snapshot(self.target), before)

    def test_unmanaged_install_and_remove_refused(self):
        path = self.target / self.name
        path.mkdir(parents=True)
        (path / 'user.txt').write_bytes(b'keep')
        before = snapshot(self.target)
        for action in ('install', 'remove', 'upgrade'):
            with self.assertRaises(ValueError):
                self.manage(action, True)
        self.assertEqual(snapshot(self.target), before)

    def test_modified_missing_extra_file_and_empty_dir_block_management(self):
        self.manage('install', True)
        skill = self.target / self.name
        for kind in ('changed', 'missing', 'extra', 'directory'):
            with self.subTest(kind=kind):
                entry = skill / 'SKILL.md'
                original = entry.read_bytes()
                if kind == 'changed':
                    entry.write_bytes(b'user edit')
                elif kind == 'missing':
                    entry.unlink()
                elif kind == 'extra':
                    (skill / 'extra.txt').write_bytes(b'keep')
                else:
                    (skill / 'empty').mkdir()
                before = snapshot(self.target)
                for action in ('install', 'upgrade', 'remove'):
                    with self.assertRaises(ValueError):
                        self.manage(action, True)
                self.assertEqual(snapshot(self.target), before)
                entry.write_bytes(original)
                if kind == 'extra':
                    (skill / 'extra.txt').unlink()
                if kind == 'directory':
                    (skill / 'empty').rmdir()

    def test_upgrade_preview_and_changed_fixture_success(self):
        self.manage('install', True)
        source = self.repo / 'skills/embedded-project-init/README.md'
        source.write_bytes(source.read_bytes() + b'\nFixture revision\n')
        before = snapshot(self.base)
        self.assertIn('DRY RUN', self.manage('upgrade'))
        self.assertEqual(snapshot(self.base), before)
        self.manage('upgrade', True)
        self.assertEqual((self.target / self.name / 'README.md').read_bytes(), source.read_bytes())
        dist.verify(self.name, self.target, self.repo)
        before = snapshot(self.target)
        self.assertIn('UNCHANGED', self.manage('upgrade', True))
        self.assertEqual(snapshot(self.target), before)

    def test_remove_preview_and_apply_preserve_other_installs(self):
        self.manage('install', True)
        self.manage('install', True, 'git-governance')
        other = self.target / 'user-skill'
        other.mkdir()
        (other / 'user.txt').write_bytes(b'keep')
        before = snapshot(self.target)
        self.assertIn('DRY RUN', self.manage('remove'))
        self.assertEqual(snapshot(self.target), before)
        self.manage('remove', True)
        self.assertFalse((self.target / self.name).exists())
        self.assertEqual((other / 'user.txt').read_bytes(), b'keep')
        dist.verify('git-governance', self.target, self.repo)

    def test_install_partial_write_failure_preserves_preexisting_files(self):
        self.target.mkdir(parents=True)
        keep = self.target / 'user.txt'
        keep.write_bytes(b'keep')
        with patch.object(dist.os, 'fsync', side_effect=[None, None, OSError('disk full')]):
            with self.assertRaises(OSError):
                self.manage('install', True)
        self.assertEqual(list(self.target.iterdir()), [keep])
        self.assertEqual(keep.read_bytes(), b'keep')

    def test_lock_write_failure_removes_only_new_paths(self):
        with patch.object(dist.os, 'fsync', side_effect=OSError('injected lock flush failure')):
            with self.assertRaises(OSError):
                self.manage('install', True)
        self.assertFalse(self.target.exists())

    def test_upgrade_failure_restores_original_files_and_receipt(self):
        self.manage('install', True)
        original = support.tree(self.target)
        source = self.repo / 'skills/embedded-project-init/README.md'
        source.write_bytes(source.read_bytes() + b'\nFixture update\n')
        rename = Path.rename
        def fail(path, target):
            if path.name == 'record.json':
                raise OSError('injected receipt promotion failure')
            return rename(path, target)
        with patch.object(Path, 'rename', fail), self.assertRaises(OSError):
            self.manage('upgrade', True)
        self.assertEqual(support.tree(self.target), original)
        dist.verify(self.name, self.target, self.repo)

    def test_remove_failure_restores_original(self):
        self.manage('install', True)
        original = support.tree(self.target)
        rename = Path.rename
        def fail(path, target):
            if path.name == self.name + '.json':
                raise OSError('injected record rename failure')
            return rename(path, target)
        with patch.object(Path, 'rename', fail), self.assertRaises(OSError):
            self.manage('remove', True)
        self.assertEqual(support.tree(self.target), original)

    def test_invalid_paths_and_same_name_files(self):
        for path in (self.base / '..' / 'escape', self.repo / 'installed', self.base / 'NUL', self.base / 'bad:ads'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                dist.manage('install', self.name, path, True, self.repo)
        self.target.parent.mkdir(parents=True)
        self.target.write_bytes(b'user file')
        with self.assertRaises(ValueError):
            self.manage('install', True)
        self.assertEqual(self.target.read_bytes(), b'user file')

    def test_pending_transaction_and_corrupt_record_stop(self):
        self.manage('install', True)
        state = self.target / dist.MANAGEMENT
        (state / 'lock').write_bytes(b'other process')
        with self.assertRaises(ValueError):
            self.manage('remove', True)
        (state / 'lock').unlink()
        receipt = state / (self.name + '.json')
        receipt.write_text('{}', encoding='utf-8')
        before = snapshot(self.target)
        with self.assertRaises(ValueError):
            self.manage('remove', True)
        self.assertEqual(snapshot(self.target), before)

    def test_cli_preview_is_read_only_and_exit_codes_are_explicit(self):
        command = [sys.executable, '-X', 'utf8', str(support.ROOT / 'scripts/skill_dist.py')]
        before = snapshot(self.base)
        result = subprocess.run(command + ['install', '--skill', self.name, '--target-dir', str(self.target)],
                                cwd=self.base, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b'DRY RUN', result.stdout)
        self.assertEqual(snapshot(self.base), before)
        result = subprocess.run(command + ['verify', '--skill', self.name, '--target-dir', str(self.target)],
                                cwd=self.base, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(snapshot(self.base), before)
        result = subprocess.run(command + ['install', '--skill', self.name], cwd=self.base, capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_actual_symlink_target_and_source_rejected(self):
        outside = self.base / 'outside'
        outside.mkdir()
        link = self.base / 'link'
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f'NOT RUN: symlink unavailable: {error}')
        self.addCleanup(link.unlink)
        with self.assertRaises(ValueError):
            dist.manage('install', self.name, link / 'skills', True, self.repo)
        source_link = self.repo / 'git-governance/linked'
        source_link.symlink_to(outside, target_is_directory=True)
        self.addCleanup(source_link.unlink)
        with self.assertRaises(ValueError):
            support.package('git-governance', self.repo)
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipUnless(os.name == 'nt', 'Windows junction scenario')
    def test_actual_junction_target_and_source_rejected(self):
        outside = self.base / 'outside'
        outside.mkdir()
        for link in (self.base / 'linked target', self.repo / 'git-governance/linked'):
            result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(outside)], capture_output=True)
            if result.returncode:
                self.skipTest('NOT RUN: junction creation unavailable')
            self.addCleanup(os.rmdir, link)
            if link.parent == self.base:
                with self.assertRaises(ValueError):
                    dist.manage('install', self.name, link / 'skills', True, self.repo)
            else:
                with self.assertRaises(ValueError):
                    support.package('git-governance', self.repo)
        self.assertEqual(list(outside.iterdir()), [])

    def test_installed_skills_run_without_source(self):
        for name in support.EXPECTED:
            self.manage('install', True, name)
        self.repo.rename(self.base / 'unavailable-source')
        module = self.target / 'embedded-c-module/scripts/new_c_module.py'
        init = self.target / 'embedded-project-init/scripts/init_project.py'
        check = init.with_name('validate_project.py')
        for script, args in [(module, ['--module', 'sample_module', '--output', str(self.base / 'C 模块')]),
                             (init, ['--target', str(self.base / '空 project'), '--name', 'Example', '--profile', 'firmware']),
                             (check, ['--target', str(self.base / '空 project'), '--profile', 'firmware'])]:
            result = subprocess.run([sys.executable, '-I', '-B', str(script), *args], cwd=self.base,
                                    capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.base / 'C 模块/sample_module.c').is_file())
        self.assertTrue((self.base / 'C 模块/sample_module.h').is_file())
        for name in support.EXPECTED:
            dist.verify(name, self.target, self.repo)


if __name__ == '__main__':
    unittest.main()
