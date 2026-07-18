"""Generate deterministic signals, build C runners, and validate their output."""

import argparse
from datetime import datetime, timezone
import json
import math
import os
import shutil
import subprocess
import sys

from signal_generator import generate_signal, write_signal_header


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GENERATED_DIR = os.path.join(PROJECT_ROOT, 'test', 'generated')
DEFAULT_BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')
DEFAULT_SEED = 20260717

MODULES = {
    'frequency': {'target': 'test_frequency', 'samples': 8192, 'freq': 1000.0},
    'fft_core': {'target': 'test_fft_core', 'samples': 8192, 'freq': 1000.0},
    'amplitude': {'target': 'test_amplitude', 'samples': 4096, 'freq': 1000.0},
    'mag_phase': {'target': 'test_mag_phase', 'samples': 4096, 'freq': 1000.0},
    'phase': {'target': 'test_phase', 'samples': 1024, 'freq': 50.0},
    'czt': {'target': 'test_czt', 'samples': 2048, 'freq': 1000.3},
    'safety': {'target': 'test_safety', 'samples': 1024, 'freq': 50.0},
}


def value_or_default(value, default):
    return default if value is None else value


def circular_abs_error(actual, expected):
    return abs((actual - expected + math.pi) % (2.0 * math.pi) - math.pi)


def resolve_cmake_command(build_dir, override=None):
    if override:
        return override
    discovered = shutil.which('cmake')
    if discovered:
        return discovered
    cache_path = os.path.join(build_dir, 'CMakeCache.txt')
    if os.path.isfile(cache_path):
        with open(cache_path, 'r', encoding='utf-8', errors='replace') as stream:
            for line in stream:
                if line.startswith('CMAKE_COMMAND:INTERNAL='):
                    return line.split('=', 1)[1].strip()
    raise FileNotFoundError(
        'CMake not found. Pass --cmake, add it to PATH, or configure the build directory once.'
    )


def describe_cmake(cmake):
    completed = subprocess.run([cmake, '--version'], capture_output=True, text=True)
    if completed.returncode == 0 and completed.stdout.strip():
        return completed.stdout.splitlines()[0]
    return os.path.basename(cmake)


def make_error_result(module, case_id, error):
    return {
        'module': module, 'case_id': case_id, 'label': 'module_execution',
        'expected': None, 'actual': None, 'abs_error': None, 'rel_error': None,
        'status': 'ERROR', 'tolerance': None, 'message': str(error),
    }


def has_failures(results):
    return any(item.get('status') != 'PASS' for item in results)


def evaluate_check(module, case_id, label, expected, actual, check):
    if actual is None:
        return {
            'module': module, 'case_id': case_id, 'label': label,
            'expected': expected, 'actual': None, 'abs_error': None,
            'rel_error': None, 'status': 'NO_RESULT',
            'tolerance': check.get('description', str(check['tolerance'])),
        }

    kind = check['kind']
    if kind == 'phase':
        abs_error = circular_abs_error(actual, expected)
        rel_error = None
        passed = abs_error <= check['tolerance']
    else:
        abs_error = abs(actual - expected)
        rel_error = abs_error / abs(expected) if abs(expected) > 1e-12 else abs_error
        passed = (abs_error <= check['tolerance'] if kind == 'absolute'
                  else rel_error <= check['tolerance'])
    return {
        'module': module, 'case_id': case_id, 'label': label,
        'expected': expected, 'actual': actual, 'abs_error': abs_error,
        'rel_error': rel_error, 'status': 'PASS' if passed else 'FAIL',
        'tolerance': check.get('description', str(check['tolerance'])),
    }


def _case(case_id, waveform='sine', freq=1000.0, amplitude=1.0, phase=0.0,
          samples=8192, fs=51200.0, noise=0.0, adc_bits=0, seed=DEFAULT_SEED):
    return dict(case_id=case_id, waveform=waveform, freq=freq, amplitude=amplitude,
                phase=phase, samples=samples, fs=fs, noise=noise,
                adc_bits=adc_bits, seed=seed)


def _seed_cases(cases, seed):
    return [dict(case, seed=seed) for case in cases]


