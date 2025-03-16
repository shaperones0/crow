"""A module for live-editing and rendering a project's HTML pages.

This module provides the `LiveProject` class, which enables live-editing functionality
for a project. It allows querying rendered HTML content by page title, automatically
rebuilding the project if its structure changes, or re-rendering individual pages
if their content is modified. The class integrates with a database to track page
metadata and timestamps, ensuring efficient updates and rendering.

The module is designed to support dynamic content updates and is suitable for
use in environments where live previews of changes are required.
"""

import logging
import os
import tempfile
from pathlib import Path

from . import db
from .model import Page
from .project import Project
from .renderer import BaseRenderer


class LiveProject:
    """A class for managing live-editing and rendering of a project's source pages.

    This class provides functionality to query rendered HTML content by page title,
    automatically rebuild the project when its structure changes, and re-render
    individual pages when their content is modified. It uses a database to track
    page metadata and timestamps for efficient updates.
    """

    def __init__(
        self,
        root_path: Path,
        build_path: Path,
        renderer: BaseRenderer,
        db_path: str | None = "pages.sqlite",
        glob: str = "**/*.html",
        output_extension: str = "html",
    ):
        """Initializes the LiveProject with the given paths, renderer, and configuration.

        Args:
            root_path (Path): The root directory containing the project's source files.
            build_path (Path): The directory where rendered HTML files will be stored.
            renderer (BaseRenderer): The renderer used to convert source files into HTML.
            db_path (str, optional): Path to the SQLite database to use. Set to None to use Python's `tempfile`.
            glob (str, optional): The glob pattern to find source files. Defaults to "**/*.html".
            output_extension (str, optional): The file extension for rendered output files.
                                              Defaults to "html".
        """
        self.root_path = root_path
        self.build_path = build_path
        self.glob = glob
        self.output_extension = output_extension

        if db_path is None:
            db.init(tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite").name)
        else:
            db_path_obj = Path(db_path)
            if not db_path_obj.is_file():
                db_path_obj.parent.mkdir(parents=True, exist_ok=True)
            db.init(db_path)

        self.project = Project(root_path, glob)
        self.renderer = renderer

    def get_rendered_content(self, title: str) -> str | None:
        """Retrieves the rendered HTML content for a page by its title.

        This method checks if the project structure has changed or if the page's
        content has been modified. If so, it triggers a rebuild or re-render before
        returning the rendered HTML content.

        Args:
            title (str): The title of the page to retrieve.

        Returns:
            str | None: The rendered HTML content as a string, or `None` if the page does not exist.
        """
        if self.is_project_needs_rebuild():
            logging.info(f"Source ({self.root_path}) structure hash mismatch, rebuilding")
            self.build()

        # Now structure is validated - we can fetch the page
        # Get page metadata from db
        page = db.page_get_by_title(title)
        if page is None:
            # Looks like this page doesn't exist :/
            return None

        # Page exist - check timestamp
        page_timestamp_real = os.path.getmtime(page.source_path)
        if page_timestamp_real != page.modified:
            # Page must be rebuilt
            logging.info(f"Page ({page.title}) timestamp mismatch, rendering")
            self.render(page)
            db.page_update_modified(page)

        # Page exists, and we have relevant info about it - now we can safely display it
        output_path = self.page_output_path(page)
        return output_path.read_text(encoding="utf-8")

    def build(self) -> None:
        """Rebuilds the entire project.

        This method clears all stored page metadata from the database, rebuilds the
        project structure, updates the renderer, and re-renders all pages. It also
        updates the database with the new page metadata.
        """
        # Clear pages info from db
        db.pages_clear()

        # Rebuild project metadata
        self.project.build()

        # Update renderer
        self.renderer.build(self.project.pages_stored)
        # Render all pages
        for page in self.project.pages_stored:
            self.render(page)
        # Add project metadata to db
        db.pages_add(self.project.pages_stored)

    def render(self, page: Page) -> None:
        """Renders a single page and updates its metadata.

        This method reads the source content of the page, renders it using the
        renderer, writes the rendered content to the output file, and updates
        the page's modification timestamp.

        Args:
            page (Page): The page to render.
        """
        source_content = page.source_path.read_text(encoding="utf-8")
        page.modified = os.path.getmtime(page.source_path)
        rendered_content = self.renderer.render(source_content, page)
        output_path = self.page_output_path(page)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered_content, encoding="utf-8")

    def page_output_path(self, page: Page) -> Path:
        """Calculates the output file path for a given page.

        Args:
            page (Page): The page for which to calculate the output path.

        Returns:
            Path: The path, where rendered output file should be saved.
        """
        return self.build_path / (page.title + "." + self.output_extension)

    def is_project_needs_rebuild(self) -> bool:
        """Checks if the project structure has changed and requires a rebuild.

        Returns:
            bool: `True` if the project structure has changed, `False` otherwise.
        """
        hash_stored = self.project.structure_hash_stored
        hash_actual = self.project.structure_hash_get_actual()
        return hash_stored != hash_actual
