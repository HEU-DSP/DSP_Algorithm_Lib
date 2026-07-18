"""Render JSON output from run_test.py as a Markdown verification report."""

import argparse
from datetime import datetime
import json


def _unpack(payload):
    if isinstance(payload, dict):
        return payload.get('metadata', {}), payload.get('results', [])
    return {}, payload


def generate_report(payload, title="DSP Algorithm Test Report"):
    metadata, results = _unpack(payload)
    lines = [
        f'# {title}',
        '',
        f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        '',
    ]

    if metadata:
        lines.extend(['## Run metadata', '', '| Field | Value |', '|-------|-------|'])
        for key, value in metadata.items():
            lines.append(f'| {key.replace("_", " ").title()} | {value} |')
        lines.append('')

    lines.extend([
        '## 修订结论',
        '',
        '- 原报告中 RMS 三项约 1.54% 的统一偏高是实质缺陷：循环多处理了一个样本，但仍按原长度归一化。现已修正边界。',
        '- 原报告中 CZT 幅值约为 1.5708 倍也是实质缺陷：归一化公式误乘了 π/2，并且峰值搜索越界。两项均已修正。',
        '- 原报告的 45° 测相 PASS 属于假阳性。旧公式实际返回 `90° - 输入相位`，只有 45° 恰好相等；修订数据集覆盖负角、0°、90°、跨 ±180° 和噪声。',
        '- 原报告只用整数 FFT 频点，未真正检验插值。修订后增加非整数频点，并采用对数抛物线插值。',
        '- 表中 Expected 来自信号生成参数，不由另一份同类测量算法计算，避免 C 与 Python 同错。',
        '- PASS 只代表本报告列出的确定性仿真用例；不等同于已完成硬件、全动态范围或所有信噪比验证。',
        '- `czt_Phase()` 暂未列为已验证结果：当前实现没有保留去啁啾后的最终复数 CZT 输出。',
        '',
    ])

    total = len(results)
    counts = {
        status: sum(1 for result in results if result.get('status') == status)
        for status in ('PASS', 'FAIL', 'NO_RESULT', 'ERROR')
    }
    lines.extend([
        '## Summary',
        '',
        '| Metric | Value |',
        '|--------|-------|',
        f'| Total tests | {total} |',
        f'| PASS | {counts["PASS"]} |',
        f'| FAIL | {counts["FAIL"]} |',
        f'| NO_RESULT | {counts["NO_RESULT"]} |',
        f'| ERROR | {counts["ERROR"]} |',
    ])
    if total:
        lines.append(f'| Pass rate | {counts["PASS"] / total * 100:.1f}% |')
    lines.append('')

    groups = {}
    for result in results:
        groups.setdefault(result['module'], []).append(result)

    module_names = {
        'frequency': '测频',
        'amplitude': '测幅',
        'phase': '测相',
        'czt': 'CZT 频谱细化',
    }
    for module, module_results in groups.items():
        lines.extend([
            f'## {module_names.get(module, module)} ({module})',
            '',
            '| Case | Algorithm | Expected | Measured | Abs Error | Rel Error | Tolerance | Status |',
            '|------|-----------|----------|----------|-----------|-----------|-----------|--------|',
        ])
        for result in module_results:
            expected = _format_number(result.get('expected'))
            actual = _format_number(result.get('actual'))
            abs_error = _format_number(result.get('abs_error'), signed=True)
            rel = result.get('rel_error')
            rel_error = f'{rel * 100:+.4f}%' if rel is not None else 'N/A'
            lines.append(
                f'| {result.get("case_id", "default")} | {result["label"]} | '
                f'{expected} | {actual} | {abs_error} | {rel_error} | '
                f'{result.get("tolerance", "N/A")} | '
                f'{result.get("status", "?")} |'
            )
        lines.append('')

    return '\n'.join(lines)


def _format_number(value, signed=False):
    if value is None:
        return 'N/A'
    return f'{value:+.6f}' if signed else f'{value:.6f}'


def main():
    parser = argparse.ArgumentParser(description='DSP Test Report Generator')
    parser.add_argument('--input', required=True, help='JSON from run_test.py --save-json')
    parser.add_argument('--output', default='test_report.md', help='Markdown output path')
    parser.add_argument('--title', default='DSP Algorithm Test Report')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as stream:
        payload = json.load(stream)
    with open(args.output, 'w', encoding='utf-8') as stream:
        stream.write(generate_report(payload, args.title))
    print(f'Report saved to: {args.output}')


if __name__ == '__main__':
    main()
