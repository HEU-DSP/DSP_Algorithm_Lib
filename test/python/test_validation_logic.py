import json
import math
import os
import tempfile
import unittest
from unittest import mock

import numpy as np

import run_test
import report
import golden_reference
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

    def test_noncoherent_phase_cases_only_check_iq_phase(self):
        cases = run_test.suite_cases('phase', 'full')
        noncoherent = [case for case in cases if case['phase_only']]
        self.assertEqual(len(noncoherent), 2)
        self.assertEqual([case['freq'] for case in noncoherent], [712.20777, 137.4])
        self.assertAlmostEqual(math.degrees(noncoherent[0]['phase']), 80.0)
        self.assertAlmostEqual(math.degrees(noncoherent[1]['phase']), -120.0)
        self.assertEqual([case['noise'] for case in noncoherent], [0.0, 0.01])
        for case in noncoherent:
            checks = run_test.expected_checks('phase', case)
            self.assertEqual(set(checks), {'iq_phase'})
            self.assertEqual(checks['iq_phase'][1]['tolerance'], math.radians(0.5))

    def test_fft_interpolation_reference_uses_log_magnitudes(self):
        fs = 51200.0
        samples = 8192
        frequency = 1003.7
        signal, _ = generate_signal(
            'sine', frequency, 1.0, 0.23, fs, samples, seed=20260717,
        )
        reference = golden_reference.ref_frequency_fft_interp(signal, fs)
        magnitudes = np.abs(np.fft.fft(signal)[:samples // 2])
        index = int(np.argmax(magnitudes[1:]) + 1)
        log_mag = np.log(np.maximum(magnitudes, 1.0e-12))
        denominator = log_mag[index - 1] - 2.0 * log_mag[index] + log_mag[index + 1]
        expected = (index + 0.5 * (log_mag[index - 1] - log_mag[index + 1]) /
                    denominator) * fs / samples
        self.assertAlmostEqual(reference, expected, places=9)

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

    def test_resource_benchmarks_cover_all_algorithm_targets(self):
        self.assertEqual(
            run_test.RESOURCE_BENCHMARK_ALGORITHMS['amplitude'],
            {'rms_sine', 'rms_square', 'rms_triangle'},
        )
        self.assertEqual(run_test.RESOURCE_BENCHMARK_ALGORITHMS['czt'], {'czt_zoom'})
        self.assertEqual(
            run_test.RESOURCE_BENCHMARK_ALGORITHMS['safety'], {'safety_wrappers'},
        )
        self.assertTrue(run_test.is_resource_baseline('amplitude', 'sine_1v', 'full'))
        self.assertTrue(
            run_test.is_resource_baseline('czt', 'freq_1000p3_amp_0p7', 'full')
        )
        self.assertTrue(
            run_test.is_resource_baseline('safety', 'fixed_size_wrappers', 'full')
        )
        self.assertEqual(
            sum(len(algorithms) for algorithms in
                run_test.RESOURCE_BENCHMARK_ALGORITHMS.values()),
            16,
        )

    def test_readmes_declare_breaking_include_migration_and_sanity_scope(self):
        with open(os.path.join(run_test.PROJECT_ROOT, 'README.md'),
                  encoding='utf-8') as stream:
            root_readme = stream.read()
        with open(os.path.join(run_test.PROJECT_ROOT, 'test', 'README.md'),
                  encoding='utf-8') as stream:
            test_readme = stream.read()

        self.assertIn('目录迁移与兼容性（Breaking）', root_readme)
        self.assertIn('FFTNt.h', root_readme)
        self.assertIn('freq_measure/fft/fft_n.h', root_readme)
        self.assertIn('IIR.h', root_readme)
        self.assertIn('phase_measure/fir_filter/fir_filter.h', root_readme)
        self.assertIn('test_sanity', test_readme)
        self.assertIn('不属于算法运行时资源目标', test_readme)

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
        self.assertEqual(len(cases), 2)
        self.assertEqual(cases[0]['samples'], 1024)
        self.assertEqual(cases[0]['waveform'], 'sine')
        self.assertEqual(cases[1]['case_id'], 'fir_impulse')
        self.assertEqual(cases[1]['waveform'], 'impulse')

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

        impulse = np.zeros(1024, dtype=np.float32)
        impulse[0] = 1.0
        impulse_expected = np.convolve(
            impulse.astype(np.float64), FIR_COEFFICIENTS, mode='full',
        )[:len(impulse)].astype(np.float32)
        np.testing.assert_allclose(impulse_expected[:11], FIR_COEFFICIENTS)
        np.testing.assert_array_equal(impulse_expected[11:], 0.0)


class ReportCompatibilityTests(unittest.TestCase):
    def test_report_renders_pc_gcc_resources_and_coverage_matrix(self):
        payload = {
            "metadata": {"suite": "full"},
            "results": [],
            "resources": [
                {
                    "target": "test_fft_core", "algorithm": "fft_core",
                    "samples": 8192, "iterations": 40, "average_us": 12.5,
                    "executable_bytes": 12345, "text_bytes": 1000,
                    "data_bytes": 24, "bss_bytes": 256,
                }
            ],
        }

        markdown = report.generate_report(payload, "Resource Report")

        self.assertIn("## 资源占用（PC/GCC 参考）", markdown)
        self.assertIn("平均耗时", markdown)
        self.assertIn(".text", markdown)
        self.assertIn(".data", markdown)
        self.assertIn(".bss", markdown)
        self.assertIn("不是 STM32 目标测量值", markdown)
        self.assertIn("test_sanity", markdown)
        self.assertIn("不属于算法运行时资源目标", markdown)
        self.assertIn("## 测频/测相源码覆盖矩阵", markdown)
        self.assertIn("freq_measure/fft/fft_n.c", markdown)
        self.assertIn("phase_measure/iq_demod/mag_phase.c", markdown)
        self.assertIn("phase_measure/fir_filter/fir_filter.c", markdown)

    def test_report_explains_missing_legacy_resource_rows(self):
        markdown = report.generate_report({"metadata": {}, "results": []})

        self.assertIn("## 资源占用（PC/GCC 参考）", markdown)
        self.assertIn("没有资源数据", markdown)

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
