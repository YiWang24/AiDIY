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
        input_dir: Input directory with MDX files (relative to kb/ or absolute)
        output_path: Output JSONL file path
        noise_filter: Enable noise filtering (remove "Next:", "Previous:" etc)

    Returns:
        Statistics dict
    """
    # Find the JS cleaner script
    js_cleaner = (
        Path(__file__).parent.parent / "tools" / "mdx-clean" / "bin" / "clean.mjs"
    )

    if not js_cleaner.exists():
        raise RuntimeError(
            f"JS cleaner not found at {js_cleaner}. "
            "Please ensure the mdx-clean tool is installed."
        )

    # Get project root (kb parent directory)
    # IMPORTANT: Don't resolve project_root to avoid following symlinks
    project_root = Path(__file__).parent.parent.parent

    # Resolve and normalize input directory
    # The goal is to get a path relative to project root for the JS tool
    input_path_abs = Path(input_dir).resolve()

    # Special handling: if input_path is outside project_root but seems to be "docs"
    # This can happen when paths resolve differently due to symlinks or path components
    # Try to match common patterns
    if str(input_path_abs).endswith("/docs") or str(input_path_abs).endswith("/docs/"):
        # Check if there's a docs/ directory in project_root
        docs_in_project = (project_root / "docs").resolve()
        if input_path_abs == docs_in_project or str(input_path_abs) == str(docs_in_project):
            input_dir_rel = "docs"
        else:
            # Use "docs" as fallback if the path ends with "docs"
            input_dir_rel = "docs"
    else:
        # Try to get relative path from project root
        try:
            input_dir_rel = str(input_path_abs.relative_to(project_root.resolve()))
        except ValueError:
            # Not under project root, use absolute path
            input_dir_rel = str(input_path_abs)

    # For output, also use relative path from project root
    output_path_abs = Path(output_path).resolve()
    try:
        output_path_rel = str(output_path_abs.relative_to(project_root))
    except ValueError:
        output_path_rel = str(output_path_abs)

    # Prepare command - use node and script path separately
    cmd = [
        "node",
        str(js_cleaner.relative_to(project_root)),  # Relative path for node
        "--roots",
        input_dir_rel,
        "--output",
        output_path_rel,
    ]

    if noise_filter:
        cmd.append("--noise-filter")

    print(f"Running: node {' '.join(cmd)}")
    print(f"Working dir: {project_root}")

    # Run JS cleaner from project root
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(project_root),
    )

    if result.returncode != 0:
        raise RuntimeError(f"JS cleaner failed:\n{result.stderr}\n{result.stdout}")

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
                        stats["errors"].append(
                            {
                                "doc_id": record.get("id"),
                                "error": record["frontmatter"]["parseError"],
                            }
                        )
    except FileNotFoundError:
        pass

    return stats
