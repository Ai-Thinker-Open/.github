#!/usr/bin/env python3
"""Update the hard-coded Star count in the recommended-repo SVG cards.

Uses the GitHub CLI (`gh api`) to fetch the current stargazers_count for each
repository, then rewrites the Star pill number inside every matching SVG card.
Run this in CI (see .github/workflows/update-repo-cards.yml) or locally when
the GitHub CLI is authenticated.
"""
import glob
import re
import subprocess

REPOS = [
    ("skills", "Ai-Thinker-Open/skills"),
    ("aiwb2", "Ai-Thinker-Open/Ai-Thinker-WB2"),
    ("middleware", "Ai-Thinker-Open/aithinker_dev_open_sdk"),
    ("sigmesh", "Ai-Thinker-Open/Telink_SIG_Mesh"),
]

# Match the Star pill label text: fill="#ffffff">NN</text>
PILL_RE = re.compile(r'(fill="#ffffff">)\d+(</text>)')


def fetch_stars(repo: str) -> str:
    out = subprocess.check_output(
        ["gh", "api", f"repos/{repo}", "--jq", ".stargazers_count"],
        text=True,
    ).strip()
    return out


def main() -> int:
    changed = 0
    for key, repo in REPOS:
        try:
            stars = fetch_stars(repo)
        except Exception as exc:  # noqa: BLE001 - keep going on failures
            print(f"skip {repo}: {exc}")
            continue
        print(f"{repo}: {stars}")
        for path in glob.glob(f"profile/repo-{key}-*.svg"):
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            new_content, n = PILL_RE.subn(lambda m: f"{m.group(1)}{stars}{m.group(2)}", content)
            if n and new_content != content:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new_content)
                changed += 1
                print(f"  updated {path}")
    print(f"updated {changed} card(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
