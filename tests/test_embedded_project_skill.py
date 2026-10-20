"""Project initialization behavior tested only in isolated external directories."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import sync_embedded_project_skill as syncer
from scripts import validate_embedded_project_skill as checker

SCRIPTS = checker.ROOT / checker.SKILL / 'scripts'
sys.path.insert(0, str(SCRIPTS))
try:
    import project_common as common
    import init_project as initializer
    import validate_project as project_validator
finally:
    sys.path.pop(0)


def snapshot(root):
    if not root.exists():
        return None
    return {str(p.relative_to(root)): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
            for p in (root, *root.rglob('*'))}


class EmbeddedProjectTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='project-init-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.skill = self.root / '独立 Skill' / 'embedded-project-init'
        shutil.copytree(checker.ROOT / checker.SKILL, self.skill, ignore=shutil.ignore_patterns('__pycache__'))
        self.assets = self.skill / 'assets'
        self.target = self.root / '项目 with spaces'

    def initialize(self, profile='firmware', dry_run=False):
        return initializer.initialize(self.target, '测试 Project', profile, dry_run, self.assets)

    def validate(self, profile='firmware'):
        return project_validator.validate(self.target, profile, self.assets)

    def cli(self, script, *args):
        return subprocess.run([sys.executable, '-I', '-X', 'utf8', str(self.skill / 'scripts' / script), *args],
                              cwd=self.root, capture_output=True, text=True, encoding='utf-8',
                              env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})

    def test_three_profiles_generate_exact_directory_sets_and_validate(self):
        for profile, leaf_count, directory_count in [('firmware', 11, 17), ('embedded-fullstack', 18, 26), ('robotics', 34, 46)]:
            with self.subTest(profile=profile):
                self.target = self.root / ('项目 ' + profile)
                actions, success = self.initialize(profile)
                self.assertTrue(success, actions)
                self.assertEqual(self.validate(profile), [])
                directories = {p.relative_to(self.target).as_posix() for p in self.target.rglob('*') if p.is_dir()}
                self.assertEqual(len(directories), directory_count)
                self.assertEqual(len(list(self.target.rglob('.gitkeep'))), leaf_count)
                self.assertIn('00_Project_Management/Requirements', directories)
                self.assertIn('05_Firmware/Applications', directories)
                self.assertEqual('10_Course/Media' in directories, profile == 'robotics')
                self.assertEqual('04_Hardware/Controller' in directories, profile != 'firmware')
                if profile == 'robotics':
                    for name in ('02_Motor/Maxwell', '03_Mechanical/Fixtures', '07_Simulation/HIL', '04_Hardware/Power_Stage'):
                        self.assertIn(name, directories)
                self.assertFalse((self.target / '.git').exists())
                data = common.read_json(self.target / common.MANIFEST)
                self.assertNotIn(str(self.root), json.dumps(data))

    def test_independent_standard_library_cli_generates_and_validates(self):
        self.assertEqual(checker.validate(self.skill), [])
        before = snapshot(self.root)
        result = self.cli('init_project.py', '--target', str(self.target), '--name', '测试 Project', '--profile', 'firmware', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.root), before)
        result = self.cli('init_project.py', '--target', str(self.target), '--name', '测试 Project', '--profile', 'firmware')
        self.assertEqual(result.returncode, 0, result.stderr)
        before = snapshot(self.root)
        result = self.cli('validate_project.py', '--target', str(self.target), '--profile', 'firmware')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_dry_run_missing_target_has_no_writes(self):
        before = snapshot(self.root)
        actions, success = self.initialize(dry_run=True)
        self.assertTrue(success)
        self.assertTrue(any('CREATE' in item for item in actions))
        self.assertEqual(snapshot(self.root), before)

    def test_dry_run_existing_target_and_repeat_preserve_all_timestamps(self):
        self.initialize()
        before = snapshot(self.target)
        self.assertTrue(self.initialize(dry_run=True)[1])
        self.assertEqual(snapshot(self.target), before)
        actions, success = self.initialize()
        self.assertTrue(success)
        self.assertTrue(all(item.startswith('UNCHANGED') for item in actions))
        self.assertEqual(snapshot(self.target), before)

    def test_existing_root_not_nested(self):
        self.target.mkdir()
        self.initialize()
        self.assertFalse((self.target / '测试 Project').exists())
        self.assertTrue((self.target / '05_Firmware').is_dir())

    def test_existing_root_files_conflict_without_any_writes(self):
        self.target.mkdir()
        for name in ('README.md', '.gitignore', common.MANIFEST):
            with self.subTest(name=name):
                path = self.target / name
                path.write_bytes(b'user content')
                before = snapshot(self.target)
                for dry_run in (True, False):
                    actions, success = self.initialize(dry_run=dry_run)
                    self.assertFalse(success)
                    self.assertTrue(any('CONFLICT' in action for action in actions))
                    self.assertEqual(snapshot(self.target), before)
                path.unlink()

    def test_nonempty_leaf_does_not_get_placeholder(self):
        leaf = self.target / '05_Firmware/Core'
        leaf.mkdir(parents=True)
        (leaf / 'user.c').write_bytes(b'user')
        self.assertTrue(self.initialize()[1])
        self.assertFalse((leaf / '.gitkeep').exists())
        self.assertEqual(self.validate(), [])

    def test_validation_is_read_only_and_allows_user_extensions(self):
        self.initialize()
        (self.target / 'Custom').mkdir()
        (self.target / 'README.md').write_text('User documentation', encoding='utf-8')
        before = snapshot(self.target)
        self.assertEqual(self.validate(), [])
        self.assertEqual(snapshot(self.target), before)

    def test_missing_placeholder_only_fails_for_empty_leaf(self):
        self.initialize()
        leaf = self.target / '05_Firmware/Core'
        (leaf / '.gitkeep').unlink()
        self.assertTrue(any('placeholder' in error for error in self.validate()))
        (leaf / 'module.c').write_bytes(b'content')
        self.assertEqual(self.validate(), [])

    def test_missing_required_directory_and_manifest_mismatch_fail(self):
        self.initialize()
        leaf = self.target / '05_Firmware/Core'
        (leaf / '.gitkeep').unlink()
        leaf.rmdir()
        self.assertTrue(any('Missing directory' in item for item in self.validate()))
        self.initialize()
        path = self.target / common.MANIFEST
        data = common.read_json(path)
        data['profile'] = 'robotics'
        path.write_text(json.dumps(data), encoding='utf-8')
        self.assertTrue(any('Manifest' in error for error in self.validate()))

    def test_invalid_profile_names_and_target_traversal(self):
        for profile in ('../firmware', '/firmware', 'unknown', 'F:\\profile'):
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                self.initialize(profile)
        with self.assertRaises(ValueError):
            initializer.initialize(self.target / '..' / 'escape', 'Test', 'firmware', assets=self.assets)
        self.assertFalse(self.target.exists())

    def test_malicious_profile_paths_rejected_before_writes(self):
        path = self.assets / 'profiles/firmware.json'
        original = common.read_json(path)
        for names in (['../escape'], ['/absolute'], ['C:/escape'], ['a\\b'], ['a//b'],
                      ['safe', 'safe'], ['safe/A', 'Safe/B'], ['safe', 'safe/child'], ['NUL'], ['a.']):
            with self.subTest(names=names):
                path.write_text(json.dumps({**original, 'directories': names}), encoding='utf-8')
                with self.assertRaises(ValueError):
                    self.initialize()
                self.assertFalse(self.target.exists())

    def test_duplicate_json_keys_rejected(self):
        path = self.assets / 'profiles/firmware.json'
        path.write_text('{"id":"firmware","id":"robotics"}', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.initialize()

    def test_same_name_file_blocks_directory_creation(self):
        self.target.mkdir()
        (self.target / '05_Firmware').write_bytes(b'user file')
        before = snapshot(self.target)
        with self.assertRaises(ValueError):
            self.initialize()
        self.assertEqual(snapshot(self.target), before)

    def test_mid_write_failure_rolls_back_only_new_content(self):
        self.target.mkdir()
        keep = self.target / 'keep.txt'
        keep.write_bytes(b'user')
        with patch.object(initializer.os, 'fsync', side_effect=[None, OSError('disk failure')]):
            with self.assertRaises(OSError):
                self.initialize()
        self.assertEqual(list(self.target.iterdir()), [keep])
        self.assertEqual(keep.read_bytes(), b'user')

    def test_permission_failure_rolls_back_new_target(self):
        original = Path.open
        def deny(path, mode='r', *args, **kwargs):
            if mode == 'xb':
                raise PermissionError('simulated no write permission')
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', deny), self.assertRaises(PermissionError):
            self.initialize()
        self.assertFalse(self.target.exists())

    def test_actual_symlink_rejected_without_external_writes(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.target.mkdir()
        link = self.target / '05_Firmware'
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f'NOT RUN: OS symlink privilege unavailable: {error}')
        self.addCleanup(link.unlink)
        with self.assertRaises(ValueError):
            self.initialize()
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipUnless(os.name == 'nt', 'Windows junction test; POSIX uses symlink test')
    def test_actual_windows_junction_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.target.mkdir()
        junction = self.target / '05_Firmware'
        result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(junction), str(outside)], capture_output=True)
        if result.returncode:
            self.skipTest('NOT RUN: OS could not create test junction')
        self.addCleanup(os.rmdir, junction)
        with self.assertRaises(ValueError):
            self.initialize()
        self.assertEqual(list(outside.iterdir()), [])

    def test_sync_detects_source_and_copy_drift_without_writing(self):
        for source in syncer.COPIES:
            path = self.root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(syncer.ROOT / source, path)
        self.assertTrue(syncer.sync(self.root, check=True))
        self.assertFalse((self.root / syncer.SKILL).exists())
        syncer.sync(self.root)
        self.assertEqual(syncer.sync(self.root, check=True), [])
        source = self.root / 'templates/embedded-project/assets/README.md.tpl'
        source.write_bytes(source.read_bytes() + b'\nchange\n')
        before = snapshot(self.root / syncer.SKILL)
        self.assertTrue(syncer.sync(self.root, check=True))
        self.assertEqual(snapshot(self.root / syncer.SKILL), before)
        syncer.sync(self.root)
        self.assertEqual(syncer.sync(self.root, check=True), [])
        copy = self.root / syncer.SKILL / 'assets/profiles/firmware.json'
        copy.write_bytes(b'{}')
        self.assertTrue(syncer.sync(self.root, check=True))

    def test_validator_rejects_metadata_links_and_template_tokens(self):
        entry = self.skill / 'SKILL.md'
        text = entry.read_text(encoding='utf-8')
        entry.write_text(text.replace('status: "draft"', 'status: "stable"'), encoding='utf-8')
        self.assertTrue(checker.validate(self.skill))
        entry.write_text(text + '\n[Bad](../../outside)\n', encoding='utf-8')
        self.assertTrue(checker.validate(self.skill))
        entry.write_text(text, encoding='utf-8')
        (self.assets / 'templates/README.md.tpl').write_text('${unknown}', encoding='utf-8')
        with self.assertRaises(KeyError):
            checker.validate(self.skill)


if __name__ == '__main__':
    unittest.main()
