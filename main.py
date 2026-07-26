from auditor.fetcher import fetch_page
from auditor.reporter import print_report
from auditor.runner import run_all_checks
from auditor.constants import (
    MAX_DESCRIPTION_LENGTH,
    MIN_DESCRIPTION_LENGTH,
)
from auditor.fetcher import fetch_page
from auditor.reporter import print_result


APP_NAME = "SEO Auditor"
VERSION = "0.1.0"

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

results = run_all_checks(soup)

print_report(results)