from pathlib import Path

from faker import Faker

from crow.model import Page

fake = Faker()


def test_from_source_path():
    project_dir = Path("C:\\books\\crow-book")
    source_path = project_dir / "source" / "chapter 1" / "Does the suffering ever end or does it merely transform.html"

    page = Page.from_source_path(source_path, project_dir)
    assert page.title == "Does the suffering ever end or does it merely transform"
    assert (
        page.source_path.as_posix()
        == "C:/books/crow-book/source/chapter 1/Does the suffering ever end or does it merely transform.html"
    )
    assert page.toc_path == "source/chapter 1/Does the suffering ever end or does it merely transform"


# def test_toc_from_ordered_pages():
#     pages = [
#         fake_page(toc_path="", title=""),  # index doc
#         fake_page(toc_path="chapter 1", title="chapter 1"),  # some chapter description
#         fake_page(toc_path="chapter 1/Peter Griffin/lol", title="lol"),  # endpoint doc
#         fake_page(toc_path="when god decided to create", title="when god decided to create"),  # intermission
#         fake_page(toc_path="chapter 2/electric boogaloo/minions", title="minions"),
#     ]
#
#     toc = toc_from_ordered_pages(pages)
#
#     toc_expected = [
#         TOCEntry(indent=0, title=""),
#         TOCEntry(indent=1, title="chapter 1"),
#         TOCEntry(indent=3, title="lol"),
#         TOCEntry(indent=1, title="when god decided to create"),
#         TOCEntry(indent=3, title="minions"),
#     ]
#
#     assert toc_expected == toc
