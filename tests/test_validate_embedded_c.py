"""Regression tests mutate isolated copies, never repository documents."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate_embedded_c as validator


class EmbeddedCValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.module = self.root / validator.MODULE
        shutil.copytree(validator.ROOT / validator.MODULE, self.module)
        # The module navigation and validator links have real local targets.
        for name in ('README.md', 'standards/README.md', 'scripts/validate_embedded_c.py'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Fixture target', encoding='utf-8')

    def change_standard(self, old, new):
        path = self.module / 'C_CODING_STANDARD.md'
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding='utf-8')

    def test_real_package_passes_without_mutation(self):
        before = {str(path): path.read_bytes() for path in self.module.rglob('*') if path.is_file()}
        self.assertEqual(validator.validate(self.root), [])
        self.assertEqual(before, {str(path): path.read_bytes() for path in self.module.rglob('*') if path.is_file()})

    def test_each_missing_required_file_fails(self):
        for name in validator.REQUIRED:
            with self.subTest(name=name):
                path = self.module / name
                original = path.read_bytes()
                path.unlink()
                self.assertTrue(any('required file:' in error for error in validator.validate(self.root)))
                path.write_bytes(original)

    def test_broken_inline_and_reference_links_fail(self):
        path = self.module / 'CHANGE_REVIEW.md'
        original = path.read_text(encoding='utf-8')
        for link in ('[Broken](missing.md)', '[broken]: missing.md'):
            with self.subTest(link=link):
                path.write_text(original + '\n' + link, encoding='utf-8')
                self.assertTrue(any('invalid local link' in error for error in validator.validate(self.root)))

    def test_external_urls_anchors_and_code_examples_pass(self):
        path = self.module / 'CHANGE_REVIEW.md'
        with path.open('a', encoding='utf-8') as stream:
            stream.write('\n[Site](https://example.com) [Section](#section)\n'
                         '~~~text\n[Example](missing.md)\n~~~\n')
        self.assertEqual(validator.validate(self.root), [])

    def test_local_link_cannot_escape_repository(self):
        path = self.module / 'CHANGE_REVIEW.md'
        with path.open('a', encoding='utf-8') as stream:
            stream.write('\n[Outside](../../../)\n')
        self.assertTrue(any('invalid local link' in error for error in validator.validate(self.root)))

    def test_wrong_version_and_status_fail(self):
        self.change_standard('version: 0.1.0', 'version: 1.0.0')
        self.change_standard('status: Draft', 'status: Stable')
        errors = validator.validate(self.root)
        self.assertTrue(any('version must be' in error for error in errors))
        self.assertTrue(any('status must be' in error for error in errors))

    def test_missing_frontmatter_fails(self):
        self.change_standard('---\ntitle:', 'title:')
        self.assertTrue(any('frontmatter' in error for error in validator.validate(self.root)))

    def test_malformed_frontmatter_fails(self):
        self.change_standard('status: Draft', 'status Draft')
        self.assertTrue(any('malformed' in error for error in validator.validate(self.root)))

    def test_duplicate_frontmatter_fails(self):
        self.change_standard('status: Draft', 'status: Draft\nstatus: Stable')
        self.assertTrue(any('duplicate' in error for error in validator.validate(self.root)))

    def test_unclosed_fence_fails(self):
        path = self.module / 'REVIEW_CHECKLIST.md'
        with path.open('a', encoding='utf-8') as stream:
            stream.write('\n```c\nint unfinished;\n')
        self.assertTrue(any('unclosed code fence' in error for error in validator.validate(self.root)))

    def test_non_doxygen_comment_fails(self):
        path = self.module / 'examples/adc_scale.c'
        path.write_text(path.read_text(encoding='utf-8').replace('/**', '/*'), encoding='utf-8')
        self.assertTrue(any('Doxygen' in error for error in validator.validate(self.root)))

    def test_main_returns_nonzero_on_failure(self):
        with patch.object(validator, 'ROOT', self.root), redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(validator.main(), 0)
            (self.module / 'config/.clang-format').unlink()
            self.assertEqual(validator.main(), 1)


if __name__ == '__main__':
    unittest.main()
