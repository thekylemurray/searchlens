from dataclasses import dataclass

from bs4 import BeautifulSoup
from requests import Response


@dataclass(slots=True)
class PageContext:
    """Store the webpage data needed by SEO checks."""

    response: Response
    soup: BeautifulSoup
    html: str

    @property
    def url(self) -> str:
        """Return the final URL after redirects."""

        return self.response.url