"""MDX document cleaning - uses existing JS tool."""

import json
import subprocess
from pathlib import Path


def clean_documents(
    input_dir: str,
    output_path: str,
    noise_filter: bool = False,
) -> dict:
    """Clean MDX documents using existing JS tool.

    Args:
        input_dir: Input directory with MDX files
        output_path: Output JSONL file path
        noise_filter: Enable noise filtering (remove "Next:", "Previous:" etc)

    Returns:
        Statistics dict
    """
    # Find the JS cleaner script
    js_cleaner = Path(__file__).parent.parent / "tools" / "mdx-clean" / "bin" / "clean.mjs"

    if not js_cleaner.exists():
        raise RuntimeError(
            f"JS cleaner not found at {js_cleaner}. "
            "Please ensure the mdx-clean tool is installed."
        )

    # Prepare command (JS tool expects comma-separated directory names, not JSON)
    cmd = [
        "node",
        str(js_cleaner),
        "--roots", input_dir,
        "--output", output_path,
    ]

    if noise_filter:
        cmd.append("--noise-filter")

    print(f"Running: {' '.join(cmd)}")

    # Run JS cleaner
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"JS cleaner failed:\n{result.stderr}\n{result.stdout}"
        )

    # Parse output to get stats
    stats = {
        "total": 0,
        "cleaned": 0,
        "errors": [],
    }

    try:
        with open(output_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    stats["cleaned"] += 1
                    stats["total"] += 1

                    # Check for parse errors in frontmatter
                    record = json.loads(line)
                    if record.get("frontmatter", {}).get("parseError"):
                        stats["errors"].append({
                            "doc_id": record.get("id"),
                            "error": record["frontmatter"]["parseError"],
                        })
    except FileNotFoundError:
        pass

    return stats
