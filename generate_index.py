#!/usr/bin/env python3
"""Generate index.html by scanning content folders (images, etc.)."""

import html
from pathlib import Path

# Folders to scan for files (relative to the repo root)
CONTENT_FOLDERS = ["images"]

# File extensions to include per folder (empty set = include all)
EXTENSIONS: dict[str, set[str]] = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp"},
}

# Files/folders to ignore
IGNORED = {".gitkeep", ".DS_Store"}


def collect_files(root: Path) -> dict[str, list[Path]]:
    """Return a mapping of folder -> sorted list of files."""
    result: dict[str, list[Path]] = {}
    for folder_name in CONTENT_FOLDERS:
        folder = root / folder_name
        if not folder.is_dir():
            continue
        allowed_ext = EXTENSIONS.get(folder_name, set())
        files: list[Path] = []
        for entry in sorted(folder.rglob("*")):
            if not entry.is_file():
                continue
            if entry.name in IGNORED:
                continue
            if allowed_ext and entry.suffix.lower() not in allowed_ext:
                continue
            files.append(entry.relative_to(root))
        result[folder_name] = files
    return result


def render_folder_section(folder_name: str, files: list[Path]) -> str:
    """Render the HTML section for one folder."""
    esc_folder = html.escape(folder_name)
    lines = [
        f'  <section id="{esc_folder}">',
        f'    <h2>{esc_folder}</h2>',
    ]
    if not files:
        lines.append("    <p class=\"empty\">No files yet.</p>")
    else:
        lines.append("    <ul>")
        for f in files:
            href = html.escape(f.as_posix())
            name = html.escape(f.name)
            lines.append(f'      <li><a href="{href}">{name}</a></li>')
        lines.append("    </ul>")
    lines.append("  </section>")
    return "\n".join(lines)


def render_nav(folder_names: list[str]) -> str:
    lines = ["  <nav>", "    <ul>"]
    for name in folder_names:
        esc = html.escape(name)
        lines.append(f'      <li><a href="#{esc}">{esc}</a></li>')
    lines += ["    </ul>", "  </nav>"]
    return "\n".join(lines)


def build_html(sections: dict[str, list[Path]]) -> str:
    folder_names = list(sections.keys())
    nav_html = render_nav(folder_names) if folder_names else ""
    sections_html = "\n".join(
        render_folder_section(name, files) for name, files in sections.items()
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Shared Assets</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: system-ui, sans-serif;
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1rem;
      color: #222;
      background: #fafafa;
    }}
    h1 {{ border-bottom: 2px solid #ddd; padding-bottom: .4rem; }}
    nav ul {{ display: flex; gap: 1rem; list-style: none; padding: 0; }}
    nav a {{ text-decoration: none; color: #0066cc; }}
    nav a:hover {{ text-decoration: underline; }}
    section {{ margin-top: 2rem; }}
    h2 {{ text-transform: capitalize; color: #444; }}
    ul {{ list-style: disc; padding-left: 1.5rem; }}
    li {{ margin: .3rem 0; }}
    a {{ color: #0066cc; word-break: break-all; }}
    a:hover {{ text-decoration: underline; }}
    .empty {{ color: #888; font-style: italic; }}
    footer {{ margin-top: 3rem; font-size: .8rem; color: #999; border-top: 1px solid #ddd; padding-top: .5rem; }}
  </style>
</head>
<body>
  <h1>Shared Assets</h1>
{nav_html}
{sections_html}
  <footer>Auto-generated index &mdash; do not edit by hand.</footer>
</body>
</html>
"""


def main() -> None:
    root = Path(__file__).parent
    sections = collect_files(root)
    html_content = build_html(sections)
    index_path = root / "index.html"
    index_path.write_text(html_content, encoding="utf-8")
    total = sum(len(v) for v in sections.values())
    print(f"index.html written ({total} file(s) indexed).")


if __name__ == "__main__":
    main()
