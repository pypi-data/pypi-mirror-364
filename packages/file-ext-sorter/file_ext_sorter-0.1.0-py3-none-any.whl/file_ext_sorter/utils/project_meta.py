"""
Utility to extract project metadata using importlib.metadata.

This version avoids runtime dependency on pyproject.toml by using
the installed distribution metadata.
"""

from importlib.metadata import metadata, PackageNotFoundError
from typing import TypedDict


class ProjectMetadata(TypedDict):
    """
    Typed dictionary representing project metadata retrieved from installed package.

    Fields:
        version (str): The installed version of the package.
        author (str): The author's name.
        email (str): The author's email address.
        description (str): A short summary of the project.
        homepage (str): The project's homepage URL.
    """

    version: str
    author: str
    email: str
    description: str
    homepage: str


def get_project_metadata(distribution_name: str = "file-ext-sorter") -> dict:
    """
    Return relevant metadata for the installed distribution.

    Args:
        distribution_name (str): The package name as declared in pyproject.toml.

    Returns:
        dict: Contains version, author, email, description, homepage, issues.

    Raises:
        RuntimeError: If the metadata cannot be found (e.g., not installed).
    """
    try:
        dist_meta = metadata(distribution_name)

        # Extract URLs from "Project-URL" metadata entries
        project_urls = {}
        for item in dist_meta.get_all("Project-URL", []):
            try:
                key, value = item.split(",", 1)
                project_urls[key.strip()] = value.strip()
            except ValueError:
                continue  # Safely skip malformed entries

        return {
            "version": dist_meta.get("Version", "unknown"),
            "author": dist_meta.get("Author", "unknown"),
            "email": dist_meta.get("Author-email", ""),
            "description": dist_meta.get("Summary", ""),
            "homepage": project_urls.get("Homepage", ""),
            "issues": project_urls.get("Issues", ""),
        }
    except PackageNotFoundError as exc:
        raise RuntimeError(
            f"Cannot read installed metadata for package '{distribution_name}'."
        ) from exc
