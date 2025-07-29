"""
Tests for the check-images command.
"""

from click.testing import CliRunner

from sall.commands.images import (
    check_images,
    find_real_path,
    is_local_image,
    normalize_src,
    validate_image_paths,
)


class TestUtilityFunctions:
    """Test utility functions for image validation."""

    def test_is_local_image(self):
        """Test is_local_image function."""
        # Local images
        assert is_local_image("images/logo.png") is True
        assert is_local_image("./images/logo.png") is True
        assert is_local_image("/images/logo.png") is True
        assert is_local_image("img/photo.jpg") is True

        # External URLs
        assert is_local_image("http://example.com/image.png") is False
        assert is_local_image("https://example.com/image.png") is False
        assert is_local_image("//cdn.example.com/image.png") is False

        # Edge cases
        assert is_local_image("") is False
        assert is_local_image(None) is False

    def test_normalize_src(self):
        """Test normalize_src function."""
        # Remove query strings
        assert normalize_src("images/logo.png?v=1.0") == "images/logo.png"
        assert normalize_src("img/photo.jpg?width=100&height=50") == "img/photo.jpg"

        # Remove prefixes
        assert normalize_src("./images/logo.png") == "images/logo.png"
        assert normalize_src("/images/logo.png") == "images/logo.png"
        assert normalize_src("///images/logo.png") == "images/logo.png"

        # Edge cases
        assert normalize_src("") == ""
        assert normalize_src(None) == ""
        assert normalize_src("images/logo.png") == "images/logo.png"

    def test_find_real_path(self, tmp_path):
        """Test find_real_path function."""
        # Create test directory structure
        images_dir = tmp_path / "Images"  # Note the capital I
        images_dir.mkdir()

        logo_file = images_dir / "Logo.png"  # Note the capital L
        logo_file.write_text("fake image")

        # Test case-insensitive matching
        result = find_real_path(tmp_path, "images/logo.png")
        assert result == logo_file

        # Test non-existent path
        result = find_real_path(tmp_path, "images/nonexistent.png")
        assert result is None

        # Test nested path
        nested_dir = images_dir / "SubDir"
        nested_dir.mkdir()
        nested_file = nested_dir / "Nested.png"
        nested_file.write_text("nested image")

        result = find_real_path(tmp_path, "images/subdir/nested.png")
        assert result == nested_file


