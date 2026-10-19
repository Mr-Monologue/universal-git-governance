"""Owner decision regressions, real formatter behavior and isolated templates."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts import validate_embedded_c as standard
from scripts import validate_embedded_c_skill as skill


class FreezeTests(unittest.TestCase):
    def test_adc_doxygen_contract_with_complete_output(self):
        doxygen = os.environ.get('DOXYGEN') or shutil.which('doxygen')
        if not doxygen:
            self.skipTest('NOT RUN: Doxygen unavailable; set DOXYGEN to an existing executable')
        examples = standard.ROOT / standard.MODULE / 'examples'
        with tempfile.TemporaryDirectory(prefix='freeze-doxygen-') as folder:
            root = Path(folder)
            config = root / 'Doxyfile'
            config.write_text('\n'.join([
                'INPUT = ' + ' '.join('"' + (examples / name).as_posix() + '"'
                                      for name in ('adc_scale.h', 'adc_scale.c')),
                'OUTPUT_DIRECTORY = "' + (root / 'docs').as_posix() + '"',
                'INPUT_ENCODING = UTF-8', 'EXTRACT_ALL = NO', 'WARNINGS = YES',
                'WARN_IF_UNDOCUMENTED = YES', 'WARN_IF_DOC_ERROR = YES', 'WARN_NO_PARAMDOC = YES',
                'WARN_AS_ERROR = FAIL_ON_WARNINGS', 'GENERATE_HTML = YES', 'GENERATE_XML = YES',
                'GENERATE_LATEX = NO', 'HAVE_DOT = NO', 'QUIET = YES']), encoding='utf-8')
            result = subprocess.run([doxygen, str(config)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            members = [member for path in (root / 'docs/xml').glob('*.xml')
                       for member in ET.parse(path).getroot().iter('memberdef')
                       if member.findtext('name') == 'adc_scale_convert_mv']
            self.assertTrue(members)
            for member in members:
                documented = {node.text for node in member.findall('.//parameterlist[@kind="param"]//parametername')}
                self.assertEqual(documented, {'raw_code', 'full_scale_code', 'reference_mv', 'result_mv'})
                returns = {node.text for node in member.findall('.//parameterlist[@kind="retval"]//parametername')}
                self.assertEqual(returns, {'ADC_SCALE_OK', 'ADC_SCALE_INVALID_ARG'})

    def test_each_default_and_exception_is_bound_to_its_decision(self):
        text = (standard.ROOT / standard.MODULE / 'C_CODING_STANDARD.md').read_text(encoding='utf-8')
        self.assertEqual(standard.check_approved_defaults(text, 'standard'), [])
        for index, (defaults, exceptions) in enumerate(standard.APPROVED, 1):
            key = f'C-STYLE-{index:02}'
            row = next(line for line in text.splitlines() if line.startswith('| ' + key + ' |'))
            for clause in (*defaults, *exceptions):
                with self.subTest(decision=key, clause=clause):
                    changed = text.replace(row, row.replace(clause, 'REMOVED'))
                    self.assertTrue(any(key in e for e in standard.check_approved_defaults(changed, 'standard')))
        swapped = text.replace('| C-STYLE-01 |', '| C-STYLE-12 |')
        self.assertTrue(standard.check_approved_defaults(swapped, 'standard'))

    def test_real_configuration_values_not_comment_claims(self):
        config = (standard.ROOT / standard.MODULE / 'config/.clang-format').read_text(encoding='utf-8')
        for old, new in [('IndentWidth: 4', 'IndentWidth: 8'), ('UseTab: Never', 'UseTab: Always'),
                         ('ColumnLimit: 100', 'ColumnLimit: 80'), ('BreakBeforeBraces: Attach', 'BreakBeforeBraces: Allman'),
                         ('BreakStringLiterals: false', 'BreakStringLiterals: true')]:
            with self.subTest(option=old):
                self.assertTrue(standard.check_format_config(config.replace(old, new)))

    def test_installed_reference_cannot_drift_from_approved_values(self):
        with tempfile.TemporaryDirectory(prefix='freeze-reference-') as folder:
            installed = Path(folder) / 'embedded-c-module'
            shutil.copytree(skill.SKILL, installed, ignore=shutil.ignore_patterns('__pycache__'))
            path = installed / 'references/C_CODING_STANDARD.md'
            path.write_text(path.read_text(encoding='utf-8').replace('100 列软限制', '80 列软限制'), encoding='utf-8')
            self.assertTrue(any('C-STYLE-03' in e for e in skill.validate(installed)))

    def test_standalone_templates_and_real_formatter_defaults(self):
        formatter = os.environ.get('CLANG_FORMAT') or shutil.which('clang-format')
        if not formatter:
            self.skipTest('NOT RUN: clang-format unavailable; set CLANG_FORMAT to an existing executable')
        with tempfile.TemporaryDirectory(prefix='freeze-format-') as folder:
            root = Path(folder)
            installed = root / 'embedded-c-module'
            shutil.copytree(skill.SKILL, installed, ignore=shutil.ignore_patterns('__pycache__'))
            output = root / 'module'
            result = subprocess.run([sys.executable, '-I', '-S', str(installed / 'scripts/new_c_module.py'),
                                     '--module', 'freeze_sample', '--output', str(output)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            config = '--style=file:' + str(installed / 'references/config/.clang-format')
            for suffix in ('c', 'h'):
                result = subprocess.run([formatter, config, '--dry-run', '--Werror', str(output / f'freeze_sample.{suffix}')], capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            # Exercise formatter transformation, not only YAML values. Keep a long literal intact.
            literal = 'x' * 110
            sample = 'int sample(int value)\n{\n\tif(value==0)\n\t{\n\t\treturn 1;\n\t}\n\treturn 0;\n}\nconst char *sample_text = "' + literal + '";\n'
            result = subprocess.run([formatter, config, '--assume-filename=sample.c'], input=sample,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('int sample(int value) {\n    if (value == 0) {\n        return 1;', result.stdout)
            self.assertNotIn('\t', result.stdout)
            self.assertIn('"' + literal + '"', result.stdout)
            self.assertNotIn('@author', (output / 'freeze_sample.h').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
