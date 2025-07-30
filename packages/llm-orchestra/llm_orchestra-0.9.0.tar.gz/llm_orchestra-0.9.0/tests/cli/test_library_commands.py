"""Tests for library CLI commands."""

from unittest.mock import mock_open, patch

from click.testing import CliRunner

from llm_orc.cli import cli


class TestLibraryBrowseCommand:
    """Test library browse command functionality."""

    def test_library_browse_lists_all_categories(self) -> None:
        """Should list all available ensemble categories."""
        runner = CliRunner()

        with patch(
            "llm_orc.cli_library.library.get_library_categories"
        ) as mock_get_categories:
            mock_get_categories.return_value = [
                "code-analysis",
                "idea-exploration",
                "research-analysis",
                "decision-support",
                "problem-decomposition",
                "learning-facilitation",
            ]

            result = runner.invoke(cli, ["library", "browse"])

            assert result.exit_code == 0
            assert "code-analysis" in result.output
            assert "idea-exploration" in result.output
            assert "research-analysis" in result.output

    def test_library_browse_specific_category(self) -> None:
        """Should list ensembles in a specific category."""
        runner = CliRunner()

        with patch(
            "llm_orc.cli_library.library.get_category_ensembles"
        ) as mock_get_ensembles:
            mock_get_ensembles.return_value = [
                {
                    "name": "security-review",
                    "description": "Multi-perspective security analysis ensemble",
                    "path": "code-analysis/security-review.yaml",
                }
            ]

            result = runner.invoke(cli, ["library", "browse", "code-analysis"])

            assert result.exit_code == 0
            assert "security-review" in result.output
            assert "Multi-perspective security analysis" in result.output

    def test_library_browse_invalid_category(self) -> None:
        """Should show error for invalid category."""
        runner = CliRunner()

        with patch(
            "llm_orc.cli_library.library.get_category_ensembles"
        ) as mock_get_ensembles:
            mock_get_ensembles.return_value = []

            result = runner.invoke(cli, ["library", "browse", "invalid-category"])

            assert result.exit_code == 0
            assert (
                "No ensembles found" in result.output
                or "invalid-category" in result.output
            )


