"""
A module for managing common data models (currently Page and Table of Contents (TOC) Entry).

This module defines Pydantic models for representing pages and TOC entries, along with utility
functions for creating Page instances from file paths and generating TOC structures from ordered
pages. It is designed to handle hierarchical document structures, such as those found in
documentation or book projects.

Classes:
    - TOCEntry: Represents a single entry in a table of contents.
    - Page: Represents a document page with metadata, including its title, source path, TOC path,
      and modification timestamp.

Functions:
    - toc_from_ordered_pages: Generates a list of TOCEntry objects from an ordered list of Page
      instances.
"""

from pathlib import Path

from pydantic import BaseModel, Field


class Page(BaseModel):
    """Represents a document page with metadata.

    Attributes:
        title: The title of the page. Immutable once set.
        source_path: The filesystem path to the page's source file. Immutable once set.
        toc_path: The hierarchical path used for organizing the page in the table of contents.
                  Immutable once set.
        modified: The timestamp of the last modification to the page. Defaults to 0.0.

    Methods:
        from_source_path: Constructs a Page instance from a source file path and project directory.
    """

    title: str = Field(frozen=True)
    source_path: Path = Field(frozen=True)
    toc_path: str = Field(frozen=True)
    modified: float = 0.0

    @classmethod
    def from_source_path(cls, source_path: Path, project_dir: Path) -> "Page":
        """Constructs a Page instance from a source file path and project directory.

        Determines the page's title and TOC path based on its relative location within the project
        directory. Handles special cases for "index" pages, which may represent top-level or nested
        sections.

        Args:
            source_path: The absolute path to the page's source file.
            project_dir: The root directory of the project.

        Returns:
            A Page instance with the calculated title, TOC path, and default metadata.
        """
        rel_source_path_parts = source_path.relative_to(project_dir).parts
        if source_path.stem == "index":
            # Check if this index is the top level index or not
            if len(rel_source_path_parts) > 1:
                # Folder name will be the title of this page (or none, if it's top level index)
                title = rel_source_path_parts[-2]
                # All up to page's folder will be part TOC path
                toc_path = "/".join(rel_source_path_parts[:-1])
            else:
                # For top level index no title or TOC path available
                title = ""
                toc_path = ""
        else:
            # Title is just filename without extension - available for any page
            title = source_path.stem
            if len(rel_source_path_parts) >= 2:
                # TOC path is combined path to file and title
                toc_path = "/".join(
                    rel_source_path_parts[i] if i != len(rel_source_path_parts) - 1 else title
                    for i in range(len(rel_source_path_parts))
                )
            else:
                # TOC path unavailable
                toc_path = ""

        return cls(
            title=title,
            source_path=source_path,
            toc_path=toc_path,
            modified=0.0,  # this value is set when we render the page
        )
