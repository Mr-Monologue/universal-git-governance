"""Compile Markdown review fixtures externally; no production driver claims."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / 'standards/embedded-c/examples/style-review/README.md'


def samples():
    text = DOCUMENT.read_text(encoding='utf-8')
    return dict(re.findall(r'<!-- sample: ([\w-]+) -->\n```c\n(.*?)```', text, re.S))


class StyleReviewTests(unittest.TestCase):
    def test_only_whitespace_changes_and_contracts_survive(self):
        blocks = samples()
        self.assertEqual(set(blocks), {'header-80', 'header-100', 'header-120', 'source-attach', 'source-allman'})
        # Doxygen reflow adds a leading '*' on each new comment line.
        # Normalize that decoration while retaining all contract words and code.
        compact = lambda text: re.sub(r'\s+', '', re.sub(r'^\s*\* ?', '', text, flags=re.M))
        for width in (80, 100, 120):
            header = blocks[f'header-{width}']
            self.assertEqual(compact(header), compact(blocks['header-100']))
            self.assertLessEqual(max(map(len, header.splitlines())), width)
            for tag in ('@file', '@brief', '@param[in]', '@param[out]', '@retval', '@pre', '@note', 'ISR'):
                self.assertIn(tag, header)
        self.assertEqual(compact(blocks['source-attach']), compact(blocks['source-allman']))

    def test_all_layouts_c99_c11_have_identical_behavior(self):
        compiler = shutil.which('gcc') or shutil.which('clang')
        if not compiler:
            self.skipTest('NOT RUN: GCC/Clang unavailable')
        blocks = samples()
        with tempfile.TemporaryDirectory(prefix='style-review-') as folder:
            root = Path(folder)
            (root / 'test.c').write_text('''#include "style_sample.h"
#include <assert.h>
#include <stddef.h>
int main(void) {
    uint16_t out = 123U;
    assert(sample_limit_checked(1U, 1U, NULL) == SAMPLE_INVALID_ARG);
    assert(sample_limit_checked(5001U, 1U, &out) == SAMPLE_INVALID_ARG);
    assert(out == 123U);
    assert(sample_limit_checked(1U, 5001U, &out) == SAMPLE_INVALID_ARG);
    assert(out == 123U);
    const uint16_t values[] = {0U, 1U, 2499U, 5000U};
    for (size_t i = 0; i < sizeof(values) / sizeof(values[0]); ++i) {
        for (size_t j = 0; j < sizeof(values) / sizeof(values[0]); ++j) {
            uint16_t fast = 0U;
            assert(sample_limit_checked(values[i], values[j], &out) == SAMPLE_OK);
            sample_limit_assume_valid(values[i], values[j], &fast);
            assert(out == fast);
            assert(out == ((values[i] > values[j]) ? values[j] : values[i]));
        }
    }
    return 0;
}
''', encoding='utf-8')
            for standard in ('c99', 'c11'):
                for width in (80, 100, 120):
                    for style in ('attach', 'allman'):
                        with self.subTest(standard=standard, width=width, style=style):
                            (root / 'style_sample.h').write_text(blocks[f'header-{width}'], encoding='utf-8')
                            (root / 'style_sample.c').write_text(blocks[f'source-{style}'], encoding='utf-8')
                            exe = root / 'test.exe'
                            result = subprocess.run([compiler, '-std=' + standard, '-Wall', '-Wextra', '-Wpedantic',
                                      '-Wconversion', '-Wsign-conversion', '-Werror', str(root / 'style_sample.c'),
                                      str(root / 'test.c'), '-o', str(exe)], capture_output=True, text=True)
                            self.assertEqual(result.returncode, 0, result.stderr)
                            result = subprocess.run([str(exe)], capture_output=True, text=True)
                            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