class TestLibraryCopyCommand:
    """Test library copy command functionality."""

    def test_library_copy_to_local_config(self) -> None:
        """Should copy ensemble to local .llm-orc/ensembles/ directory."""
        runner = CliRunner()

        ensemble_content = """
name: test-ensemble
description: Test ensemble
agents:
  - name: test-agent
    model_profile: micro-local
"""

        with (
            patch("llm_orc.cli_library.library.fetch_ensemble_content") as mock_fetch,
            patch(
                "llm_orc.cli_library.library.ensure_local_ensembles_dir"
            ) as mock_ensure_dir,
            patch("builtins.open", mock_open()),
        ):
            mock_fetch.return_value = ensemble_content
            mock_ensure_dir.return_value = ".llm-orc/ensembles"

            result = runner.invoke(
                cli, ["library", "copy", "code-analysis/security-review"]
            )

            assert result.exit_code == 0
            assert "Copied" in result.output
            assert "test-ensemble" in result.output
            mock_fetch.assert_called_once_with("code-analysis/security-review")

    def test_library_copy_to_global_config(self) -> None:
        """Should copy ensemble to global config when --global flag used."""
        runner = CliRunner()

        ensemble_content = """
name: test-ensemble
description: Test ensemble
agents:
  - name: test-agent
    model_profile: default
"""

        with (
            patch("llm_orc.cli_library.library.fetch_ensemble_content") as mock_fetch,
            patch(
                "llm_orc.cli_library.library.ensure_global_ensembles_dir"
            ) as mock_ensure_dir,
            patch("builtins.open", mock_open()),
        ):
            mock_fetch.return_value = ensemble_content
            mock_ensure_dir.return_value = "/home/user/.config/llm-orc/ensembles"

            result = runner.invoke(
                cli, ["library", "copy", "idea-exploration/concept-mapper", "--global"]
            )

            assert result.exit_code == 0
            assert "Copied" in result.output
            assert "test-ensemble" in result.output
            mock_fetch.assert_called_once_with("idea-exploration/concept-mapper")

    def test_library_copy_invalid_ensemble(self) -> None:
        """Should show error for invalid ensemble path."""
        runner = CliRunner()

        with patch("llm_orc.cli_library.library.fetch_ensemble_content") as mock_fetch:
            mock_fetch.side_effect = FileNotFoundError("Ensemble not found")

            result = runner.invoke(cli, ["library", "copy", "invalid/ensemble"])

            assert result.exit_code == 1
            assert "not found" in result.output.lower()

    def test_library_copy_overwrites_existing_with_confirmation(self) -> None:
        """Should prompt for confirmation when overwriting existing ensemble."""
        runner = CliRunner()

        ensemble_content = "name: existing-ensemble"

        with (
            patch("llm_orc.cli_library.library.fetch_ensemble_content") as mock_fetch,
            patch("llm_orc.cli_library.library.ensemble_exists") as mock_exists,
            patch(
                "llm_orc.cli_library.library.ensure_local_ensembles_dir"
            ) as mock_ensure_dir,
            patch("builtins.open", mock_open()),
        ):
            mock_fetch.return_value = ensemble_content
            mock_exists.return_value = True
            mock_ensure_dir.return_value = ".llm-orc/ensembles"

            # Test with 'y' input for confirmation
            result = runner.invoke(
                cli, ["library", "copy", "test/ensemble"], input="y\n"
            )

            assert result.exit_code == 0
            assert "already exists" in result.output
            assert "Copied" in result.output


class TestLibraryCategoriesCommand:
    """Test library categories command functionality."""

    def test_library_categories_lists_all(self) -> None:
        """Should list all available categories with descriptions."""
        runner = CliRunner()

        with patch(
            "llm_orc.cli_library.library.get_library_categories_with_descriptions"
        ) as mock_get_categories:
            mock_get_categories.return_value = [
                ("code-analysis", "Code review and security analysis"),
                ("idea-exploration", "Concept mapping and perspective taking"),
                ("research-analysis", "Literature review and synthesis"),
            ]

            result = runner.invoke(cli, ["library", "categories"])

            assert result.exit_code == 0
            assert "code-analysis" in result.output
            assert "Code review and security analysis" in result.output
            assert "idea-exploration" in result.output


class TestLibraryIntegration:
    """Integration tests for library commands."""

    def test_browse_then_copy_workflow(self) -> None:
        """Should support browsing then copying an ensemble."""
        runner = CliRunner()

        # First browse to see available ensembles
        with patch(
            "llm_orc.cli_library.library.get_category_ensembles"
        ) as mock_get_ensembles:
            mock_get_ensembles.return_value = [
                {
                    "name": "security-review",
                    "description": "Security analysis",
                    "path": "code-analysis/security-review.yaml",
                }
            ]

            browse_result = runner.invoke(cli, ["library", "browse", "code-analysis"])
            assert browse_result.exit_code == 0
            assert "security-review" in browse_result.output

        # Then copy the ensemble
        ensemble_content = "name: security-review\ndescription: Security analysis"

        with (
            patch("llm_orc.cli_library.library.fetch_ensemble_content") as mock_fetch,
            patch(
                "llm_orc.cli_library.library.ensure_local_ensembles_dir"
            ) as mock_ensure_dir,
            patch("builtins.open", mock_open()),
        ):
            mock_fetch.return_value = ensemble_content
            mock_ensure_dir.return_value = ".llm-orc/ensembles"

            copy_result = runner.invoke(
                cli, ["library", "copy", "code-analysis/security-review"]
            )
            assert copy_result.exit_code == 0
            assert "Copied" in copy_result.output