def suite_cases(module, suite, seed=DEFAULT_SEED):
    if module == 'frequency':
        full = [
            _case('integer_bin', freq=1000.0, samples=8192, adc_bits=12),
            _case('non_integer_bin', freq=1003.7, samples=8192, adc_bits=12),
            _case('with_noise', freq=997.3, samples=8192, noise=0.02, adc_bits=12),
            _case('quantized_non_integer', freq=1234.5, samples=8192, adc_bits=12),
        ]
        return _seed_cases(full if suite == 'full' else full[1:2], seed)
    if module == 'fft_core':
        full = [
            _case('integer_bin', freq=1000.0, samples=8192),
            _case('second_integer_bin', freq=1250.0, amplitude=0.7,
                  samples=8192),
        ]
        return _seed_cases(full if suite == 'full' else full[:1], seed)
    if module == 'amplitude':
        full = [
            _case('sine_1v', waveform='sine', freq=1000.0, samples=4096, adc_bits=12),
            _case('square_0p8v', waveform='square', freq=800.0, amplitude=0.8,
                  samples=4096, adc_bits=12),
            _case('triangle_1p2v', waveform='triangle', freq=800.0, amplitude=1.2,
                  samples=4096, adc_bits=12),
        ]
        return _seed_cases(full, seed)
    if module == 'mag_phase':
        full = [
            _case('sine_1v', waveform='sine', freq=1000.0, samples=4096, adc_bits=12),
            _case('square_0p8v', waveform='square', freq=1000.0, amplitude=0.8,
                  samples=4096, adc_bits=12),
            _case('triangle_1p2v', waveform='triangle', freq=1000.0, amplitude=1.2,
                  samples=4096, adc_bits=12),
        ]
        return _seed_cases(full if suite == 'full' else full[:1], seed)
    if module == 'phase':
        degrees = [-170, -90, -30, 0, 45, 90, 170]
        full = [
            _case(f'phase_{degree:+d}deg', freq=50.0, phase=math.radians(degree),
                  samples=1024)
            for degree in degrees
        ]
        full.append(_case('phase_45deg_noise', freq=50.0, phase=math.pi / 4,
                          samples=1024, noise=0.01))
        return _seed_cases(full if suite == 'full' else [full[3], full[4]], seed)
    if module == 'czt':
        full = [
            _case('freq_1000p3_amp_0p7', freq=1000.3, amplitude=0.7, phase=0.2,
                  samples=2048),
            _case('freq_1234p6_amp_1p2', freq=1234.6, amplitude=1.2, phase=-0.4,
                  samples=2048),
        ]
        return _seed_cases(full if suite == 'full' else full[:1], seed)
    if module == 'safety':
        return _seed_cases([_case('fixed_size_wrappers', samples=1024)], seed)
    raise ValueError(f'Unknown module: {module}')


def custom_case(module, args):
    config = MODULES[module]
    waveform = 'sine' if module in ('frequency', 'fft_core', 'phase', 'czt', 'safety') else args.waveform
    adc_bits = args.adc_bits
    if module in ('frequency', 'amplitude', 'mag_phase') and adc_bits == 0:
        adc_bits = 12
    return _case(
        'custom', waveform=waveform,
        freq=value_or_default(args.freq, config['freq']), amplitude=args.amp,
        phase=value_or_default(args.phase, 0.0),
        samples=value_or_default(args.samples, config['samples']),
        fs=args.fs, noise=args.noise, adc_bits=adc_bits, seed=args.seed,
    )


