"""Loading of the bundled CSS/JS assets."""

import json
from pathlib import Path

# Assets ship inside the package (works from a source checkout, a pip install
# and a PyInstaller bundle alike).
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def load_css(style: str) -> str:
    """
    Load and validate a CSS stylesheet from the package's `assets/css/` directory.

    This function supports the theme system by reading external `.css`
    files such as `css/print.css`, `css/default.css`, or any future
    theme file. The selected stylesheet is returned as a raw string and
    later injected directly into the generated HTML inside a <style>
    block, keeping the final document fully self‑contained and printable.

    The function performs lightweight validation to catch common
    mistakes early (such as empty files, accidental HTML markup, or
    corrupted binary content) without attempting full CSS parsing.

    Parameters
    ----------
    style : str
        The name of the CSS theme to load (e.g., "default", "print").
        The function will automatically construct the full path:
        `<package>/assets/css/<style>.css`.

    Returns
    -------
    str
        The validated CSS content exactly as stored on disk.

    Raises
    ------
    FileNotFoundError
        If the CSS file does not exist.

    ValueError
        If the file is empty, contains HTML markup, appears corrupted,
        or does not contain any valid CSS blocks.

    OSError
        If the file cannot be read due to permissions or I/O errors.

    Notes
    -----
    • Validation is intentionally minimal: it checks for structural
      sanity but does not attempt to enforce CSS correctness.

    • This function ensures that theme files are safe to embed inline
      in the final HTML output.

    • Additional themes can be added simply by placing new `.css`
      files in the `assets/css/` directory.
    """
    css_path = ASSETS_DIR / "css" / f"{style}.css"

    # --- Read file ---
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # --- Validation rules ---

    # 1. Must not be empty or whitespace-only
    if not css.strip():
        raise ValueError(f"CSS file '{css_path}' is empty or whitespace-only.")

    # 2. Must not contain HTML tags (common mistake when editing)
    lowered = css.lower()
    forbidden_html = ("<html", "<body", "<head", "<style", "<script")
    if any(tag in lowered for tag in forbidden_html):
        raise ValueError(
            f"CSS file '{css_path}' appears to contain HTML or script markup. "
            "CSS files must contain only raw CSS rules."
        )

    # 3. Must contain at least one CSS block
    if "{" not in css or "}" not in css:
        raise ValueError(
            f"CSS file '{css_path}' does not appear to contain any CSS blocks."
        )

    # 4. Detect null bytes or binary garbage
    if "\x00" in css:
        raise ValueError(
            f"CSS file '{css_path}' contains null bytes and may be corrupted."
        )

    # 5. Warn about extremely large CSS files
    if len(css) > 500_000:  # 500 KB threshold
        raise ValueError(
            f"CSS file '{css_path}' is unexpectedly large and may be invalid."
        )

    return css


def js_json(obj) -> str:
    """Serialise `obj` as JSON that is safe to embed inside a <script> tag."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def load_js(name: str) -> str:
    """Read an inline script from the package's `assets/js/` directory."""
    return (ASSETS_DIR / "js" / f"{name}.js").read_text(encoding="utf-8")
