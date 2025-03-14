import shutil
from collections.abc import Iterable
from pathlib import Path

from crow.live import LiveProject
from crow.model import Page
from crow.renderer import BaseRenderer


class TestRenderer(BaseRenderer):
    def build(self, pages: Iterable[Page]) -> None:
        pass

    def render(self, page_source: str, page_metadata: Page) -> str:
        return page_source


global_renderer = TestRenderer()
paths = [
    Path("index.html"),
    Path("chapter 1", "1.1. Welcome.html"),
    Path("chapter 1", "1.2. Semantic compositions on trolling and its meaning.html"),
    Path("chapter 1", "1.3. Welcome.html"),
    Path("chapter 1", "index.html"),
    Path("chapter 2", "bruh.html"),
    Path("chapter 2", "part 1", "paragraph 1", "minions.html"),
]


def make_project(tmp_path: Path) -> LiveProject:
    for path in paths:
        tmp_file = tmp_path / "project" / path
        tmp_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file.write_text("helo)")

    return LiveProject(
        root_path=Path(tmp_path / "project"),
        build_path=Path(tmp_path / "build"),
        renderer=global_renderer,
        db_path=str(tmp_path / "db" / "pages.sqlite"),
    )


def test_live_project_init(tmp_path: Path) -> None:
    make_project(tmp_path)


def test_get_rendered_content(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    rendered_content = project.get_rendered_content("bruh")
    assert rendered_content == "helo)"


def test_get_rendered_content_after_file_change(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    change_path = project.root_path / "chapter 2" / "bruh.html"
    change_path.write_text("bye(")

    rendered_content = project.get_rendered_content("bruh")
    assert rendered_content == "bye("


def test_get_rendered_content_after_structure_change(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    project_path = project.root_path
    shutil.rmtree(project_path)

    new_paths = [
        Path("hello", "bruh.html"),
        Path("world.html"),
    ]

    for path in new_paths:
        tmp_file = project_path / path
        tmp_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file.write_text("whatever")

    rendered_content = project.get_rendered_content("bruh")
    assert rendered_content == "whatever"
