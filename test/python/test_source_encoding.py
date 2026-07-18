"""Regression checks for readable UTF-8 comments in owned C sources."""

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
OWNED_SOURCE_DIRS = (
    "backend",
    "freq_measure",
    "amp_measure",
    "phase_measure",
    "test/test_runner",
)
MOJIBAKE = re.compile(r"\ufffd|\?{3,}|锟斤拷|烫烫烫|屯屯屯")


class SourceEncodingTests(unittest.TestCase):
    def test_owned_c_sources_are_readable_utf8_without_mojibake(self) -> None:
        failures = []

        for relative_dir in OWNED_SOURCE_DIRS:
            source_dir = REPO_ROOT / relative_dir
            for path in sorted(source_dir.rglob("*")):
                if path.suffix.lower() not in {".c", ".h"}:
                    continue

                try:
                    text = path.read_text(encoding="utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    failures.append(f"{path.relative_to(REPO_ROOT)}: invalid UTF-8 ({exc})")
                    continue

                for line_number, line in enumerate(text.splitlines(), start=1):
                    if MOJIBAKE.search(line):
                        failures.append(
                            f"{path.relative_to(REPO_ROOT)}:{line_number}: {line.strip()}"
                        )

        self.assertEqual([], failures, "Unreadable source comments:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
