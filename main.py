from auditor.fetcher import fetch_page

APP_NAME = "SEO Auditor"
VERSION = "0.1.0"

MIN_TITLE_LENGTH = 30
MAX_TITLE_LENGTH = 60

MIN_DESCRIPTION_LENGTH = 70
MAX_DESCRIPTION_LENGTH = 160

def get_page_title(soup):
    if soup.title:
        return soup.title.get_text(strip=True)

    return "No title tag found"


def audit_title(title):
    if title == "No title tag found":
        return "FAIL: No title tag found"

    title_length = len(title)

    if title_length < MIN_TITLE_LENGTH:
        return f"WARNING: Title is too short ({title_length} characters)"

    if title_length > MAX_TITLE_LENGTH:
        return f"WARNING: Title is too long ({title_length} characters)"

    return f"PASS: Title length is good ({title_length} characters)"


def get_meta_description(soup):
    meta_tag = soup.find("meta", attrs={"name": "description"})

    if meta_tag:
        return meta_tag.get("content", "Description tag has no content")

    return "No description meta tag found"


def audit_meta_description(description):
    if description == "No description meta tag found":
        return "FAIL: No description meta tag found"

    description_length = len(description)

    if description_length < MIN_DESCRIPTION_LENGTH:
        return f"WARNING: Description is too short ({description_length} characters)"

    if description_length > MAX_DESCRIPTION_LENGTH:
        return f"WARNING: Description is too long ({description_length} characters)"

    return f"PASS: Description length is good ({description_length} characters)"


def get_h1_tags(soup):
    h1_tags = soup.find_all("h1")

    return [h1.get_text(strip=True) for h1 in h1_tags]


def get_canonical_url(soup):
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})

    if canonical_tag:
        return canonical_tag.get("href", "Canonical tag has no href")

    return "No canonical tag found"


def get_robots_directives(soup):
    robots_tag = soup.find("meta", attrs={"name": "robots"})

    if robots_tag:
        return robots_tag.get("content", "Robots tag has no content")

    return "No robots meta tag found"


def get_image_count(soup):
    return len(soup.find_all("img"))


def get_images_missing_alt(soup):
    img_tags = soup.find_all("img")
    missing_alt_images = []

    for img in img_tags:
        alt_text = img.get("alt")

        if alt_text is None or not alt_text.strip():
            missing_alt_images.append(
                img.get("src", "Image has no src attribute")
            )

    return missing_alt_images


print(f"{APP_NAME} {VERSION}")
print("Select your URL")
user_url = input(" ").strip()
print("You selected:", user_url)

if not user_url.startswith(("http://", "https://")):
    user_url = "https://" + user_url

page = fetch_page(user_url)

response = page["response"]
soup = page["soup"]
html = page["html"]

print(f"Status Code: {response.status_code}")

from auditor.checks.title import check_title

title_result = check_title(soup)

print(title_result.message)

meta_description = get_meta_description(soup)
print("Description:", meta_description)

meta_result = audit_meta_description(meta_description)
print("Description audit:", meta_result)

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

robots_directives = get_robots_directives(soup)
print("Robots directives:", robots_directives)

image_count = get_image_count(soup)
print(f"Image count: {image_count}")

missing_alt_images = get_images_missing_alt(soup)
if missing_alt_images:
    print("Images missing alt text:")
    for img in missing_alt_images:
        print("-", img)
    