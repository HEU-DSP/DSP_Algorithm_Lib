import math
import os
import tempfile
import unittest
from unittest import mock

import resource_metrics


class ResourceMetricsTests(unittest.TestCase):
    def test_parse_gnu_size_row_returns_exact_section_sizes(self):
        payload = (
            '   text    data     bss     dec     hex filename\n'
            '  12345     456    7890   20691    50d3 test_fft_core.exe\n'
        )

        self.assertEqual(
            resource_metrics.parse_gnu_size_output(payload),
            {'text_bytes': 12345, 'data_bytes': 456, 'bss_bytes': 7890},
        )

    def test_parse_gnu_size_rejects_missing_numeric_row(self):
        with self.assertRaises(ValueError):
            resource_metrics.parse_gnu_size_output('text data bss dec hex filename\n')

    def test_parse_gnu_size_rejects_malformed_numeric_columns(self):
        payload = '12345 456 7890 not-a-decimal 50d3 test_fft_core.exe\n'
        with self.assertRaises(ValueError):
            resource_metrics.parse_gnu_size_output(payload)

    def test_parse_benchmark_line_returns_validated_record(self):
        self.assertEqual(
            resource_metrics.parse_benchmark_line('BENCH:fft_core:20:153.250000'),
            {'algorithm': 'fft_core', 'iterations': 20, 'average_us': 153.25},
        )

    def test_parse_benchmark_line_rejects_invalid_fields(self):
        invalid_lines = (
            'BENCH:fft_core:20',
            'BENCH:fft_core:20:1.0:extra',
            'BENCH:fft_core:not-a-number:1.0',
            'BENCH:fft_core:0:1.0',
            'BENCH:fft_core:-1:1.0',
            'BENCH:fft_core:20:not-a-number',
            'BENCH:fft_core:20:nan',
            'BENCH:fft_core:20:inf',
            'BENCH:fft_core:20:0',
            'BENCH:fft_core:20:-0.1',
        )
        for line in invalid_lines:
            with self.subTest(line=line), self.assertRaises(ValueError):
                resource_metrics.parse_benchmark_line(line)

    def test_resolve_size_command_uses_path_lookup(self):
        with mock.patch('resource_metrics.shutil.which', return_value='C:/Tools/size.exe') as which:
            self.assertEqual(resource_metrics.resolve_size_command(), 'C:/Tools/size.exe')
        which.assert_called_once_with('size')

    def test_resolve_size_command_raises_when_unavailable(self):
        with mock.patch('resource_metrics.shutil.which', return_value=None):
            with self.assertRaises(FileNotFoundError):
                resource_metrics.resolve_size_command()

    def test_collect_resource_metrics_runs_size_and_reads_executable_bytes(self):
        payload = (
            '   text    data     bss     dec     hex filename\n'
            '  12345     456    7890   20691    50d3 test_fft_core.exe\n'
        )
        completed = mock.Mock(returncode=0, stdout=payload, stderr='')
        with tempfile.NamedTemporaryFile(delete=False) as stream:
            stream.write(b'abcde')
            executable = stream.name
        try:
            with mock.patch('resource_metrics.subprocess.run', return_value=completed) as run:
                self.assertEqual(
                    resource_metrics.collect_resource_metrics(executable, 'size-tool'),
                    {
                        'executable_bytes': 5,
                        'text_bytes': 12345,
                        'data_bytes': 456,
                        'bss_bytes': 7890,
                    },
                )
            run.assert_called_once_with(
                ['size-tool', '-B', executable], capture_output=True, text=True,
            )
        finally:
            os.unlink(executable)

    def test_collect_resource_metrics_rejects_missing_executable_and_size_failure(self):
        with self.assertRaises(FileNotFoundError):
            resource_metrics.collect_resource_metrics('missing-program.exe', 'size-tool')

        with tempfile.NamedTemporaryFile(delete=False) as stream:
            executable = stream.name
        try:
            failed = mock.Mock(returncode=1, stdout='', stderr='size failed')
            with mock.patch('resource_metrics.subprocess.run', return_value=failed):
                with self.assertRaises(RuntimeError):
                    resource_metrics.collect_resource_metrics(executable, 'size-tool')
        finally:
            os.unlink(executable)


if __name__ == '__main__':
    unittest.main()
