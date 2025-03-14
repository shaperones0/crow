"""A module defining an abstract base class for rendering HTML pages.

This module provides the `BaseRenderer` class, which serves as a blueprint for
creating renderers that convert project source files into rendered HTML pages.
The class defines two abstract methods: `build`, which is invoked when the
project structure is rebuilt, and `render`, which is responsible for converting
a source file into a rendered HTML page.

Implementations of this class should handle the specifics of rendering logic,
such as template processing, metadata injection, or custom transformations.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from .model import Page


class BaseRenderer(ABC):
    """An abstract base class for rendering HTML pages from source files.

    This class defines the interface for renderers that process project source
    files and generate rendered HTML pages. Subclasses must implement the `build`
    and `render` methods to provide specific rendering logic.

    Methods:
        build: Prepares the renderer for processing a collection of pages.
        render: Converts a source file into a rendered HTML page.
    """

    @abstractmethod
    def build(self, pages: Iterable[Page]) -> None:
        """Prepares the renderer for processing a collection of pages.

        This method is invoked when the project structure is rebuilt. It allows
        the renderer to perform any necessary setup or preprocessing for the
        provided pages.

        Args:
            pages (Iterable[Page]): A collection of `Page` objects representing the project's source
                                    files, in order of which they should be shown in table of contents
        """
        raise NotImplementedError

    @abstractmethod
    def render(self, page_source: str, page_metadata: Page) -> str:
        """Converts a source file into a rendered HTML page.

        This method takes the source content of a page and its associated metadata
        and returns the rendered HTML as a string.

        Args:
            page_source (str): The source content of the page to be rendered.
            page_metadata (Page): The metadata associated with the page.

        Returns:
            str: The rendered HTML content as a string.
        """
        raise NotImplementedError
