"""Exercise the validator against isolated real filesystem fixtures."""
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate_repository as validator


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in validator.MODULES:
            (self.root / name).mkdir()
            (self.root / name / 'README.md').write_text(
                '[Home](../README.md)\n', encoding='utf-8')
        for name in validator.ENTRYPOINTS:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# Entry\n', encoding='utf-8')

    def test_complete_structure_passes(self):
        self.assertEqual(validator.validate(self.root), [])

    def test_each_missing_directory_fails(self):
        for name in validator.MODULES:
            with self.subTest(name=name):
                directory = self.root / name
                moved = self.root / (name + '-saved')
                directory.rename(moved)
                self.assertIn(f'Missing directory: {name}', validator.validate(self.root))
                moved.rename(directory)

    def test_each_missing_entrypoint_or_module_readme_fails(self):
        names = (*validator.ENTRYPOINTS,
                 *(f'{name}/README.md' for name in validator.MODULES))
        for name in names:
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.unlink()
                self.assertTrue(any('Missing file:' in error for error in validator.validate(self.root)))
                path.write_bytes(original)

    def test_broken_inline_and_reference_links_fail(self):
        for link in ('[Missing](missing.md)', '[target]: missing.md'):
            with self.subTest(link=link):
                (self.root / 'skills/README.md').write_text(link, encoding='utf-8')
                self.assertTrue(any('invalid local link' in error for error in validator.validate(self.root)))

    def test_existing_external_local_target_is_rejected(self):
        (self.root / 'skills/README.md').write_text('[Outside](../../)', encoding='utf-8')
        self.assertTrue(any('invalid local link' in error for error in validator.validate(self.root)))

    def test_urls_anchors_and_code_are_excluded(self):
        (self.root / 'skills/README.md').write_text(
            '[Web](https://example.com) [Anchor](#section)\n'
            '```text\n[Sample](missing.md)\n```\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), [])

    def test_encoded_path_with_fragment_passes(self):
        (self.root / 'space name.md').write_text('# Heading', encoding='utf-8')
        (self.root / 'skills/README.md').write_text(
            '[Space](../space%20name.md#heading)', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), [])

    def test_main_exit_status(self):
        with patch.object(validator, 'ROOT', self.root), redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(validator.main(), 0)
            (self.root / 'AGENTS.md').unlink()
            self.assertEqual(validator.main(), 1)


if __name__ == '__main__':
    unittest.main()
