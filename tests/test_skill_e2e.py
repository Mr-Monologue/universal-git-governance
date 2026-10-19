"""E2E entrypoint regression tests; all mutations stay in owned temporary fixtures."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate_skill_e2e as e2e


class SkillE2ETests(unittest.TestCase):
    def test_complete_workflow_without_optional_tools_and_native_evidence(self):
        before = e2e.source_state()
        with redirect_stdout(io.StringIO()) as output:
            result = e2e.run()
        self.assertEqual(result.counts()['FAIL'], 0, output.getvalue())
        self.assertEqual(result.counts()['NOT RUN'], 7)
        for profile in ('firmware', 'robotics'):
            self.assertTrue(any(i['name'] == profile and i['status'] == 'PASS' for i in result.items))
        self.assertTrue(all(i['status'] == 'NOT RUN' for i in result.items if i['layer'] == 'native-agent'))
        location = output.getvalue().split('ISOLATION: ')[1].splitlines()[0]
        self.assertFalse(Path(location).exists())
        self.assertEqual(e2e.source_state(), before)

    def test_owned_workspace_cleans_failure_and_does_not_touch_sibling(self):
        with tempfile.TemporaryDirectory(prefix='e2e owner ') as folder:
            parent = Path(folder)
            sentinel = parent / 'keep.txt'
            sentinel.write_bytes(b'keep')
            with patch.object(e2e.tempfile, 'gettempdir', return_value=folder):
                with self.assertRaisesRegex(RuntimeError, 'injected'):
                    with e2e.workspace() as base:
                        (base / 'partial.txt').write_bytes(b'partial')
                        raise RuntimeError('injected workflow failure')
            self.assertFalse(base.exists())
            self.assertEqual(list(parent.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_bytes(), b'keep')

    def test_keep_is_explicit_and_retains_diagnostic_report_on_failure(self):
        with tempfile.TemporaryDirectory(prefix='e2e report ') as folder:
            with patch.object(e2e.tempfile, 'gettempdir', return_value=folder), \
                 patch.object(e2e, 'copy_fixture', side_effect=OSError('injected')), \
                 redirect_stdout(io.StringIO()):
                result = e2e.run(keep=True)
            report = next(Path(folder).glob('*/report.json'))
            data = json.loads(report.read_text(encoding='utf-8'))
            self.assertTrue(data['kept'])
            self.assertEqual(result.counts()['FAIL'], 1)
            self.assertEqual(data['counts']['FAIL'], 1)
            self.assertIn('injected', str(data))

    def test_containment_rejects_traversal_root_outside_and_file_ancestor(self):
        with e2e.workspace() as base:
            (base / 'file').write_bytes(b'keep')
            before = e2e.snapshot(base)
            for path in (base, base.parent / 'unexpected', base / 'a/../escape', base / 'file/child'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    e2e.contained(base, path)
            self.assertEqual(e2e.snapshot(base), before)
            self.assertEqual(e2e.contained(base, base / 'path with spaces'), base / 'path with spaces')

    def test_temp_parent_in_repository_rejected_before_creation(self):
        with patch.object(e2e.tempfile, 'gettempdir', return_value=str(e2e.ROOT)), \
             patch.object(e2e.tempfile, 'mkdtemp') as create:
            with self.assertRaisesRegex(ValueError, 'outside repository'):
                with e2e.workspace():
                    self.fail('must not enter workspace')
            create.assert_not_called()

    def test_scaffold_requires_real_doxygen_block_and_guard(self):
        with e2e.workspace() as base:
            header = '/** @file sample.h @brief Example. */\n#ifndef SAMPLE_H_\n#define SAMPLE_H_\n/* Draft */\n#endif\n'
            (base / 'sample.c').write_text('/** @file sample.c @brief Example. */', encoding='utf-8')
            path = base / 'sample.h'
            path.write_text(header, encoding='utf-8')
            e2e.check_scaffold(base, 'sample')
            for invalid in (header.replace('/**', '/*'), header.replace('#define', '#undef')):
                path.write_text(invalid, encoding='utf-8')
                with self.assertRaises(ValueError):
                    e2e.check_scaffold(base, 'sample')

    def test_unexpected_command_exit_is_failure_and_preserves_output(self):
        evidence = e2e.Evidence()
        with e2e.workspace() as base:
            with self.assertRaisesRegex(ValueError, 'Unexpected exit 7'):
                evidence.command([sys.executable, '-c', 'print("diagnostic"); raise SystemExit(7)'], base)
        self.assertEqual(evidence.commands[0]['exit'], 7)
        self.assertIn('diagnostic', evidence.commands[0]['stdout'])

    def test_cli_has_no_user_target_option_and_failure_exit_is_nonzero(self):
        result = subprocess.run([sys.executable, str(e2e.ROOT / 'scripts/validate_skill_e2e.py'),
                                 '--target-dir', 'unused'], capture_output=True)
        self.assertEqual(result.returncode, 2)
        evidence = e2e.Evidence()
        with redirect_stdout(io.StringIO()):
            evidence.add('workflow', 'injected', 'FAIL')
        with patch.object(e2e, 'run', return_value=evidence):
            self.assertEqual(e2e.main([]), 1)


if __name__ == '__main__':
    unittest.main()
