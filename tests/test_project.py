import shutil
from pathlib import Path

from crow.project import Project

global_project: Project | None = None
paths = [
    Path("index.html"),
    Path("chapter 1", "1.1. Welcome.html"),
    Path("chapter 1", "1.2. Semantic compositions on trolling and its meaning.html"),
    Path("chapter 1", "1.3. Welcome.html"),
    Path("chapter 1", "index.html"),
    Path("chapter 2", "bruh.html"),
    Path("chapter 2", "part 1", "paragraph 1", "minions.html"),
]


def test_project_init(tmp_path: Path) -> None:
    global global_project
    # setup filesystem
    for path in paths:
        tmp_inner_path = tmp_path / "project" / path
        tmp_inner_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_inner_path.write_text("helo)")

    global_project = Project(tmp_path / "project")
    global_project.build()


def test_project_structure(tmp_path: Path) -> None:
    paths_retrieved = [page.source_path.relative_to(global_project.root_path) for page in global_project.pages_stored]
    assert set(paths) == set(paths_retrieved)


def test_project_titles():
    titles = [
        "",
        "1.1. Welcome",
        "1.2. Semantic compositions on trolling and its meaning",
        "1.3. Welcome",
        "chapter 1",
        "bruh",
        "minions",
    ]

    titles_retrieved = [str(page.title) for page in global_project.pages_stored]
    assert set(titles) == set(titles_retrieved)


def test_project_toc():
    toc = [
        "",
        "chapter 1/1.1. Welcome",
        "chapter 1/1.2. Semantic compositions on trolling and its meaning",
        "chapter 1/1.3. Welcome",
        "chapter 1",
        "chapter 2/bruh",
        "chapter 2/part 1/paragraph 1/minions",
    ]

    toc_retrieved = [str(page.toc_path) for page in global_project.pages_stored]
    assert set(toc) == set(toc_retrieved)


def test_project_rebuild(tmp_path: Path) -> None:
    new_paths = [
        Path("chapter 1", "1.1. Welcome.html"),
        Path("chapter 1", "1.2. Semantic compositions on trolling and its meaning.html"),
    ]

    new_titles = [
        "1.1. Welcome",
        "1.2. Semantic compositions on trolling and its meaning",
    ]

    new_toc = [
        "chapter 1/1.1. Welcome",
        "chapter 1/1.2. Semantic compositions on trolling and its meaning",
    ]

    project_path = global_project.root_path
    shutil.rmtree(project_path, ignore_errors=True)

    for path in new_paths:
        tmp_inner_path = project_path / path
        tmp_inner_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_inner_path.write_text("q")

    global_project.build()

    paths_received = [page.source_path.relative_to(project_path) for page in global_project.pages_stored]
    titles_received = [str(page.title) for page in global_project.pages_stored]
    toc_received = [str(page.toc_path) for page in global_project.pages_stored]

    assert set(paths_received) == set(new_paths)
    assert set(titles_received) == set(new_titles)
    assert set(toc_received) == set(new_toc)
