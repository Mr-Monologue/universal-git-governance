"""Behavioral regressions in temporary directories outside the repository."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import sync_embedded_c_skill as syncer
from scripts import validate_embedded_c_skill as validator

SPEC = importlib.util.spec_from_file_location('new_c_module', validator.SKILL / 'scripts/new_c_module.py')
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class EmbeddedCSkillTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='embedded-c-skill-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.skill = self.root / 'standalone skill' / 'embedded-c-module'
        shutil.copytree(validator.SKILL, self.skill, ignore=shutil.ignore_patterns('__pycache__'))
        self.output = self.root / 'generated modules'

    def run_generator(self, *args):
        return subprocess.run([sys.executable, '-I', str(self.skill / 'scripts/new_c_module.py'),
                               *args], cwd=self.root, capture_output=True, text=True)

    def test_standalone_copy_links_metadata_and_generation(self):
        self.assertEqual(validator.validate(self.skill), [])
        result = self.run_generator('--module', 'adc_scale', '--output', str(self.output))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in self.output.iterdir()}, {'adc_scale.h', 'adc_scale.c'})
        header = (self.output / 'adc_scale.h').read_text(encoding='utf-8')
        source = (self.output / 'adc_scale.c').read_text(encoding='utf-8')
        self.assertIn('#ifndef ADC_SCALE_H_', header)
        self.assertIn('#define ADC_SCALE_H_', header)
        self.assertEqual(next(line for line in source.splitlines() if line.startswith('#include')),
                         '#include "adc_scale.h"')
        for name, text in (('adc_scale.h', header), ('adc_scale.c', source)):
            self.assertIn('@file ' + name, text)
            self.assertIn('@brief', text)
            self.assertNotIn('@param', text)
            self.assertNotIn('@author', text)

    def test_frontmatter_name_description_and_status_are_checked(self):
        path = self.skill / 'SKILL.md'
        original = path.read_text(encoding='utf-8')
        for old, new in [('name: embedded-c-module', 'name: other-module'),
                         ('description:', 'unused_description:'),
                         ('status: "draft"', 'status: "accepted"')]:
            with self.subTest(old=old):
                path.write_text(original.replace(old, new), encoding='utf-8')
                self.assertTrue(validator.validate(self.skill))
        path.write_text('---\nname: [unterminated\n---\n', encoding='utf-8')
        result = subprocess.run([sys.executable, str(validator.ROOT / 'scripts/validate_embedded_c_skill.py'),
                                 '--skill-dir', str(self.skill)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)

    def test_missing_reference_and_link_escape_fail(self):
        reference = self.skill / 'references/OPEN_DECISIONS.md'
        reference.unlink()
        self.assertTrue(validator.validate(self.skill))
        shutil.copyfile(validator.SKILL / 'references/OPEN_DECISIONS.md', reference)
        with (self.skill / 'README.md').open('a', encoding='utf-8') as stream:
            stream.write('\n[Outside](../)\n')
        self.assertTrue(any('invalid local link' in item for item in validator.validate(self.skill)))

    def test_dry_run_leaves_no_directory(self):
        result = self.run_generator('--module', 'adc_scale', '--output', str(self.output / 'nested'), '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PREVIEW:', result.stdout)
        self.assertFalse(self.output.exists())

    def test_invalid_names_write_nothing(self):
        for name in ('../bad', 'bad/name', 'bad\\name', 'Upper', '_hidden', 'a__b',
                     'a_', 'int', 'con', 'nul', 'com1', 'a' * 65):
            with self.subTest(name=name):
                result = self.run_generator('--module', name, '--output', str(self.output))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(self.output.exists())

    def test_repeat_does_not_overwrite(self):
        generator.generate('adc_scale', self.output, skill=self.skill)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        result = self.run_generator('--module', 'adc_scale', '--output', str(self.output))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})

    def test_either_existing_file_blocks_both_outputs(self):
        self.output.mkdir()
        for suffix in ('h', 'c'):
            with self.subTest(suffix=suffix):
                existing = self.output / f'adc_scale.{suffix}'
                existing.write_bytes(b'user work')
                with self.assertRaises(FileExistsError):
                    generator.generate('adc_scale', self.output, skill=self.skill)
                self.assertEqual(list(self.output.iterdir()), [existing])
                self.assertEqual(existing.read_bytes(), b'user work')
                existing.unlink()

    def test_existing_target_directory_is_preserved(self):
        existing = self.output / 'adc_scale.c'
        existing.mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            generator.generate('adc_scale', self.output, skill=self.skill)
        self.assertTrue(existing.is_dir())
        self.assertFalse((self.output / 'adc_scale.h').exists())

    def test_non_directory_output_ancestor_fails(self):
        self.output.write_text('user file', encoding='utf-8')
        with self.assertRaises(NotADirectoryError):
            generator.generate('adc_scale', self.output / 'nested', skill=self.skill)
        self.assertEqual(self.output.read_text(encoding='utf-8'), 'user file')

    def test_permission_failure_removes_only_new_empty_dirs(self):
        original_open = Path.open
        def denied(path, mode='r', *args, **kwargs):
            if mode == 'x':
                raise PermissionError('simulated unwritable output')
            return original_open(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', denied), self.assertRaises(PermissionError):
            generator.generate('adc_scale', self.output / 'nested', skill=self.skill)
        self.assertFalse(self.output.exists())

    def test_second_create_race_preserves_other_file_and_rolls_back_first(self):
        self.output.mkdir()
        original_open = Path.open
        def race(path, mode='r', *args, **kwargs):
            if mode == 'x' and path.suffix == '.c':
                path.write_bytes(b'concurrent user file')
            return original_open(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', race), self.assertRaises(FileExistsError):
            generator.generate('adc_scale', self.output, skill=self.skill)
        self.assertFalse((self.output / 'adc_scale.h').exists())
        self.assertEqual((self.output / 'adc_scale.c').read_bytes(), b'concurrent user file')

    def test_mid_write_failure_rolls_back_pair_preserving_other_files(self):
        self.output.mkdir()
        sentinel = self.output / 'keep.txt'
        sentinel.write_bytes(b'preserve')
        with patch.object(generator.os, 'fsync', side_effect=[None, OSError('disk failure')]):
            with self.assertRaises(OSError):
                generator.generate('adc_scale', self.output, skill=self.skill)
        self.assertEqual(list(self.output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b'preserve')

    def test_missing_template_leaves_no_outputs(self):
        (self.skill / 'assets/module.c.tpl').unlink()
        with self.assertRaises(FileNotFoundError):
            generator.generate('adc_scale', self.output, skill=self.skill)
        self.assertFalse(self.output.exists())

    def test_generated_minimal_module_compiles_when_compiler_available(self):
        compiler = shutil.which('gcc') or shutil.which('clang')
        if compiler is None:
            self.skipTest('NOT RUN: no GCC/Clang available')
        generator.generate('adc_scale', self.output, skill=self.skill)
        result = subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Wpedantic',
                                 '-Wconversion', '-Wsign-conversion', '-Werror', '-c',
                                 str(self.output / 'adc_scale.c'), '-o', str(self.root / 'module.o')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sync_check_detects_drift_and_write_restores(self):
        for source in syncer.COPIES:
            path = self.root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(syncer.ROOT / source, path)
        self.assertTrue(syncer.sync(self.root, check=True))
        self.assertFalse((self.root / syncer.SKILL_PATH).exists())
        self.assertEqual(syncer.sync(self.root), [])
        self.assertEqual(syncer.sync(self.root, check=True), [])
        for source, target in syncer.COPIES.items():
            with self.subTest(target=target):
                destination = self.root / target
                destination.write_bytes(b'manual edit')
                self.assertTrue(syncer.sync(self.root, check=True))
                self.assertEqual(destination.read_bytes(), b'manual edit')
                syncer.sync(self.root)
                self.assertEqual(destination.read_bytes(), (self.root / source).read_bytes())
        source = self.root / 'standards/embedded-c/C_CODING_STANDARD.md'
        source.write_bytes(source.read_bytes() + b'\nUpdated source\n')
        self.assertTrue(syncer.sync(self.root, check=True))
        syncer.sync(self.root)
        self.assertEqual(syncer.sync(self.root, check=True), [])

    def test_sync_cli_check_is_read_only_and_returns_nonzero(self):
        for source in syncer.COPIES:
            path = self.root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(syncer.ROOT / source, path)
        script = self.root / 'scripts/sync_embedded_c_skill.py'
        script.parent.mkdir()
        shutil.copyfile(syncer.ROOT / 'scripts/sync_embedded_c_skill.py', script)
        for args, expected in ((['--check'], 1), ([], 0), (['--check'], 0)):
            result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stderr)

    def test_skill_policy_cannot_weaken_doxygen_or_override_project(self):
        path = self.skill / 'SKILL.md'
        original = path.read_text(encoding='utf-8')
        for old, new in [('Doxygen 是强制要求', 'Doxygen 是可选'),
                         ('既有正式规则优先', '候选规则覆盖项目规则'),
                         ('目标项目无正式规则时', '所有项目一律')]:
            path.write_text(original.replace(old, new), encoding='utf-8')
            self.assertTrue(any('SKILL.md' in e for e in validator.validate(self.skill)))
        path.write_text(original, encoding='utf-8')
        self.assertEqual(validator.validate(self.skill), [])

    def test_template_doxygen_draft_and_false_approval_are_checked(self):
        path = self.skill / 'assets/module.h.tpl'
        original = path.read_text(encoding='utf-8')
        for text in (original.replace('/**', '/*'), original.replace('Draft', 'Stable'),
                     original + '\n/* K&R 全局强制 */\n'):
            path.write_text(text, encoding='utf-8')
            before = path.read_bytes()
            self.assertTrue(any('module.h.tpl' in e for e in validator.validate(self.skill)))
            self.assertEqual(path.read_bytes(), before)
        path.write_text(original, encoding='utf-8')
        self.assertEqual(validator.validate(self.skill), [])


if __name__ == '__main__':
    unittest.main()