class TestValidateImagePaths:
    """Test validate_image_paths function."""

    def test_validate_image_paths_valid_images(self, tmp_path):
        """Test validation with valid images."""
        # Create test structure
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        logo_file = images_dir / "logo.png"
        logo_file.write_text("fake image")

        # Create HTML with valid image
        html_content = """
        <html>
        <body>
            <img src="images/logo.png" alt="Logo">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        errors, warnings, fixes = validate_image_paths(html_file)

        assert len(errors) == 0
        assert len(warnings) == 0
        assert len(fixes) == 0

    def test_validate_image_paths_missing_image(self, tmp_path):
        """Test validation with missing image."""
        # Create test structure
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        # Create HTML with missing image
        html_content = """
        <html>
        <body>
            <img src="images/missing.png" alt="Missing">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        errors, warnings, fixes = validate_image_paths(html_file)

        assert len(errors) == 1
        assert "Image not found" in errors[0]
        assert len(warnings) == 0
        assert len(fixes) == 0

    def test_validate_image_paths_case_mismatch(self, tmp_path):
        """Test validation with case mismatch."""
        # Create test structure with different case
        images_dir = tmp_path / "Images"  # Capital I
        images_dir.mkdir()

        logo_file = images_dir / "Logo.png"  # Capital L
        logo_file.write_text("fake image")

        # Create HTML with lowercase reference
        html_content = """
        <html>
        <body>
            <img src="images/logo.png" alt="Logo">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        errors, warnings, fixes = validate_image_paths(html_file)

        assert len(errors) == 1
        assert "Case mismatch" in errors[0]
        assert len(warnings) == 0
        assert len(fixes) == 0

    def test_validate_image_paths_with_fix(self, tmp_path):
        """Test validation with automatic fixes."""
        # Create test structure with different case
        images_dir = tmp_path / "Images"
        images_dir.mkdir()

        logo_file = images_dir / "Logo.png"
        logo_file.write_text("fake image")

        # Create HTML with lowercase reference
        html_content = """
        <html>
        <body>
            <img src="images/logo.png" alt="Logo">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        errors, warnings, fixes = validate_image_paths(html_file, fix=True)

        assert len(errors) == 0  # Fixed
        assert len(warnings) == 0
        assert len(fixes) == 1
        assert "Fixed:" in fixes[0]

        # Check that backup was created
        backup_file = html_file.with_suffix(".html.bak")
        assert backup_file.exists()

        # Check that HTML was updated
        updated_content = html_file.read_text()
        # Handle both forward and backward slashes for cross-platform compatibility
        assert (
            'src="Images/Logo.png"' in updated_content
            or 'src="Images\\Logo.png"' in updated_content
        )

    def test_validate_image_paths_external_urls(self, tmp_path):
        """Test validation ignores external URLs."""
        html_content = """
        <html>
        <body>
            <img src="http://example.com/image.png" alt="External">
            <img src="https://cdn.example.com/logo.png" alt="CDN">
            <img src="//example.com/image.jpg" alt="Protocol-relative">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        errors, warnings, fixes = validate_image_paths(html_file)

        assert len(errors) == 0
        assert len(warnings) == 0
        assert len(fixes) == 0

    def test_validate_image_paths_wrong_directory(self, tmp_path):
        """Test validation warns about images not in images/ or img/."""
        # Create test structure
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()

        logo_file = assets_dir / "logo.png"
        logo_file.write_text("fake image")

        html_content = """
        <html>
        <body>
            <img src="assets/logo.png" alt="Logo">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        errors, warnings, fixes = validate_image_paths(html_file)

        assert len(errors) == 0
        assert len(warnings) == 1
        assert "not in images/ or img/ directory" in warnings[0]
        assert len(fixes) == 0


class TestCheckImagesCommand:
    """Test the check-images CLI command."""

    def test_check_images_command_success(self, tmp_path):
        """Test successful check-images command."""
        # Create test structure
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        logo_file = images_dir / "logo.png"
        logo_file.write_text("fake image")

        html_content = """
        <html>
        <body>
            <img src="images/logo.png" alt="Logo">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        runner = CliRunner()
        result = runner.invoke(check_images, [str(tmp_path)])

        assert result.exit_code == 0
        assert "All images are valid!" in result.output

    def test_check_images_command_errors(self, tmp_path):
        """Test check-images command with errors."""
        # Create test structure
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        html_content = """
        <html>
        <body>
            <img src="images/missing.png" alt="Missing">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        runner = CliRunner()
        result = runner.invoke(check_images, [str(tmp_path)])

        assert result.exit_code != 0
        assert "Image not found" in result.output

    def test_check_images_command_with_fix(self, tmp_path):
        """Test check-images command with --fix option."""
        # Create test structure with case mismatch
        images_dir = tmp_path / "Images"
        images_dir.mkdir()

        logo_file = images_dir / "Logo.png"
        logo_file.write_text("fake image")

        html_content = """
        <html>
        <body>
            <img src="images/logo.png" alt="Logo">
        </body>
        </html>
        """

        html_file = tmp_path / "index.html"
        html_file.write_text(html_content)

        runner = CliRunner()
        result = runner.invoke(check_images, [str(tmp_path), "--fix"])

        assert result.exit_code == 0
        assert "Applied 1 fixes" in result.output
        assert "Backup saved" in result.output

        # Check backup was created
        backup_file = html_file.with_suffix(".html.bak")
        assert backup_file.exists()

    def test_check_images_command_no_index_html(self, tmp_path):
        """Test check-images command when index.html doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(check_images, [str(tmp_path)])

        assert result.exit_code != 0
        assert "index.html not found" in result.output

    def test_check_images_command_help(self):
        """Test check-images command help."""
        runner = CliRunner()
        result = runner.invoke(check_images, ["--help"])

        assert result.exit_code == 0
        assert "Check and validate image references" in result.output
        assert "--fix" in result.output
