import json
import math
import os
import tempfile
import unittest
from unittest import mock

import numpy as np

import run_test
import report
from signal_generator import FIR_COEFFICIENTS, generate_signal, write_signal_header


class ValidationLogicTests(unittest.TestCase):
    def test_phase_error_wraps_at_pi(self):
        actual = math.radians(-179.0)
        expected = math.radians(179.0)
        self.assertAlmostEqual(
            run_test.circular_abs_error(actual, expected),
            math.radians(2.0),
            places=7,
        )

    def test_explicit_zero_is_not_replaced_by_default(self):
        self.assertEqual(run_test.value_or_default(0.0, math.pi / 4), 0.0)
        self.assertEqual(run_test.value_or_default(None, math.pi / 4), math.pi / 4)

    def test_cmake_falls_back_to_existing_cache_command(self):
        with tempfile.TemporaryDirectory() as build_dir:
            cache = os.path.join(build_dir, "CMakeCache.txt")
            with open(cache, "w", encoding="utf-8") as stream:
                stream.write("CMAKE_COMMAND:INTERNAL=C:/Tools/cmake.exe\n")

            with mock.patch("run_test.shutil.which", return_value=None):
                self.assertEqual(
                    run_test.resolve_cmake_command(build_dir),
                    "C:/Tools/cmake.exe",
                )

    def test_error_result_is_counted_as_unsuccessful(self):
        item = run_test.make_error_result("phase", "phase_0deg", RuntimeError("boom"))
        self.assertEqual(item["status"], "ERROR")
        self.assertIn("boom", item["message"])
        self.assertTrue(run_test.has_failures([item]))

    def test_seed_makes_noisy_signal_reproducible(self):
        kwargs = dict(
            waveform='sine', freq=1000.0, amplitude=1.0, phase=0.0,
            sample_rate=51200.0, samples=128, noise_std=0.02, adc_bits=0,
            seed=20260717,
        )
        first, _ = generate_signal(**kwargs)
        second, _ = generate_signal(**kwargs)
        self.assertTrue((first == second).all())

    def test_suite_seed_override_is_applied_to_every_case(self):
        cases = run_test.suite_cases('phase', 'full', seed=12345)
        self.assertTrue(cases)
        self.assertTrue(all(case['seed'] == 12345 for case in cases))

    def test_phase_check_uses_injected_expected_phase(self):
        check = {'kind': 'phase', 'tolerance': math.radians(0.5)}
        result = run_test.evaluate_check(
            'phase', 'phase_90deg', 'iq_phase', math.pi / 2,
            math.pi / 2 + math.radians(0.2), check,
        )
        self.assertEqual(result['status'], 'PASS')
        self.assertAlmostEqual(result['abs_error'], math.radians(0.2), places=7)

    def test_fft_core_has_non_quantized_cases_and_analytical_checks(self):
        self.assertEqual(
            run_test.MODULES['fft_core'],
            {'target': 'test_fft_core', 'samples': 8192, 'freq': 1000.0},
        )
        cases = run_test.suite_cases('fft_core', 'full')
        self.assertTrue(cases)
        for case in cases:
            self.assertEqual(case['waveform'], 'sine')
            self.assertEqual(case['adc_bits'], 0)
            checks = run_test.expected_checks('fft_core', case)
            self.assertEqual(checks['fft_core_freq'][0], case['freq'])
            self.assertAlmostEqual(
                checks['fft_core_freq'][1]['tolerance'],
                case['fs'] / case['samples'] / 2.0,
            )
            self.assertAlmostEqual(
                checks['fft_core_magnitude'][0],
                case['amplitude'] * case['samples'] / 2.0,
            )
            self.assertEqual(checks['fft_core_magnitude'][1]['tolerance'], 0.005)

    def test_mag_phase_uses_deterministic_adc_cases_and_waveform_labels(self):
        self.assertEqual(
            run_test.MODULES['mag_phase'],
            {'target': 'test_mag_phase', 'samples': 4096, 'freq': 1000.0},
        )
        cases = run_test.suite_cases('mag_phase', 'full')
        self.assertEqual(
            [(case['waveform'], case['amplitude'], case['samples'], case['adc_bits'])
             for case in cases],
            [('sine', 1.0, 4096, 12),
             ('square', 0.8, 4096, 12),
             ('triangle', 1.2, 4096, 12)],
        )
        labels = {
            'sine': 'mag_phase_sine',
            'square': 'mag_phase_square',
            'triangle': 'mag_phase_triangle',
        }
        for case in cases:
            checks = run_test.expected_checks('mag_phase', case)
            self.assertEqual(set(checks), {labels[case['waveform']]})
            expected, validation = checks[labels[case['waveform']]]
            self.assertEqual(expected, case['amplitude'])
            self.assertEqual(validation['kind'], 'relative')
            self.assertEqual(validation['tolerance'], 0.005)

    def test_runner_returns_validated_structured_benchmark_records(self):
        completed = mock.Mock(
            returncode=0,
            stdout='RESULT:fft_core_freq:1000.0\nBENCH:fft_core:20:12.5\n',
            stderr='',
        )
        with mock.patch('run_test.subprocess.run', return_value=completed), \
             mock.patch('builtins.print') as print_mock:
            measured, benchmarks = run_test.run_executable('build-dir', 'test_fft_core')

        self.assertEqual(measured['fft_core_freq'], 1000.0)
        self.assertEqual(
            benchmarks,
            [{'algorithm': 'fft_core', 'iterations': 20, 'average_us': 12.5}],
        )
        self.assertEqual(measured['fft_core_iterations'], 20)
        self.assertEqual(measured['fft_core_avg_us'], 12.5)
        print_mock.assert_any_call('BENCH:fft_core:20:12.5')

    def test_runner_rejects_malformed_benchmark_records(self):
        completed = mock.Mock(
            returncode=0,
            stdout='RESULT:fft_core_freq:1000.0\nBENCH:fft_core:0:12.5\n',
            stderr='',
        )
        with mock.patch('run_test.subprocess.run', return_value=completed):
            with self.assertRaises(ValueError):
                run_test.run_executable('build-dir', 'test_fft_core')

    def test_resource_benchmarks_reject_missing_phase_algorithm(self):
        with self.assertRaises(ValueError):
            run_test.validate_benchmark_algorithms(
                'phase',
                [{'algorithm': 'iq_phase', 'iterations': 20, 'average_us': 1.0}],
            )

    def test_resource_benchmarks_reject_duplicate_phase_algorithm(self):
        with self.assertRaises(ValueError):
            run_test.validate_benchmark_algorithms(
                'phase',
                [
                    {'algorithm': 'iq_phase', 'iterations': 20, 'average_us': 1.0},
                    {'algorithm': 'iq_phase', 'iterations': 20, 'average_us': 1.0},
                    {'algorithm': 'xiebo_fundamental', 'iterations': 20, 'average_us': 1.0},
                ],
            )

    def test_resource_benchmarks_match_each_module_contract(self):
        self.assertEqual(
            run_test.validate_benchmark_algorithms(
                'phase',
                [
                    {'algorithm': 'iq_phase', 'iterations': 20, 'average_us': 1.0},
                    {'algorithm': 'xiebo_fundamental', 'iterations': 20, 'average_us': 1.0},
                ],
            ),
            None,
        )

    def test_compiler_description_uses_cmake_cache_compiler(self):
        with tempfile.TemporaryDirectory() as build_dir:
            compiler = os.path.join(build_dir, 'actual-gcc.exe')
            with open(compiler, 'w', encoding='utf-8') as stream:
                stream.write('placeholder')
            with open(os.path.join(build_dir, 'CMakeCache.txt'), 'w', encoding='utf-8') as stream:
                stream.write(f'CMAKE_C_COMPILER:STRING={compiler}\n')
            completed = mock.Mock(returncode=0, stdout='Actual GCC 1.2.3\n', stderr='')
            with mock.patch('run_test.subprocess.run', return_value=completed) as run:
                self.assertEqual(run_test.describe_configured_compiler(build_dir), 'Actual GCC 1.2.3')
            run.assert_called_once_with([compiler, '--version'], capture_output=True, text=True)

    def test_compiler_cache_parser_accepts_filepath_and_rejects_missing_path(self):
        with tempfile.TemporaryDirectory() as build_dir:
            compiler = os.path.join(build_dir, 'actual-gcc.exe')
            with open(compiler, 'w', encoding='utf-8') as stream:
                stream.write('placeholder')
            cache_path = os.path.join(build_dir, 'CMakeCache.txt')
            with open(cache_path, 'w', encoding='utf-8') as stream:
                stream.write(f'CMAKE_C_COMPILER:FILEPATH={compiler}\n')
            self.assertEqual(run_test.compiler_from_cmake_cache(build_dir), compiler)
            with open(cache_path, 'w', encoding='utf-8') as stream:
                stream.write('CMAKE_C_COMPILER:FILEPATH=missing-gcc.exe\n')
            with self.assertRaises(FileNotFoundError):
                run_test.compiler_from_cmake_cache(build_dir)

    def test_resource_baseline_case_selection(self):
        self.assertTrue(run_test.is_resource_baseline('frequency', 'integer_bin', 'full'))
        self.assertFalse(run_test.is_resource_baseline('frequency', 'with_noise', 'full'))
        self.assertTrue(run_test.is_resource_baseline('phase', 'custom', 'custom'))
        self.assertTrue(
            run_test.is_resource_baseline('frequency', 'non_integer_bin', 'smoke')
        )

    def test_resource_records_attach_target_sizes_to_each_benchmark(self):
        records = run_test.make_resource_records(
            'test_phase',
            {'samples': 1024},
            [
                {'algorithm': 'iq_phase', 'iterations': 30, 'average_us': 1.5},
                {'algorithm': 'xiebo_fundamental', 'iterations': 30, 'average_us': 3.0},
            ],
            {
                'executable_bytes': 1000,
                'text_bytes': 100,
                'data_bytes': 20,
                'bss_bytes': 30,
            },
        )
        self.assertEqual(len(records), 2)
        self.assertEqual(
            records[0],
            {
                'target': 'test_phase', 'algorithm': 'iq_phase', 'samples': 1024,
                'iterations': 30, 'average_us': 1.5, 'executable_bytes': 1000,
                'text_bytes': 100, 'data_bytes': 20, 'bss_bytes': 30,
            },
        )

    def test_phase_runner_emits_required_benchmark_contracts(self):
        source_path = os.path.join(
            run_test.PROJECT_ROOT, 'test', 'test_runner', 'test_phase.c',
        )
        with open(source_path, encoding='utf-8', errors='replace') as stream:
            source = stream.read()
        self.assertIn('#include "benchmark.h"', source)
        self.assertIn('BENCH:iq_phase:', source)
        self.assertIn('BENCH:xiebo_fundamental:', source)
        self.assertIn('volatile float32_t benchmark_sink', source)

    def test_fir_contract_generates_numpy_convolution_reference(self):
        self.assertEqual(
            run_test.MODULES['fir'],
            {'target': 'test_fir_response', 'samples': 1024, 'freq': 1000.0},
        )
        cases = run_test.suite_cases('fir', 'full')
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]['samples'], 1024)
        self.assertEqual(cases[0]['waveform'], 'sine')

        signal, raw = generate_signal(
            'sine', 1000.0, 1.0, 0.0, 51200.0, 1024, seed=20260717,
        )
        expected = np.convolve(
            signal.astype(np.float64), FIR_COEFFICIENTS, mode='full',
        )[:len(signal)].astype(np.float32)
        self.assertEqual(expected.shape, signal.shape)
        self.assertTrue(np.isfinite(expected).all())

        with tempfile.TemporaryDirectory() as output_dir:
            metadata = {
                'waveform': 'sine', 'freq': 1000.0, 'amplitude': 1.0,
                'phase': 0.0, 'sample_rate': 51200.0, 'samples': 1024,
            }
            header_path = write_signal_header(
                signal, raw, output_dir, metadata, expected_fir_output=expected,
            )
            with open(header_path, encoding='utf-8') as stream:
                header = stream.read()
        self.assertIn('static const float expected_fir_output[SIGNAL_LENGTH]', header)

        checks = run_test.expected_checks('fir', cases[0])
        self.assertEqual(checks['fir_max_abs_error'][0], 0.0)
        self.assertEqual(checks['fir_max_abs_error'][1]['kind'], 'absolute')
        self.assertEqual(checks['fir_max_abs_error'][1]['tolerance'], 1.0e-5)


class ReportCompatibilityTests(unittest.TestCase):
    def test_report_accepts_metadata_results_payload(self):
        payload = {
            "metadata": {"suite": "smoke", "seed": 20260717},
            "results": [
                {
                    "module": "frequency",
                    "case_id": "integer_bin",
                    "label": "fft_peak",
                    "expected": 1000.0,
                    "actual": 1000.0,
                    "abs_error": 0.0,
                    "rel_error": 0.0,
                    "status": "PASS",
                    "tolerance": "half FFT bin",
                }
            ],
        }
        markdown = report.generate_report(payload, "Regression Report")
        self.assertIn("Suite", markdown)
        self.assertIn("smoke", markdown)
        self.assertIn("integer_bin", markdown)

    def test_report_still_accepts_legacy_list(self):
        legacy = [
            {
                "module": "amplitude",
                "label": "rms_sine",
                "expected": 1.0,
                "actual": 1.0,
                "abs_error": 0.0,
                "rel_error": 0.0,
                "status": "PASS",
            }
        ]
        markdown = report.generate_report(legacy)
        self.assertIn("rms_sine", markdown)


if __name__ == "__main__":
    unittest.main()
