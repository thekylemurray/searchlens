from bs4 import BeautifulSoup

from auditor.checks.headings import (
    check_heading_structure,
)


def build_soup(html: str) -> BeautifulSoup:
    """Build a BeautifulSoup document for a heading test."""

    return BeautifulSoup(html, "html.parser")


def test_valid_heading_structure_passes() -> None:
    soup = build_soup(
        """
        <h1>Main heading</h1>
        <h2>First section</h2>
        <h3>Subsection</h3>
        <h2>Second section</h2>
        """
    )

    result = check_heading_structure(soup)

    assert result.status == "pass"
    assert result.value["Counts"] == {
        "H1": 1,
        "H2": 2,
        "H3": 1,
    }
    assert result.value["Skipped Levels"] == []


def test_heading_level_jump_produces_warning() -> None:
    soup = build_soup(
        """
        <h1>Main heading</h1>
        <h3>Skipped H2</h3>
        """
    )

    result = check_heading_structure(soup)

    assert result.status == "warning"
    assert result.value["Skipped Levels"] == [
        "H1 → H3"
    ]


def test_multiple_heading_jumps_are_recorded() -> None:
    soup = build_soup(
        """
        <h1>Main heading</h1>
        <h3>First jump</h3>
        <h2>Section</h2>
        <h5>Second jump</h5>
        """
    )

    result = check_heading_structure(soup)

    assert result.status == "warning"
    assert result.value["Skipped Levels"] == [
        "H1 → H3",
        "H2 → H5",
    ]


def test_no_headings_produces_warning() -> None:
    soup = build_soup(
        """
        <main>
            <p>This page has no headings.</p>
        </main>
        """
    )

    result = check_heading_structure(soup)

    assert result.status == "warning"
    assert result.value["Counts"] == {}
    assert result.value["Heading Order"] == []


def test_heading_order_is_preserved() -> None:
    soup = build_soup(
        """
        <h1>Page title</h1>
        <h2>Alpha</h2>
        <h3>Beta</h3>
        <h2>Gamma</h2>
        """
    )

    result = check_heading_structure(soup)

    assert result.value["Heading Order"] == [
        {
            "Level": "H1",
            "Text": "Page title",
        },
        {
            "Level": "H2",
            "Text": "Alpha",
        },
        {
            "Level": "H3",
            "Text": "Beta",
        },
        {
            "Level": "H2",
            "Text": "Gamma",
        },
    ]


def test_heading_text_is_trimmed() -> None:
    soup = build_soup(
        """
        <h1>
            Main heading
        </h1>
        """
    )

    result = check_heading_structure(soup)

    assert result.value["Heading Order"][0] == {
        "Level": "H1",
        "Text": "Main heading",
    }