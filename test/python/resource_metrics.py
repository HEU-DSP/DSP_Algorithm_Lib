"""Strict GNU host-executable resource collection helpers."""

import math
import os
import re
import shutil
import subprocess


DECIMAL_NUMBER = re.compile(
    r'^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$'
)


def parse_gnu_size_output(output):
    """Return section byte counts from the first numeric GNU ``size -B`` row."""
    for line in output.splitlines():
        fields = line.split()
        if not fields or not fields[0].isdigit():
            continue
        if (len(fields) < 6 or any(not field.isdigit() for field in fields[:4])):
            raise ValueError(f'Malformed GNU size row: {line!r}')
        try:
            text_bytes = int(fields[0])
            data_bytes = int(fields[1])
            bss_bytes = int(fields[2])
            int(fields[4], 16)
        except ValueError as error:
            raise ValueError(f'Malformed GNU size row: {line!r}') from error
        if min(text_bytes, data_bytes, bss_bytes) < 0:
            raise ValueError(f'Negative GNU size section: {line!r}')
        return {
            'text_bytes': text_bytes,
            'data_bytes': data_bytes,
            'bss_bytes': bss_bytes,
        }
    raise ValueError('GNU size output has no numeric section row')


def parse_benchmark_line(line):
    """Parse and validate one ``BENCH:algorithm:iterations:average_us`` line."""
    fields = line.strip().split(':')
    if len(fields) != 4 or fields[0] != 'BENCH' or not fields[1].strip():
        raise ValueError(f'Malformed BENCH record: {line!r}')
    algorithm = fields[1].strip()
    if not DECIMAL_NUMBER.fullmatch(fields[3].strip()):
        raise ValueError(f'Invalid BENCH average time: {line!r}')
    try:
        iterations = int(fields[2].strip())
    except ValueError as error:
        raise ValueError(f'Invalid BENCH iterations: {line!r}') from error
    if iterations <= 0 or str(iterations) != fields[2].strip():
        raise ValueError(f'Invalid BENCH iterations: {line!r}')
    try:
        average_us = float(fields[3].strip())
    except ValueError as error:
        raise ValueError(f'Invalid BENCH average time: {line!r}') from error
    if not math.isfinite(average_us) or average_us <= 0.0:
        raise ValueError(f'Invalid BENCH average time: {line!r}')
    return {
        'algorithm': algorithm,
        'iterations': iterations,
        'average_us': average_us,
    }


def resolve_size_command():
    """Resolve GNU ``size`` from PATH or raise a visible error."""
    size_command = shutil.which('size')
    if not size_command:
        raise FileNotFoundError('GNU size not found in PATH')
    return size_command


def collect_resource_metrics(executable, size_command=None):
    """Collect host executable and GNU section sizes for one built runner."""
    if not os.path.isfile(executable):
        raise FileNotFoundError(f'Executable not found: {executable}')
    if size_command is None:
        size_command = resolve_size_command()
    completed = subprocess.run(
        [size_command, '-B', executable], capture_output=True, text=True,
    )
    if completed.returncode:
        raise RuntimeError(
            f'GNU size failed for {executable}: {completed.stderr.strip()}'
        )
    sections = parse_gnu_size_output(completed.stdout)
    metrics = {'executable_bytes': os.path.getsize(executable), **sections}
    if (metrics['executable_bytes'] <= 0 or metrics['text_bytes'] <= 0
            or metrics['data_bytes'] <= 0 or metrics['bss_bytes'] < 0):
        raise ValueError(f'Invalid GNU host executable resource sizes: {metrics}')
    return metrics