def expected_checks(module, case):
    freq = case['freq']
    if module == 'frequency':
        fft_bin = case['fs'] / case['samples']
        return {
            'fft_interp': (freq, {'kind': 'relative', 'tolerance': 0.001,
                                  'description': 'relative error <= 0.1%'}),
            'fft_peak': (freq, {'kind': 'absolute', 'tolerance': fft_bin / 2 + 1e-6,
                                'description': 'absolute error <= half FFT bin'}),
            'zero_cross_freq': (freq, {'kind': 'relative', 'tolerance': 0.001,
                                       'description': 'relative error <= 0.1%'}),
            'zero_cross_period': (1.0 / freq, {'kind': 'relative', 'tolerance': 0.001,
                                               'description': 'relative error <= 0.1%'}),
        }
    if module == 'amplitude':
        labels = {'sine': 'rms_sine', 'square': 'rms_square', 'triangle': 'rms_triangle'}
        return {labels[case['waveform']]: (
            case['amplitude'], {'kind': 'relative', 'tolerance': 0.005,
                                'description': 'relative error <= 0.5%'})}
    if module == 'mag_phase':
        labels = {
            'sine': 'mag_phase_sine',
            'square': 'mag_phase_square',
            'triangle': 'mag_phase_triangle',
        }
        return {labels[case['waveform']]: (
            case['amplitude'], {'kind': 'relative', 'tolerance': 0.005,
                                'description': 'relative error <= 0.5%'})}
    if module == 'phase':
        return {
            'iq_phase': (case['phase'], {'kind': 'phase',
                                         'tolerance': math.radians(0.5),
                                         'description': 'circular error <= 0.5 degree'}),
            'xiebo_fundamental': (
                case['amplitude'] * case['samples'] / 2.0,
                {'kind': 'relative', 'tolerance': 0.005,
                 'description': 'relative error <= 0.5%'}),
        }
    if module == 'czt':
        start = max(int(freq) - 100, 0)
        end = int(freq) + 100
        scan_step = (end - start) / 2047.0
        return {
            'czt_freq': (freq, {'kind': 'absolute', 'tolerance': scan_step,
                                'description': 'absolute error <= one CZT scan step'}),
            'czt_amp': (case['amplitude'], {'kind': 'relative', 'tolerance': 0.005,
                                            'description': 'relative error <= 0.5%'}),
        }
    if module == 'fft_core':
        fft_bin = case['fs'] / case['samples']
        return {
            'fft_core_freq': (freq, {
                'kind': 'absolute', 'tolerance': fft_bin / 2.0,
                'description': 'absolute error <= half FFT bin',
            }),
            'fft_core_magnitude': (case['amplitude'] * case['samples'] / 2.0, {
                'kind': 'relative', 'tolerance': 0.005,
                'description': 'relative error <= 0.5%',
            }),
        }
    if module == 'safety':
        return {
            'iq_invalid_length_unchanged': (
                1.0, {'kind': 'absolute', 'tolerance': 0.0,
                      'description': 'invalid length leaves output unchanged'}),
            'fir_zero_max_abs': (
                0.0, {'kind': 'absolute', 'tolerance': 1.0e-6,
                      'description': 'zero-input FIR output <= 1e-6'}),
        }
    raise ValueError(f'Unknown module: {module}')


def ensure_configured(cmake, build_dir, args):
    if os.path.isfile(os.path.join(build_dir, 'CMakeCache.txt')):
        return
    command = [cmake, '-S', PROJECT_ROOT, '-B', build_dir]
    if args.generator:
        command.extend(['-G', args.generator])
    if args.c_compiler:
        command.append(f'-DCMAKE_C_COMPILER={args.c_compiler}')
    if args.make_program:
        command.append(f'-DCMAKE_MAKE_PROGRAM={args.make_program}')
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(f'CMake configure failed:\n{completed.stdout}\n{completed.stderr}')


def build_target(cmake, build_dir, target):
    completed = subprocess.run(
        [cmake, '--build', build_dir, '--target', target],
        capture_output=True, text=True,
    )
    if completed.returncode:
        raise RuntimeError(f'Build failed for {target}:\n{completed.stdout}\n{completed.stderr}')


