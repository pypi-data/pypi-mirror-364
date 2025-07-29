"""
Command to check and validate image references in HTML files.
"""

from pathlib import Path
from typing import List, Optional, Tuple, cast

import click
from bs4 import BeautifulSoup, Tag


def is_local_image(src: str) -> bool:
    """
    Filter out external URLs (http://, //).

    Args:
        src: Image source URL

    Returns:
        True if the image is local, False otherwise
    """
    if not src:
        return False

    # Skip external URLs
    if src.startswith(("http://", "https://", "//")):
        return False

    return True


def normalize_src(src: str) -> str:
    """
    Remove query strings and prefixes ./ or /.

    Args:
        src: Image source URL

    Returns:
        Normalized source path
    """
    if not src:
        return ""

    # Remove query strings
    src = src.split("?")[0]

    # Remove leading ./ or /
    src = src.lstrip("./").lstrip("/")

    return src


def find_real_path(base_dir: Path, ref: str) -> Optional[Path]:
    """
    Segment the path, list parent directory, find real case of each segment,
    and return the real path or None if not found.

    Args:
        base_dir: Base directory to search from
        ref: Reference path to find

    Returns:
        Real path with correct case or None if not found
    """
    if not ref:
        return None

    # Split path into segments
    segments = ref.split("/")
    current_path = base_dir

    for segment in segments:
        if not segment:  # Skip empty segments
            continue

        # List parent directory to find real case
        try:
            parent_contents = list(current_path.iterdir())
        except (OSError, PermissionError):
            return None

        # Find matching segment (case-insensitive)
        found_segment = None
        for item in parent_contents:
            if item.name.lower() == segment.lower():
                found_segment = item.name
                break

        if found_segment is None:
            return None

        current_path = current_path / found_segment

    return current_path if current_path.exists() else None


def validate_image_paths(
    html_file: Path, fix: bool = False
) -> Tuple[List[str], List[str], List[str]]:
    """
    Validate image paths in HTML file.

    Args:
        html_file: Path to HTML file
        fix: Whether to apply fixes automatically

    Returns:
        Tuple of (errors, warnings, fixes_applied)
    """
    errors: list[str] = []
    warnings: list[str] = []
    fixes_applied: list[str] = []

    try:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        errors.append(f"Cannot read HTML file: {e}")
        return errors, warnings, fixes_applied

    soup = BeautifulSoup(content, "html.parser")
    img_tags = soup.find_all("img")

    base_dir = html_file.parent

    for img in img_tags:
        # Cast to Tag to ensure we have the right type
        img_tag = cast(Tag, img)
        src_attr = img_tag.get("src")
        src = str(src_attr) if src_attr is not None else ""

        if not is_local_image(src):
            continue

        normalized_src = normalize_src(src)
        if not normalized_src:
            continue

        # Check if image is in images/ or img/ directory
        if not (
            normalized_src.startswith("images/") or normalized_src.startswith("img/")
        ):
            warnings.append(f"Image '{src}' is not in images/ or img/ directory")
            continue

        # Find real path with correct case
        real_path = find_real_path(base_dir, normalized_src)

        if real_path is None:
            errors.append(f"Image not found: '{src}'")
            continue

        # Check if path case matches
        expected_path = base_dir / normalized_src
        if str(real_path) != str(expected_path):
            if fix:
                # Apply fix
                img_tag["src"] = str(real_path.relative_to(base_dir))
                fixes_applied.append(
                    f"Fixed: '{src}' → '{real_path.relative_to(base_dir)}'"
                )
            else:
                # Only add error if not fixing
                error_msg = (
                    f"Case mismatch: '{src}' should be "
                    f"'{real_path.relative_to(base_dir)}'"
                )
                errors.append(error_msg)

    if fix and fixes_applied:
        # Create backup
        backup_file = html_file.with_suffix(".html.bak")
        try:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(str(soup))

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(content)

        except OSError as e:
            errors.append(f"Cannot write fixed file: {e}")

    return errors, warnings, fixes_applied


@click.command("check-images")
@click.argument("root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--fix", is_flag=True, help="Apply fixes automatically and create backup")
def check_images(root: Path, fix: bool) -> None:
    """
    Check and validate image references in HTML files.

    Scans index.html in the specified directory, detects local <img> tags,
    validates that images exist in images/ or img/ directories with correct case,
    and optionally applies fixes.

    Args:
        root: Directory containing index.html
        fix: Apply fixes automatically and create backup
    """
    html_file = root / "index.html"

    if not html_file.exists():
        click.secho(f"Error: index.html not found in {root}", fg="red")
        raise click.Abort()

    click.echo(f"Checking images in {html_file}...")

    errors, warnings, fixes_applied = validate_image_paths(html_file, fix)

    # Display results
    if errors:
        click.secho(f"\n❌ Found {len(errors)} errors:", fg="red")
        for error in errors:
            click.secho(f"  • {error}", fg="red")

    if warnings:
        click.secho(f"\n⚠️  Found {len(warnings)} warnings:", fg="yellow")
        for warning in warnings:
            click.secho(f"  • {warning}", fg="yellow")

    if fixes_applied:
        click.secho(f"\n✅ Applied {len(fixes_applied)} fixes:", fg="green")
        for fix_applied in fixes_applied:
            click.secho(f"  • {fix_applied}", fg="green")
        click.secho(f"Backup saved as {html_file.with_suffix('.html.bak')}", fg="blue")

    if not errors and not warnings:
        click.secho("✅ All images are valid!", fg="green")

    # Exit with error code if there are errors
    if errors:
        raise click.Abort()
