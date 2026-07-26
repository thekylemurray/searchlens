import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    """
    Downloads a webpage and returns useful objects for auditing.

    Returns:
        dict containing:
            response - requests Response object
            soup - BeautifulSoup object
            html - raw HTML
    """

    headers = {
        "User-Agent": (
            "SEO-Auditor/1.0 "
            "(https://github.com/thekylemurray)"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    return {
        "response": response,
        "soup": soup,
        "html": html,
    }

if __name__ == "__main__":

    page = fetch_page("https://example.com")

    print(page["response"].status_code)
    print(page["soup"].title.text)