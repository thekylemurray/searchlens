from bs4 import BeautifulSoup
import requests

def get_page_title(soup):
    if soup.title:
        return soup.title.get_text(strip=True)

    return "No title tag found"


def get_meta_description(soup):
    meta_tag = soup.find("meta", attrs={"name": "description"})

    if meta_tag:
        return meta_tag.get("content", "Description tag has no content")

    return "No description meta tag found"


def get_h1_tags(soup):
    h1_tags = soup.find_all("h1")

    return [h1.get_text(strip=True) for h1 in h1_tags]


def get_canonical_url(soup):
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})

    if canonical_tag:
        return canonical_tag.get("href", "Canonical tag has no href")

    return "No canonical tag found"

print("Select your URL")
user_url = input(" ").strip()
print("You selected:", user_url)

if not user_url.startswith(("http://", "https://")):
    user_url = "https://" + user_url

# Make the request
response = requests.get(user_url)

# Print the HTTP status code (e.g., 200 means success)
print(f"Status Code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

page_title = get_page_title(soup)
print("Page title:", page_title)

meta_description = get_meta_description(soup)
print("Description:", meta_description)

canonical_url = get_canonical_url(soup)
print("Canonical URL:", canonical_url)

h1_tags = get_h1_tags(soup)

if h1_tags:
    print(f"H1 count: {len(h1_tags)}")

    for h1 in h1_tags:
        print("-", h1)

    if len(h1_tags) > 1:
        print("Warning: Multiple H1 tags detected")
else:
    print("No H1 tags found")