def run_executable(build_dir, target):
    suffix = '.exe' if os.name == 'nt' else ''
    path = os.path.join(build_dir, 'test', target + suffix)
    completed = subprocess.run([path], capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(f'{target} exited with {completed.returncode}:\n{completed.stderr}')
    measured = {}
    for line in completed.stdout.splitlines():
        if line.startswith('RESULT:'):
            _, label, value = line.split(':', 2)
            measured[label.strip()] = float(value.strip())
        elif line.startswith('BENCH:'):
            print(line)
    return measured


def run_case(module, case, cmake, build_dir):
    signal, raw = generate_signal(
        case['waveform'], case['freq'], case['amplitude'], case['phase'],
        case['fs'], case['samples'], case['noise'], case['adc_bits'], 3.3,
        case['seed'],
    )
    metadata = {
        'waveform': case['waveform'], 'freq': case['freq'],
        'amplitude': case['amplitude'], 'phase': case['phase'],
        'sample_rate': case['fs'], 'samples': case['samples'],
        'noise_std': case['noise'], 'adc_bits': case['adc_bits'], 'vref': 3.3,
    }
    write_signal_header(signal, raw, GENERATED_DIR, metadata)
    target = MODULES[module]['target']
    build_target(cmake, build_dir, target)
    measured = run_executable(build_dir, target)

    results = []
    for label, (expected, check) in expected_checks(module, case).items():
        result = evaluate_check(
            module, case['case_id'], label, expected, measured.get(label), check,
        )
        results.append(result)
        print(f'  [{result["status"]:9s}] {case["case_id"]:24s} {label:22s} '
              f'expected={expected:.6f} actual={result["actual"]}')
    return results


def parse_args():
    parser = argparse.ArgumentParser(description='DSP Algorithm Test Orchestrator')
    parser.add_argument('--module', default='all',
                        choices=['frequency', 'fft_core', 'amplitude', 'mag_phase', 'phase', 'czt', 'safety', 'all'])
    parser.add_argument('--suite', default='smoke', choices=['smoke', 'full', 'custom'])
    parser.add_argument('--waveform', default='sine', choices=['sine', 'square', 'triangle'])
    parser.add_argument('--freq', type=float, default=None)
    parser.add_argument('--amp', type=float, default=1.0)
    parser.add_argument('--phase', type=float, default=None)
    parser.add_argument('--fs', type=float, default=51200.0)
    parser.add_argument('--samples', type=int, default=None)
    parser.add_argument('--noise', type=float, default=0.0)
    parser.add_argument('--adc-bits', type=int, default=0)
    parser.add_argument('--seed', type=int, default=DEFAULT_SEED)
    parser.add_argument('--build-dir', default=DEFAULT_BUILD_DIR)
    parser.add_argument('--cmake', default=None, help='Absolute path to cmake executable')
    parser.add_argument('--generator', default=None)
    parser.add_argument('--c-compiler', default=None)
    parser.add_argument('--make-program', default=None)
    parser.add_argument('--save-json', default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    build_dir = os.path.abspath(args.build_dir)
    cmake = resolve_cmake_command(build_dir, args.cmake)
    ensure_configured(cmake, build_dir, args)
    modules = list(MODULES) if args.module == 'all' else [args.module]

    all_results = []
    for module in modules:
        cases = ([custom_case(module, args)] if args.suite == 'custom'
                 else suite_cases(module, args.suite, args.seed))
        print(f'\n== {module}: {len(cases)} case(s) ==')
        for case in cases:
            try:
                all_results.extend(run_case(module, case, cmake, build_dir))
            except Exception as error:
                print(f'  [ERROR    ] {case["case_id"]}: {error}')
                all_results.append(make_error_result(module, case['case_id'], error))

    counts = {status: sum(r['status'] == status for r in all_results)
              for status in ('PASS', 'FAIL', 'NO_RESULT', 'ERROR')}
    print(f'\nSummary: {counts["PASS"]} PASS, {counts["FAIL"]} FAIL, '
          f'{counts["NO_RESULT"]} NO_RESULT, {counts["ERROR"]} ERROR')

    payload = {
        'metadata': {
            'suite': args.suite, 'seed': args.seed,
            'generated_utc': datetime.now(timezone.utc).isoformat(),
            'cmake': describe_cmake(cmake),
        },
        'results': all_results,
    }
    if args.save_json:
        output = os.path.abspath(args.save_json)
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'w', encoding='utf-8') as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
        print(f'Results saved to: {output}')

    return 1 if has_failures(all_results) else 0


if __name__ == '__main__':
    sys.exit(main())
