#!/usr/bin/env python3
"""Export lesson 003 or 008 into a flat repo for Streamlit Community Cloud.

Usage::

    python scripts/export_streamlit_cloud.py 003
    python scripts/export_streamlit_cloud.py 008 --out /path/to/streamlit-psi-drift-alert

Does not push. Patches ``repo_root()`` to avoid ``git rev-parse``.
Vendors freeze sample slices under ``samples/``.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LESSONS: dict[str, dict] = {
    "003": {
        "src": ROOT / "003_ks_drift_alert_streamlit",
        "default_out": ROOT.parent / "streamlit-ks-drift-alert",
        "name": "streamlit-ks-drift-alert",
    },
    "008": {
        "src": ROOT / "008_psi_drift_alert_streamlit",
        "default_out": ROOT.parent / "streamlit-psi-drift-alert",
        "name": "streamlit-psi-drift-alert",
    },
}

# Runtime deps for offline Streamlit (no BentoML on Cloud).
CLOUD_REQUIREMENTS = """\
# Generated for Streamlit Community Cloud (offline demo path).
streamlit>=1.40.0
pillow>=10.0.0
numpy>=2.0.0
seaborn>=0.13.0
matplotlib>=3.8.0
"""

REPO_ROOT_REPLACEMENT = '''def repo_root() -> Path:
    """Lesson / extract repository root (Cloud-safe; does not invoke git)."""
    import os

    override = os.environ.get("SAMPLES_ROOT") or os.environ.get("LESSON_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    here = Path(__file__).resolve().parent
    # Prefer directory that already contains samples/ or app.py.
    for candidate in (here, *here.parents):
        if (candidate / "samples").is_dir() or (candidate / "app.py").is_file():
            return candidate
    return here
'''

EXCLUDE_DIR_NAMES = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "features",
    "request_features",
}


def upstream_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)

    def ignore(directory: str, names: list[str]) -> set[str]:
        skipped: set[str] = set()
        for name in names:
            if name in EXCLUDE_DIR_NAMES:
                skipped.add(name)
            elif name.endswith(".pyc"):
                skipped.add(name)
        return skipped

    shutil.copytree(src, dst, ignore=ignore)


def vendor_samples(out: Path) -> dict:
    mono_samples = ROOT / "samples"
    dest = out / "samples"
    dest.mkdir(parents=True, exist_ok=True)
    plan = {
        "beaches": 100,  # [:50] ref + [50:100] control
        "forests": 50,
        "balls": 50,
    }
    copied: dict[str, int] = {}
    for theme, n in plan.items():
        src_dir = mono_samples / theme
        if not src_dir.is_dir():
            copied[theme] = 0
            continue
        files = sorted(src_dir.glob("*.jpg")) + sorted(src_dir.glob("*.jpeg"))
        take = files[:n]
        theme_dest = dest / theme
        theme_dest.mkdir(parents=True, exist_ok=True)
        for path in take:
            shutil.copy2(path, theme_dest / path.name)
        copied[theme] = len(take)
    return copied


def patch_repo_root_functions(out: Path) -> list[str]:
    """Replace any ``def repo_root(): ... git rev-parse ...`` block."""
    touched: list[str] = []
    pattern = re.compile(
        r"def repo_root\(\) -> Path:\n"
        r"(?:.*\n)*?"
        r"(?:[ \t]+return Path\(\s*\n"
        r"[ \t]+subprocess\.check_output\(\s*\n"
        r"[ \t]+\[\"git\", \"rev-parse\", \"--show-toplevel\"\],\s*\n"
        r"(?:.*\n)+?"
        r"[ \t]+\)\s*\n"
        r"[ \t]+\)|"
        r"[ \t]+return Path\(\s*\n"
        r"[ \t]+subprocess\.check_output\(\[\"git\", \"rev-parse\", \"--show-toplevel\"\].*?\n"
        r"[ \t]+\))",
        re.MULTILINE,
    )
    # Simpler line-based rewrite for known style in this repo.
    simple = re.compile(
        r"def repo_root\(\) -> Path:\n"
        r"    return Path\(\n"
        r"        subprocess\.check_output\(\n"
        r"            \[\"git\", \"rev-parse\", \"--show-toplevel\"\],\n"
        r"            text=True,\n"
        r"        \)\.strip\(\)\n"
        r"    \)\n",
        re.MULTILINE,
    )
    for path in out.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "rev-parse" not in text or "def repo_root" not in text:
            continue
        new, n = simple.subn(REPO_ROOT_REPLACEMENT + "\n", text)
        if n == 0:
            # Fallback: replace function body heuristically
            new, n = pattern.subn(REPO_ROOT_REPLACEMENT + "\n", text)
        if n:
            # Drop unused subprocess import if no longer referenced.
            if "subprocess." not in new and "import subprocess" in new:
                new = re.sub(r"^import subprocess\n", "", new, count=1, flags=re.M)
            path.write_text(new, encoding="utf-8")
            touched.append(str(path.relative_to(out)))
    return touched


def assert_no_rev_parse_runtime(out: Path) -> None:
    """Fail if app runtime modules still call git rev-parse."""
    runtime = [
        out / "app.py",
        out / "sample_sets.py",
        out / "corpus_stats.py",
        out / "request_stats.py",
        out / "plotting.py",
        out / "ks_compare.py",
        out / "psi.py",
        out / "alert_rule.py",
        out / "alert_psi.py",
        out / "anomaly.py",
        out / "histogram.py",
    ]
    # Match real invocations, not prose mentioning the phrase.
    call_pat = re.compile(r"""\[["']git["']\s*,\s*["']rev-parse["']""")
    bad: list[str] = []
    for path in runtime:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if call_pat.search(text):
            bad.append(path.name)
    if bad:
        raise SystemExit(f"runtime still uses git rev-parse: {bad}")


def allow_vendored_samples_in_gitignore(out: Path) -> None:
    """Lesson trees ignore samples/; Cloud extracts must track the vendored freeze."""
    gitignore = out / ".gitignore"
    if not gitignore.is_file():
        gitignore.write_text(
            ".venv/\n__pycache__/\n*.pyc\n.pytest_cache/\n"
            "request_features/*.json\n!request_features/.gitkeep\n",
            encoding="utf-8",
        )
        return
    lines = gitignore.read_text(encoding="utf-8").splitlines(keepends=True)
    rewritten: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped in {"samples/", "/samples/", "samples"}:
            rewritten.append(
                "# Cloud extract: samples/ is vendored and tracked (was ignored in monorepo lesson)\n"
            )
            continue
        rewritten.append(line)
    gitignore.write_text("".join(rewritten), encoding="utf-8")


def write_cloud_meta(out: Path, lesson: str, samples: dict[str, int], patched: list[str]) -> None:
    (out / "requirements.txt").write_text(CLOUD_REQUIREMENTS, encoding="utf-8")
    streamlit_dir = out / ".streamlit"
    streamlit_dir.mkdir(exist_ok=True)
    (streamlit_dir / "config.toml").write_text(
        '[server]\nheadless = true\n',
        encoding="utf-8",
    )
    allow_vendored_samples_in_gitignore(out)
    sha = upstream_sha()
    sync = {
        "upstream_repo": "bentoML-processamento-imagens",
        "upstream_sha": sha,
        "lesson": lesson,
        "samples_copied": samples,
        "patched_repo_root": patched,
        "main_file": "app.py",
        "host": "https://share.streamlit.io",
    }
    (out / "SYNC.json").write_text(json.dumps(sync, indent=2) + "\n", encoding="utf-8")
    (out / "STREAMLIT_CLOUD.md").write_text(
        f"""# Streamlit Community Cloud

Upstream: `bentoML-processamento-imagens@{sha}` (lesson {lesson}).

## Deploy

1. Push this repository to GitHub (public).
2. Open https://share.streamlit.io → **New app**.
3. Main file path: `app.py`
4. Python: 3.13 (or closest supported; see `requires-python` in upstream).

## Refresh from monorepo

```bash
cd /path/to/bentoML-processamento-imagens
python scripts/export_streamlit_cloud.py {lesson} --out {out}
cd {out}
git add -A && git commit -m "sync from monorepo" && git push
```

Runtime does **not** call `git rev-parse`. Samples are vendored under `samples/`.
BentoML is omitted from `requirements.txt` (offline Streamlit path only).
""",
        encoding="utf-8",
    )


def maybe_git_init(out: Path) -> None:
    if (out / ".git").is_dir():
        return
    subprocess.run(["git", "init"], cwd=out, check=True)
    subprocess.run(["git", "add", "-A"], cwd=out, check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initial Streamlit Cloud extract"],
        cwd=out,
        check=False,
    )


def export_lesson(lesson: str, out: Path, *, git_init: bool) -> None:
    meta = LESSONS[lesson]
    src: Path = meta["src"]
    if not src.is_dir():
        raise SystemExit(f"missing lesson tree: {src}")
    print(f"export {lesson}: {src} → {out}")
    copy_tree(src, out)
    samples = vendor_samples(out)
    patched = patch_repo_root_functions(out)
    write_cloud_meta(out, lesson, samples, patched)
    assert_no_rev_parse_runtime(out)
    if git_init:
        maybe_git_init(out)
    print(json.dumps({"out": str(out), "samples": samples, "patched": patched}, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", choices=sorted(LESSONS))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--git-init",
        action="store_true",
        help="git init + initial commit in the extract directory",
    )
    args = parser.parse_args(argv)
    out = args.out or LESSONS[args.lesson]["default_out"]
    out = out.expanduser().resolve()
    export_lesson(args.lesson, out, git_init=args.git_init)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
