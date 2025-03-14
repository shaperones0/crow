"""A module for managing and organizing HTML (or other note format) files within a project directory.

This module provides the `Project` class, which is responsible for discovering,
organizing, and managing source files in a specified root directory. It uses glob
patterns to locate files, creates `Page` objects to represent each file,
and maintains the project's file structure for easy access and comparison.

The module is designed to handle file structure changes efficiently by using
hashing and iterators, making it suitable for projects with dynamic content.
"""

from collections.abc import Sequence
from pathlib import Path

from natsort import os_sorted

from .model import Page


class Project:
    """A class representing a project that manages a collection of pages.

    The Project class is responsible for discovering, organizing, and managing
    source files within a specified directory. It provides methods to build and
    maintain a list of `Page` objects, and offers properties to access the
    project's structure and pages.
    """

    def __init__(self, root_path: Path, glob: str = "**/*.html") -> None:
        """Initializes the Project with the given root directory and configuration.

        Args:
            root_path (Path): The root directory containing the project's source files.
            glob (str, optional): The glob pattern to find source files. Defaults to "**/*.html".
        """
        self._root_path = root_path
        self._glob = glob

        # Build pages on init
        self._pages: list[Page] = []
        self._structure_stored: list[Path] = []
        self._structure_hash_stored = 0

    def build(self) -> list[Path]:
        """(Re)Builds the project by discovering and organizing source files.

        This method clears the existing list of pages, retrieves the current file structure,
        and creates `Page` objects for each discovered source file. It also updates the stored
        file structure iterator and its hash.

        Returns:
            list[Path]: List of Path objects representing the project's file structure.
        """
        self._pages.clear()
        self._structure_stored = self.structure_get_actual()
        self._structure_hash_stored = hash(tuple(self._structure_stored))
        for source_path in os_sorted(self._structure_stored):
            self._pages.append(Page.from_source_path(source_path, self._root_path))
        return self._structure_stored

    def structure_get_actual(self) -> list[Path]:
        """Retrieves the current source structure of the project.

        This method uses the `rglob` pattern to find all source files within the root directory.

        Returns:
            list[Path]: List of Path objects representing the current file structure.
        """
        return list(self._root_path.glob(self._glob))

    def structure_hash_get_actual(self) -> int:
        """Calculates the hash of the current file structure.

        This method is useful for detecting changes in the project's file structure.

        Returns:
            int: A hash value representing the current file structure.
        """
        return hash(tuple(self.structure_get_actual()))

    @property
    def pages_stored(self) -> Sequence[Page]:
        """Returns the list of `Page` objects in the project stored since last rebuild.

        Returns:
            Sequence[Page]: A sequence of `Page` objects representing the project's HTML files.
        """
        return self._pages

    @property
    def structure_stored(self) -> list[Path]:
        """Returns iterator of the project's file structure stored since last rebuild.

        Returns:
            list[Path]: List of Path objects representing the stored file structure.
        """
        return self._structure_stored

    @property
    def structure_hash_stored(self) -> int:
        """Returns hash of the project's file structure stored since last rebuild.

        Returns:
            int: A hash value representing the stored file structure.
        """
        return self._structure_hash_stored

    @property
    def root_path(self) -> Path:
        """Returns the root directory of the project.
        Returns:
            Path: The root directory of the project.
        """
        return self._root_path
